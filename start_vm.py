#!/usr/bin/env python3
"""
start-vm: 1 step machine setups

Features:

- from a yaml 'recipe', it can generate
    - shell automated or step-by-step setup files
    - docker build files

Requires:
    - pyyaml
    - jinja2

"""

import abc
import argparse
import json
import logging
import os
import pathlib
import re
import stat
import subprocess
import sys
from datetime import datetime

import jinja2
import yaml

from typing import Optional, Any, Tuple

# Default log level - will be configured by CLI flag
LOG_FORMAT = "%(relativeCreated)-5d %(levelname)-5s: %(name)-15s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)


# Package version pinning utilities
class PackageSpec:
    """Represents a package specification with optional version constraints."""

    # Version specifier patterns for different package managers
    PATTERNS = {
        'python': re.compile(r'^([a-zA-Z0-9_\-\.]+)(==|>=|<=|>|<|~=|!=)?(.+)?$'),
        'debian': re.compile(r'^([a-zA-Z0-9_\-\.+]+)(=)?(.+)?$'),
        'ruby': re.compile(r'^([a-zA-Z0-9_\-\.]+)(:)?(.+)?$'),
        'rust': re.compile(r'^([a-zA-Z0-9_\-\.]+)(@)?(.+)?$'),
        'npm': re.compile(r'^([a-zA-Z0-9_\-\.@/]+)(@)?(.+)?$'),
        'winget': re.compile(r'^([a-zA-Z0-9_\-\.]+)(==)?(.+)?$'),
        'chocolatey': re.compile(r'^([a-zA-Z0-9_\-\.]+)(==)?(.+)?$'),
        'homebrew': re.compile(r'^([a-zA-Z0-9_\-\.@/]+)(@)?(.+)?$'),
    }

    def __init__(self, package_string: str, package_type: str = 'python'):
        self.original = package_string
        self.package_type = package_type
        self.name, self.operator, self.version = self._parse(package_string, package_type)

    def _parse(self, pkg_str: str, pkg_type: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse package string into name, operator, and version."""
        pattern = self.PATTERNS.get(pkg_type, self.PATTERNS['python'])
        match = pattern.match(pkg_str.strip())

        if not match:
            # No version specified, return as-is
            return pkg_str.strip(), None, None

        name = match.group(1)
        operator = match.group(2) if match.lastindex >= 2 else None
        version = match.group(3) if match.lastindex >= 3 else None

        return name, operator, version

    def has_version(self) -> bool:
        """Check if package has version constraint."""
        return self.version is not None

    def to_string(self, format: str = 'native') -> str:
        """Convert to package manager specific string format."""
        if not self.has_version():
            return self.name

        if format == 'python':
            return f"{self.name}{self.operator or '=='}{self.version}"
        elif format == 'debian':
            return f"{self.name}={self.version}" if self.version else self.name
        elif format == 'ruby':
            return f"{self.name}:{self.version}" if self.version else self.name
        elif format == 'rust':
            return f"{self.name}@{self.version}" if self.version else self.name
        elif format == 'npm':
            return f"{self.name}@{self.version}" if self.version else self.name
        elif format == 'winget':
            return f"{self.name} --version {self.version}" if self.version else self.name
        elif format == 'chocolatey':
            return f"{self.name} --version={self.version}" if self.version else self.name
        elif format == 'homebrew':
            return f"{self.name}@{self.version}" if self.version else self.name
        else:
            return self.original

    def to_lockfile_entry(self) -> dict:
        """Convert to lockfile entry format."""
        return {
            'name': self.name,
            'version': self.version,
            'operator': self.operator,
            'original': self.original,
        }

    def __repr__(self):
        return f"PackageSpec(name={self.name}, operator={self.operator}, version={self.version})"


class Builder(abc.ABC):
    """Abstract base class with standard interface / common functions"""

    prefix = ""
    suffix = ""
    template = ""
    setup = pathlib.Path("setup")
    filters = {
        "sequence": lambda val: ", ".join(repr(x) for x in val),
        "nosudo": lambda val: val.replace("sudo", " &&"),
        "junction": lambda val: "\n".join(
            " && " + line + " \\" for line in val.split("\n") if line
        ),
    }

    # Valid section types
    VALID_SECTION_TYPES = {
        'debian_packages', 'python_packages', 'ruby_packages',
        'rust_packages', 'rlang_packages', 'homebrew_packages', 'shell',
        'winget_packages', 'chocolatey_packages', 'powershell'
    }

    # Required recipe fields
    REQUIRED_RECIPE_FIELDS = {'name', 'platform', 'os', 'version', 'sections'}

    def __init__(self, recipe_yml: str, options: argparse.Namespace):
        self.recipe_yml = pathlib.Path(recipe_yml)
        # self.name = self.recipe_yml.stem
        self.options = options
        self.log = logging.getLogger(self.__class__.__name__)
        self.recipe = self._get_recipe()
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters.update(self.filters)

    def __repr__(self):
        return "<{} recipe='{}'>".format(self.__class__.__name__, self.recipe_yml)

    def _validate_recipe(self, recipe: dict, yml_file: pathlib.Path) -> None:
        """Validate recipe structure and required fields."""
        # Check required fields
        missing_fields = self.REQUIRED_RECIPE_FIELDS - recipe.keys()
        if missing_fields:
            self.log.error(f"Recipe {yml_file} is missing required fields: {missing_fields}")
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Validate sections exist and is a list
        if not isinstance(recipe.get('sections'), list):
            self.log.error(f"Recipe {yml_file} 'sections' must be a list")
            raise ValueError("'sections' must be a list")

        # Validate each section
        for idx, section in enumerate(recipe['sections']):
            if not isinstance(section, dict):
                self.log.error(f"Recipe {yml_file} section {idx} must be a dict")
                raise ValueError(f"Section {idx} must be a dict")

            # Check section has required fields
            if 'name' not in section:
                self.log.error(f"Recipe {yml_file} section {idx} missing 'name' field")
                raise ValueError(f"Section {idx} missing 'name' field")

            if 'type' not in section:
                self.log.error(f"Recipe {yml_file} section '{section.get('name', idx)}' missing 'type' field")
                raise ValueError(f"Section '{section.get('name', idx)}' missing 'type' field")

            # Validate section type
            section_type = section['type']
            if section_type not in self.VALID_SECTION_TYPES:
                self.log.error(
                    f"Recipe {yml_file} section '{section['name']}' has invalid type '{section_type}'. "
                    f"Valid types: {self.VALID_SECTION_TYPES}"
                )
                raise ValueError(f"Invalid section type '{section_type}'")

            # Check install field exists
            if 'install' not in section:
                self.log.error(f"Recipe {yml_file} section '{section['name']}' missing 'install' field")
                raise ValueError(f"Section '{section['name']}' missing 'install' field")

    def _load_recipe_from_file(self, name: Optional[str] = None) -> dict:
        """Returns default recipe or a named recipe."""
        yml_file = self.recipe_yml if not name else self.recipe_yml.parent / f"{name}.yml"

        try:
            with yml_file.open() as fopen:
                content = fopen.read()
                recipe = yaml.load(content, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            self.log.error(f"Recipe file not found: {yml_file}")
            raise
        except yaml.YAMLError as e:
            self.log.error(f"Invalid YAML in {yml_file}: {e}")
            raise
        except Exception as e:
            self.log.error(f"Error loading recipe from {yml_file}: {e}")
            raise

        # Validate recipe structure
        self._validate_recipe(recipe, yml_file)

        return recipe

    def _merge_configs(self, parent: dict, child: dict) -> dict:
        """
        Merge parent configuration into child with override rules.

        Override rules:
        - Child values always take precedence over parent values
        - For sections: child sections override parent sections by name
        - For other fields: child value replaces parent value if present
        - Special handling for 'inherits' field (not inherited)
        """
        # Configuration fields that can be inherited
        INHERITABLE_FIELDS = {
            'name', 'config', 'platform', 'os', 'version', 'release'
        }

        # Start with parent config
        merged = {}

        # Inherit all inheritable fields from parent
        for field in INHERITABLE_FIELDS:
            if field in parent:
                merged[field] = parent[field]

        # Override with child values (child takes precedence)
        for field in INHERITABLE_FIELDS:
            if field in child:
                merged[field] = child[field]

        # Handle sections inheritance (already exists, kept for clarity)
        merged['sections'] = child.get('sections', []).copy()
        child_section_names = [s['name'] for s in merged['sections']]

        if 'sections' in parent:
            for parent_section in parent['sections']:
                if parent_section['name'] not in child_section_names:
                    merged['sections'].append(parent_section)

        # Don't inherit the 'inherits' field itself
        if 'inherits' in child:
            merged['inherits'] = child['inherits']

        return merged

    def _get_recipe(self, recipe: Optional[dict[str,Any]] = None) -> dict:
        if not recipe:
            recipe = self._load_recipe_from_file()

        # Process inheritance with configuration inheritance
        if "inherits" in recipe:
            if isinstance(recipe["inherits"], str):
                parents = [recipe["inherits"]]
            else:
                parents = recipe["inherits"]

            # Process parents in order (left to right)
            # Later parents override earlier ones
            for parent_name in parents:
                parent_recipe = self._load_recipe_from_file(parent_name)

                # Recursively process parent's inheritance first
                if "inherits" in parent_recipe:
                    parent_recipe = self._get_recipe(parent_recipe)

                # Merge parent config into current recipe
                recipe = self._merge_configs(parent_recipe, recipe)

                self.log.debug(f"Inherited configuration from parent '{parent_name}'")

        # Handle default files
        default_path = pathlib.Path("default")
        if default_path.exists():
            recipe["defaults"] = os.listdir("default")
        else:
            self.log.warning(f"Default directory not found: {default_path}")
            recipe["defaults"] = []

        # Handle config files
        if recipe.get("config"):
            config_path = pathlib.Path("config") / recipe["config"]
            if config_path.exists():
                recipe["configs"] = os.listdir(str(config_path))
            else:
                self.log.warning(f"Config directory not found: {config_path}")
                recipe["configs"] = []
        else:
            recipe["configs"] = []

        recipe.update(vars(self.options))
        return recipe

    @property
    def target(self) -> str:
        """Output target property."""
        # return f"{self.prefix}_{self.name}{self.suffix}"
        return f"{self.prefix}{self.suffix}"

    def cmd(self, shell_cmd: str, *args, **kwds):
        """Executes a shell command with logging and easy formatting."""
        shell_cmd = shell_cmd.format(*args, **kwds)
        if self.options.dry_run:
            self.log.info(f"[DRY-RUN] Would execute: {shell_cmd}")
            return
        self.log.info(shell_cmd)
        if self.options.run:
            # Use subprocess.run with shell=True for compatibility with existing shell command strings
            # Note: shell=True is used here because generated scripts use shell syntax
            result = subprocess.run(shell_cmd, shell=True, capture_output=False)
            if result.returncode != 0:
                self.log.error(f"Command failed with exit code {result.returncode}: {shell_cmd}")

    def write_file(self, data: str):
        """Write setup file with options."""
        if self.options.strip:
            data = "\n".join(line for line in data.split("\n") if line.strip())
        path = self.setup / self.target

        # Ensure setup directory exists
        try:
            self.setup.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.log.error(f"Could not create setup directory {self.setup}: {e}")
            raise

        self.log.info("writing %s", path)
        try:
            with path.open("w") as fopen:
                fopen.write(data)
        except OSError as e:
            self.log.error(f"Could not write file {path}: {e}")
            raise

        if self.options.executable:
            try:
                flag = path.stat()
                path.chmod(flag.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except OSError as e:
                self.log.error(f"Could not make file executable {path}: {e}")
                raise

        if self.options.format:
            try:
                subprocess.run(['shfmt', '-w', str(path)], check=True, capture_output=True)
            except FileNotFoundError:
                self.log.warning(f"shfmt not found in PATH, skipping format for {path}")
            except subprocess.CalledProcessError as e:
                self.log.warning(f"Could not format {path}: {e.stderr.decode() if e.stderr else str(e)}")

    def run_section(self, name: str):
        """Run individual section from recipe."""
        # Validate that section exists
        matching_sections = [
            section for section in self.recipe["sections"] if section["name"] == name
        ]
        if not matching_sections:
            self.log.error(f"Section '{name}' not found in recipe")
            sys.exit(1)

        section = matching_sections[0]
        if section["type"] == "shell":
            shellcmd = "; ".join(section["install"].splitlines())
            if self.options.dry_run:
                self.log.info(f"[DRY-RUN] Would run section '{name}': {shellcmd}")
                return
            self.log.info(f"Running section '{name}': {shellcmd}")
            result = subprocess.run(shellcmd, shell=True)
            if result.returncode != 0:
                self.log.error(f"Section '{name}' failed with exit code {result.returncode}")
                sys.exit(result.returncode)
        else:
            self.log.error("Only sections of type 'shell' can be run currently.")
            sys.exit(1)

    def build(self):
        """Renders a template from a recipe."""
        try:
            template = self.env.get_template(self.template)
        except jinja2.TemplateNotFound:
            self.log.error(f"Template not found: {self.template}")
            raise
        except jinja2.TemplateSyntaxError as e:
            self.log.error(f"Template syntax error in {self.template}: {e}")
            raise

        try:
            rendered = template.render(**self.recipe)
        except jinja2.TemplateError as e:
            self.log.error(f"Error rendering template {self.template}: {e}")
            raise
        if not self.prefix:
            self.prefix = "_".join([
                self.recipe['platform'],
                self.recipe['os'],
                self.recipe['version'],
                self.recipe['name'],
            ])
            # self.prefix = "_".join(self.recipe["platform"].split(":"))

        if self.options.dry_run:
            self.log.info(f"[DRY-RUN] Would write {len(rendered)} bytes to {self.setup / self.target}")
            self.log.info(f"[DRY-RUN] Recipe contains {len(self.recipe['sections'])} sections")
            for section in self.recipe['sections']:
                self.log.info(f"[DRY-RUN]   - {section['name']} ({section['type']})")
        else:
            self.write_file(rendered)

    def generate_lockfile(self) -> str:
        """Generate lockfile with pinned package versions."""
        lockfile = {
            'generated_at': datetime.now().isoformat(),
            'recipe': {
                'name': self.recipe.get('name'),
                'platform': self.recipe.get('platform'),
                'os': self.recipe.get('os'),
                'version': self.recipe.get('version'),
                'release': self.recipe.get('release'),
            },
            'packages': {}
        }

        # Map section types to package manager formats
        type_to_format = {
            'python_packages': 'python',
            'debian_packages': 'debian',
            'ruby_packages': 'ruby',
            'rust_packages': 'rust',
            'homebrew_packages': 'homebrew',
            'winget_packages': 'winget',
            'chocolatey_packages': 'chocolatey',
        }

        for section in self.recipe.get('sections', []):
            section_type = section.get('type')
            section_name = section.get('name')

            if section_type not in type_to_format:
                continue

            pkg_format = type_to_format[section_type]
            packages_list = []

            if isinstance(section.get('install'), list):
                for pkg_str in section['install']:
                    pkg_spec = PackageSpec(pkg_str, pkg_format)
                    packages_list.append(pkg_spec.to_lockfile_entry())

            if packages_list:
                lockfile['packages'][section_name] = {
                    'type': section_type,
                    'packages': packages_list
                }

        return json.dumps(lockfile, indent=2)

    def write_lockfile(self):
        """Write lockfile to disk."""
        lockfile_content = self.generate_lockfile()
        lockfile_name = f"{self.prefix}.lock.json"
        lockfile_path = self.setup / lockfile_name

        self.log.info(f"Writing lockfile: {lockfile_path}")
        try:
            with lockfile_path.open("w") as f:
                f.write(lockfile_content)
        except OSError as e:
            self.log.error(f"Could not write lockfile {lockfile_path}: {e}")
            raise

    @abc.abstractmethod
    def run(self):
        "override me"


class ShellBuilder(Builder):
    """Builds a shell file for package installation."""

    suffix = ".sh"
    template = "shell.sh"

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("sh {}", path)


class DockerFileBuilder(Builder):
    """Builds a dockerfile for package installation."""

    prefix = ""
    suffix = ".Dockerfile"
    template = "Dockerfile"

    def run(self):
        self.log.info("docker build -t %s -f %s", self.name, self.target)


class PowerShellBuilder(Builder):
    """Builds a PowerShell script for Windows package installation."""

    suffix = ".ps1"
    template = "shell.ps1"

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("powershell -ExecutionPolicy Bypass -File {}", path)


class PythonBuilder(Builder):
    """Builds a Python script for cross-platform package installation."""

    suffix = ".py"
    template = "setup.py"

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("python3 {} install", path)


def commandline():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Install Packages")
    option = parser.add_argument

    option("recipe", nargs="+", help="recipes to install")
    option("-d", "--docker", action="store_true", help="generate dockerfile")
    option("-b", "--shell", action="store_true", help="generate shell file (Linux/macOS)")
    option("-p", "--powershell", action="store_true", help="generate PowerShell file (Windows)")
    option("-y", "--python", action="store_true", help="generate Python setup script (cross-platform)")
    option("-c", "--conditional", action="store_true", help="add conditional steps")
    option("-f", "--format", action="store_true", help="format using shfmt")
    option("-r", "--run", action="store_true", help="run generated file")
    option("-s", "--strip", default=False, action="store_true", help="strip empty lines")
    option("-e", "--executable", default=True, action="store_true", help="make setup file executable")
    option("--section", type=str, help="run section")
    option("--debug", action="store_true", help="enable debug logging")
    option("-n", "--dry-run", action="store_true", help="show commands without executing")
    option("--lockfile", action="store_true", help="generate lockfile with pinned versions")

    args = parser.parse_args()

    # Configure logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    for recipe in args.recipe:
        if args.section:
            builder = ShellBuilder(recipe, args)
            builder.run_section(args.section)

        if args.docker:
            builder = DockerFileBuilder(recipe, args)
            builder.build()

        if args.shell:
            builder = ShellBuilder(recipe, args)
            builder.build()

            if args.lockfile:
                builder.write_lockfile()

            if args.run:
                builder.run()

        if args.powershell:
            builder = PowerShellBuilder(recipe, args)
            builder.build()

            if args.lockfile:
                builder.write_lockfile()

            if args.run:
                builder.run()

        if args.python:
            builder = PythonBuilder(recipe, args)
            builder.build()

            if args.lockfile:
                builder.write_lockfile()

            if args.run:
                builder.run()

if __name__ == "__main__":
    commandline()
