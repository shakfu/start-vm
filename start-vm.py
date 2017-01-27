#!/usr/bin/env python3

"""
start-vm: 1 step machine initialization

features:

    - uses yaml files to generate
        - bash files
        - docker files

"""

import logging
import os
import pathlib
import stat
import sys
import traceback
from abc import ABC, abstractmethod

import jinja2
import yaml

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


class Builder(ABC):
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
        self.recipe['defaults'] = os.listdir('default')
        self.recipe['configs'] = os.listdir('config/{}'.format(self.name))
        self.recipe.update(vars(self.options))
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True)
        self.env.filters['sequence'] = lambda value: ', '.join(
            repr(x) for x in value)

    def __repr__(self):
        return "<{} recipe='{}'>".format(
            self.__class__.__name__, self.recipe_yml)

    def _load_yml(self):
        """loads the yaml recipe file
        """
        recipe = None
        with self.recipe_yml.open() as f:
            content = f.read()
            recipe = yaml.load(content)
        return recipe

    @property
    def target(self):
        return self.prefix + '_' + self.name + self.suffix

    def cmd(self, shell_cmd, *args, **kwds):
        """executes a shell command with logging and easy formatting
        """
        shell_cmd = shell_cmd.format(*args, **kwds)
        self.log.info(shell_cmd)
        if self.options.run:
            os.system(shell_cmd)

    def write_file(self, data):
        """write setup file with options
        """
        if self.options.strip:
            data = '\n'.join(
                [line for line in data.split('\n') if line.strip()])
        path = self.setup.joinpath(self.target)
        self.log.info('writing {}', path)
        with path.open('w') as f:
            f.write(data)
        if self.options.executable:
            st = path.stat()
            path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def build(self):
        """renders a template from a recipe
        """
        template = self.env.get_template(self.template)
        rendered = template.render(**self.recipe)
        if not self.prefix:
            self.prefix = '_'.join(self.recipe['platform'].split(':'))
        self.write_file(rendered)

    @abstractmethod
    def run(self):
        "override me"


class BashBuilder(Builder):
    """Builds a bash file for package installation
    """
    suffix = '.sh'
    template = 'bash.sh'

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("bash {}", path)


class DockerFileBuilder(Builder):
    """Builds a dockerfile for package installation
    """
    prefix = ''
    suffix = '.Dockerfile'
    template = 'Dockerfile'


def commandline():
    import argparse

    parser = argparse.ArgumentParser(description='Install Packages')
    
    parser.add_argument('recipe', nargs='+', help='recipes to install')
    parser.add_argument('--docker', '-d',
                        action='store_true', help='generate dockerfile')
    parser.add_argument('--bash', '-b',
                        action='store_true', help='generate bash file')
    parser.add_argument('--conditional', '-c',
                        action='store_true', help='add conditional steps')
    parser.add_argument('--run', '-r',
                        action='store_true', help='run bash file')
    parser.add_argument('--strip', '-s', default=False,
                        action='store_true', help='strip empty lines')
    parser.add_argument('--executable', '-e', default=True,
                        action='store_true', help='make setup file executable')
    args = parser.parse_args()

    for recipe in args.recipe:
        if args.docker:
            builder = DockerFileBuilder(recipe, args)
            builder.build()

        if args.bash:
            builder = BashBuilder(recipe, args)
            builder.build()

            if args.run:
                builder.run()


if __name__ == '__main__':
    commandline()
