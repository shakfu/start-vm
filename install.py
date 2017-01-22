#!/usr/bin/env python3

"""
installer: an installation support tool

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


# custom filters





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

    def _load_yml(self):
        recipe = None
        with self.recipe_yml.open() as f:
            content = f.read()
            recipe = yaml.load(content)
        return recipe

    def write_file(self, data):
        target = self.prefix + '_' + self.name + self.suffix
        path = self.setup.joinpath(target)
        self.log.info('writing {}', path)
        with path.open('w') as f:
            f.write(data)

    def cmd(self, shell_cmd, *args, **kwds):
        shell_cmd = shell_cmd.format(*args, **kwds)
        self.log.info(shell_cmd)
        if not self.options.test_run:
            os.system(shell_cmd)

    def do(self):
        """override me
        """


class PackageInstaller(Operator):
    """Install packages for multiple platforms

    """

    def do(self):
        for section in self.recipe['sections']:
            if 'install' in section:
                method = '_install_{}'.format(section['type'])
                try:
                    getattr(self, method)(section)
                except AttributeError:
                    traceback.print_exc(file=sys.stdout)

    def _install_debian_packages(self, section):
        installables = ' '.join(section['install'])
        self.cmd('sudo apt-get install {}'.format(installables))

    def _install_python_packages(self, section):
        installables = ' '.join(section['install'])
        self.cmd('sudo pip install {}'.format(installables))

    def _install_rlang_packages(self, section):
        installables = ', '.join(repr(e) for e in section['install'])
        self.cmd('sudo Rscript -e "install.packages({})"'.format(installables))

    def _install_ruby_packages(self, section):
        installables = ', '.join(repr(e) for e in section['install'])
        self.cmd('sudo gem install {}'.format(installables))


class Builder(Operator):
    def do(self):
        env = jinja2.Environment(trim_blocks=True)
        env.filters['sequence'] = lambda value: ', '.join(repr(x) for x in value)
        template = env.from_string(self.template)
        model = dict(
            installs = {section['type']: [] for section in self.recipe['sections']},
            cleanups = {section['type']: [] for section in self.recipe['sections']}
        )
        for section in self.recipe['sections']:
            if 'install' in section:
                model['installs'][section['type']].extend(section['install'])
            if 'cleanup' in section:
                model['cleanups'][section['type']].extend(section['cleanup'])
        #print(model)
        rendered = template.render(**model)
        if not self.prefix:
            self.prefix = '_'.join(self.recipe['platform'].split(':'))
        self.write_file(rendered)

class BashBuilder(Builder):
    """Builds a bash file for package installation
    """
    suffix = '.sh'
    template = dedent('''
    {% if installs.debian_packages %}
    sudo apt-get update && apt-get install -y \\
    {% for package in installs.debian_packages %}
        {{package}} \\
    {% endfor %}
     && echo "debian packages installed"

    {% endif %}
    {% if cleanups.debian_packages %}
    sudo apt-get purge -y \\
    {% for package in cleanups.debian_packages %}
        {{package}} \\
    {% endfor %}
     && echo "debian packages purged"
    {% endif %}

    {% if installs.python_packages %}
    sudo -H pip3 install \\
    {% for package in installs.python_packages %}
        {{package}} \\
    {% endfor %}
     && echo "python packages installed"
    {% endif %}

    {% if installs.ruby_packages %}
    sudo gem install \\
    {% for package in installs.ruby_packages %}
        {{package}} \\
    {% endfor %}
     && echo "ruby packages installed"
    {% endif %}

    {% if rlang_packages %}
    sudo Rscript -e "install.packages({{rlang_packages | sequence}})"
     && echo "rlang packages installed"
    {% endif %}
    ''')




class ConditionalBashBuilder(Builder):
    """Builds a bash file for package installation with conditional sections
    """
    prefix = 'cond-'
    template = dedent('''
    echo "Install debian packages?"
    echo "{{debian_packages}}"
    read -p "Are you sure? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
    {% if debian_packages %}
        sudo apt-get update && apt-get --no-install-recommends install -y \\
    {% for package in debian_packages %}
            {{package}} \\
    {% endfor %}
        && echo "debian packages installed"
    {% endif %}
    fi

    echo

    echo "Install python packages?"
    echo "{{python_packages}}"
    read -p "Are you sure? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
    {% if python_packages %}
        sudo -H pip install \\
    {% for package in python_packages %}
            {{package}} \\
    {% endfor %}
        && echo "python packages installed"
    {% endif %}
    fi

    echo "Install ruby packages?"
    echo "{{ruby_packages}}"
    read -p "Are you sure? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
    {% if ruby_packages %}
        sudo gem install \\
    {% for package in ruby_packages %}
            {{package}} \\
    {% endfor %}
        && echo "ruby packages installed"
    {% endif %}
    fi

''')


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
    parser.add_argument('--conditionalbashfile', '-c',
                        action='store_true', help='generate conditional bash file')
    parser.add_argument('--test-run', '-t',
                        action='store_true', help='test run')
    args = parser.parse_args()

    for recipe in args.recipe:
        if args.dockerfile:
            builder = DockerFileBuilder(recipe, args)
            builder.do()

        if args.bashfile:
            builder = BashBuilder(recipe, args)
            builder.do()

        if args.conditionalbashfile:
            builder = ConditionalBashBuilder(recipe, args)
            builder.do()

        # install
        installer = PackageInstaller(recipe, args)
        installer.do()

if __name__ == '__main__':
    commandline()
