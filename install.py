#!/usr/bin/env python3

"""
installer: an installation automation tool

features:

    - uses yaml files to generate
        - bash files
        - docker files

"""

import os
import sys
import traceback
import logging
import pathlib
from textwrap import dedent

import yaml
import jinja2


DEBUG = True

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = '%(relativeCreated)-5d %(levelname)-5s: %(name)-15s %(message)s'
logging.basicConfig(level=LOG_LEVEL,
                    format=LOG_FORMAT,
                    # filename=LOG_FILE,
                    stream=sys.stdout)


class Logger(object):
    """A logger class with color that can handle console and gui cases.
    """
    COLORS_LOG = {
        'debug':    'green',
        'info':     'cyan',
        'warn':     'yellow',
        'error':    'red',
        'critical': 'red',
    }

    ATTRIBUTES = dict(bold=1, underline=4)

    COLORS_TXT = dict(
        red=31,
        green=32,
        yellow=33,
        blue=34,
        magenta=35,
        cyan=36,
        white=37
    )
    RESET = '\033[0m'

    def __init__(self, name, is_colored=True, options=None):
        self.name = name
        self.log = logging.getLogger(name)
        self.is_colored = is_colored
        self.options = options

    def colored(self, text, color=None, attrs=None):
        """Colorize text.

        Available text colors:
            red, green, yellow, blue, magenta, cyan, white.

        Available attributes:
            bold, dark, underline, blink, reverse, concealed.

        Example:
            colored('Hello, World!', 'red', ['blue', 'blink'])
            colored('Hello, World!', 'green')

        """
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (self.COLORS_TXT[color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (self.ATTRIBUTES[attr], text)

            text += self.RESET
        return text

    @property
    def level(self):
        """Get logging level.
        """
        return logging.getLevelName(self.log.level)

    @level.setter
    def level(self, value):
        """Set logging level.
        """
        log_level = {
            'debug': logging.DEBUG,        # 10
            'info': logging.INFO,          # 20
            'warn': logging.WARN,          # 30
            'error': logging.ERROR,        # 40
            'critical': logging.CRITICAL,  # 50
        }
        if isinstance(value, str):
            assert value in log_level, 'level not implemented'
            self.log.parent.setLevel(log_level[value])
        elif isinstance(value, int):
            self.log.parent.setLevel(value)
        else:
            raise NotImplementedError

    def _dispatch(self, category, msg, *args, **kwargs):
        """Helper function for coloring log msg by type of msg.
        """
        msg = msg.format(*args, **kwargs)
        if self.is_colored:
            getattr(self.log, category)(
                self.colored(msg,
                             self.COLORS_LOG[category],
                             attrs=['bold']
                             )
            )
        else:
            getattr(self.log, category)

    def exception(self, msg, *args, **kwargs):
        """Log info msg.
        """
        self.log.exception(msg, *args, **kwargs)
        raise

    def info(self, msg, *args, **kwargs):
        """Log info msg.
        """
        self._dispatch('info', msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log debug msg.
        """
        self._dispatch('debug', msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """Log warn msg.
        """
        self._dispatch('warn', msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log error msg.
        """
        self._dispatch('error', msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log critical msg.
        """
        self._dispatch('critical', msg, *args, **kwargs)



class Operator:
    """Base class with standard interface and yaml loading to subclasses

    """
    prefix = ''
    suffix = ''
    setup = pathlib.Path('setup')

    def __init__(self, recipe_yml, options=None):
        self.recipe_yml = pathlib.Path(recipe_yml)
        self.name = self.recipe_yml.stem
        self.options = options
        self.recipe = self._load_yml()
        self.log = Logger(self.__class__.__name__)
        self.recipe['defaults'] = self._listdir('default')
        self.recipe['configs'] = self._listdir('config')

    def _load_yml(self):
        recipe = None
        with self.recipe_yml.open() as f:
            content = f.read()
            recipe = yaml.load(content)
        return recipe

    def _listdir(self, directory):
        entries = os.listdir(directory)
        return entries

    @property
    def target(self):
        return self.prefix + '_' + self.name + self.suffix

    def write_file(self, data, strip_empty_lines=True, is_executable=True):
        if strip_empty_lines:
            data = '\n'.join([line for line in data.split('\n') if line.strip()])
        path = self.setup.joinpath(self.target)
        self.log.info('writing {}', path)
        with path.open('w') as f:
            f.write(data)
        if is_executable:
            self.cmd('chmod +x {}', path)

    def cmd(self, shell_cmd, *args, **kwds):
        shell_cmd = shell_cmd.format(*args, **kwds)
        self.log.info(shell_cmd)
        if not self.options.test_run:
            os.system(shell_cmd)

    def run(self):
        "override me"

class Builder(Operator):
    def build(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.filters['sequence'] = lambda value: ', '.join(repr(x) for x in value)
        template = env.from_string(self.template)
        # print(vars(self.options))
        self.recipe.update(vars(self.options))
        # print(self.recipe)
        rendered = template.render(**self.recipe)
        if not self.prefix:
            self.prefix = '_'.join(self.recipe['platform'].split(':'))
        self.write_file(rendered)

class BashBuilder(Builder):
    """Builds a bash file for package installation
    """
    suffix = '.sh'
    template = dedent('''#!/usr/bin/env bash
    
    COLOR_BOLD_YELLOW="\033[1;33m"
    COLOR_BOLD_BLUE="\033[1;34m"
    COLOR_BOLD_MAGENTA="\033[1;35m"
    COLOR_BOLD_CYAN="\033[1;36m"
    COLOR_RESET="\033[m"

    CONFIG=config
    DEFAULT=default
    CONFIG_DST=$HOME/.config
    BIN=$HOME/bin

    function recipe {
        echo
        echo -e $COLOR_BOLD_MAGENTA$1 $COLOR_RESET
        echo "=========================================================="
    }

    function section {
        echo
        echo -e $COLOR_BOLD_CYAN$1 $COLOR_RESET
        echo "----------------------------------------------------------"
    }

    function install_default {
        echo "installing $1"
        cp -rf $DEFAULT/$1 $HOME/
    }

    function install_config {
        echo "installing $1"
        cp -rf $CONFIG/$1 $CONFIG_DST/
    }

    recipe "name: {{name}}"
    echo "platform: {{platform}}"
    echo

    section ">>> installing default dotfiles"
    {% for entry in defaults %}
    install_default {{entry}}
    {% endfor %}

    section ">>> installing .config folders"
    if [ ! -d "$CONFIG_DST" ]; then
        mkdir -p $CONFIG_DST
    fi
    {% for entry in configs %}
    install_config {{entry}}
    {% endfor %}

    {% for section in sections %}
    section ">>> {{section.name}}"

    {% if conditional %}
    echo "Install {{section.name}} {{section.type}}?"
    echo "{{section.install | join(', ')}}"
    read -p "Are you sure? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
    {% endif %}

    {% if section.pre_install %}
    echo "pre-install scripts"
    {{section.pre_install}}
    {% endif %}

    {% if section.type == "debian_packages" %}
    sudo apt-get update && sudo apt-get install -y \\
    {% for package in section.install %}
        {{package}} \\
    {% endfor %}
     && echo "{{section.name}} debian packages installed"
    {% endif %}

    {% if section.type == "python_packages" %}
    sudo -H pip3 install \\
    {% for package in section.install %}
        {{package}} \\
    {% endfor %}
     && echo "{{section.name}} python packages installed"
    {% endif %}

    {% if section.type == "ruby_packages" %}
    sudo gem install \\
    {% for package in section.install %}
        {{package}} \\
    {% endfor %}
     && echo "{{section.name}} ruby packages installed"
    {% endif %}

    {% if section.type == "rlang_packages" %}
    sudo Rscript -e "install.packages({{rlang_packages | sequence}})"
     && echo "rlang packages installed"
    {% endif %}

    {% if section.purge %}
    sudo apt-get purge -y \\
    {% for package in section.purge %}
        {{package}} \\
    {% endfor %}
     && echo "{{section.name}} packages purged"
    {% endif %}

    {% if section.post_install %}
    echo "post-install scripts"
    {{section.post_install}}
    {% endif %}

    {% if conditional %}
    fi
    {% endif %}
    {% endfor %}
    ''')

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("bash {}", path)

class DockerFileBuilder(Builder):
    """Builds a dockerfile for package installation
    """
    prefix = ''
    suffix = '.Dockerfile'
    template = dedent('''
    {% if debian_packages %}
    RUN apt-get update && apt-get --no-install-recommends install -y \\
    {% for package in debian_packages %}
        {{package}} \\
    {% endfor %}
     && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \\
    {% endif %}
    {% if python_packages %}
     && pip install \\
    {% for package in python_packages %}
        {{package}} \\
    {% endfor %}
     && rm -rf ${HOME}/.cache /tmp/*
    {% endif %}
    {% if ruby_packages %}
     && gem install \\
    {% for package in ruby_packages %}
        {{package}} \\
    {% endfor %}
     && rm -rf /tmp/*
    {% endif %}
    ''')


def commandline():
    import argparse

    parser = argparse.ArgumentParser(
        description='Install Packages'
    )
    parser.add_argument('recipe', nargs='+', help='recipes to install')
    parser.add_argument('--dockerfile', '-d',
                        action='store_true', help='generate dockerfile')
    parser.add_argument('--bashfile', '-b',
                        action='store_true', help='generate bash file')
    parser.add_argument('--conditional', '-c',
                        action='store_true', help='add conditional steps')
    parser.add_argument('--run', '-r',
                        action='store_true', help='run bash file')
    args = parser.parse_args()

    for recipe in args.recipe:
        if args.dockerfile:
            builder = DockerFileBuilder(recipe, args)
            builder.build()

        if args.bashfile:
            builder = BashBuilder(recipe, args)
            builder.build()

            if args.run:
                builder.run()


if __name__ == '__main__':
    commandline()
