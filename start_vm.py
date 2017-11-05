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
from abc import ABC, abstractmethod

import jinja2
import yaml

DEBUG = True

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = '%(relativeCreated)-5d %(levelname)-5s: %(name)-15s %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)


class Builder(ABC):
    """Abstract base class with standard interface / common functions
    """
    prefix = ''
    suffix = ''
    template = ''
    setup = pathlib.Path('setup')
    filters = {
        'sequence': lambda val: ', '.join(repr(x) for x in val),
        'nosudo': lambda val: val.replace('sudo', ' &&'),
        'junction': lambda val: '\n'.join(
            ' && ' + line + ' \\' for line in val.split('\n') if line),
    }

    def __init__(self, recipe_yml, options=None):
        self.recipe_yml = pathlib.Path(recipe_yml)
        self.name = self.recipe_yml.stem
        self.options = options
        self.recipe = self._load_yml()
        self.log = logging.getLogger(self.__class__.__name__)
        self.recipe['defaults'] = os.listdir('default')
        self.recipe['configs'] = os.listdir('config/{}'.format(
            self.recipe['config']))
        self.recipe.update(vars(self.options))
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True)
        self.env.filters.update(self.filters)

    def __repr__(self):
        return "<{} recipe='{}'>".format(self.__class__.__name__,
                                         self.recipe_yml)

    def _load_yml(self):
        """Loads the yaml recipe file."""
        recipe = None
        with self.recipe_yml.open() as fopen:
            content = fopen.read()
            recipe = yaml.load(content)
        return recipe

    @property
    def target(self):
        """Output target property."""
        return self.prefix + '_' + self.name + self.suffix

    def cmd(self, shell_cmd, *args, **kwds):
        """Executes a shell command with logging and easy formatting."""
        shell_cmd = shell_cmd.format(*args, **kwds)
        self.log.info(shell_cmd)
        if self.options.run:
            os.system(shell_cmd)

    def write_file(self, data):
        """Write setup file with options."""
        if self.options.strip:
            data = '\n'.join(
                [line for line in data.split('\n') if line.strip()])
        path = self.setup / self.target
        self.log.info('writing %s', path)
        with path.open('w') as fopen:
            fopen.write(data)
        if self.options.executable:
            flag = path.stat()
            path.chmod(flag.st_mode | stat.S_IXUSR | stat.S_IXGRP |
                       stat.S_IXOTH)

    def build(self):
        """Renders a template from a recipe."""
        template = self.env.get_template(self.template)
        rendered = template.render(**self.recipe)
        if not self.prefix:
            self.prefix = '_'.join(self.recipe['platform'].split(':'))
        self.write_file(rendered)

    @abstractmethod
    def run(self):
        "override me"


class BashBuilder(Builder):
    """Builds a bash file for package installation."""
    suffix = '.sh'
    template = 'bash.sh'

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("bash {}", path)


class DockerFileBuilder(Builder):
    """Builds a dockerfile for package installation."""
    prefix = ''
    suffix = '.Dockerfile'
    template = 'Dockerfile'

    def run(self):
        self.log("docker build -t %s -f %s", self.name, self.target)


def commandline():
    """Command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description='Install Packages')

    parser.add_argument('recipe', nargs='+', help='recipes to install')
    parser.add_argument(
        '--docker', '-d', action='store_true', help='generate dockerfile')
    parser.add_argument(
        '--bash', '-b', action='store_true', help='generate bash file')
    parser.add_argument(
        '--conditional',
        '-c',
        action='store_true',
        help='add conditional steps')
    parser.add_argument(
        '--run', '-r', action='store_true', help='run bash file')
    parser.add_argument(
        '--strip',
        '-s',
        default=False,
        action='store_true',
        help='strip empty lines')
    parser.add_argument(
        '--executable',
        '-e',
        default=True,
        action='store_true',
        help='make setup file executable')
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
