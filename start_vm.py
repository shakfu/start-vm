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
        'sequence':
        lambda val: ', '.join(repr(x) for x in val),
        'nosudo':
        lambda val: val.replace('sudo', ' &&'),
        'junction':
        lambda val: '\n'.join(' && ' + line + ' \\' for line in val.split('\n')
                              if line),
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
            recipe = yaml.load(content, Loader=yaml.SafeLoader)
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
            path.chmod(flag.st_mode | stat.S_IXUSR | stat.S_IXGRP
                       | stat.S_IXOTH)

    def run_section(self, name):
        """Run individual section from recipy."""
        section = [
            section for section in self.recipe['sections']
            if section['name'] == name
        ][0]
        if section['type'] == 'bash':
            shellcmd = "; ".join(section['install'].splitlines())
            os.system(shellcmd)
        else:
            print("Only sections of type 'bash' can be run currently.")

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
    option = parser.add_argument

    option('recipe', nargs='+', help='recipes to install')
    option('--docker', '-d', action='store_true', help='generate dockerfile')
    option('--bash', '-b', action='store_true', help='generate bash file')
    option('--conditional',
           '-c',
           action='store_true',
           help='add conditional steps')
    option('--run', '-r', action='store_true', help='run bash file')
    option('--strip',
           '-s',
           default=False,
           action='store_true',
           help='strip empty lines')
    option('--executable',
           '-e',
           default=True,
           action='store_true',
           help='make setup file executable')
    option('--section', type=str, help='run section')
    args = parser.parse_args()

    for recipe in args.recipe:
        if args.section:
            builder = BashBuilder(recipe, args)
            builder.run_section(args.section)

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
