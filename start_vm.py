#!/usr/bin/env python3
"""start-vm: 1 step machine setups"""

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
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import jinja2
import yaml

# Default log level - will be configured by CLI flag
LOG_FORMAT = "%(relativeCreated)-5d %(levelname)-5s: %(name)-15s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)


# Package version pinning utilities
class PackageSpec:
    """Represents a package specification with optional version constraints."""

    # Version specifier patterns for different package managers
    PATTERNS = {
        "python": re.compile(r"^([a-zA-Z0-9_\-\.]+)(==|>=|<=|>|<|~=|!=)?(.+)?$"),
        "debian": re.compile(r"^([a-zA-Z0-9_\-\.+]+)(=)?(.+)?$"),
        "ruby": re.compile(r"^([a-zA-Z0-9_\-\.]+)(:)?(.+)?$"),
        "rust": re.compile(r"^([a-zA-Z0-9_\-\.]+)(@)?(.+)?$"),
        "npm": re.compile(r"^([a-zA-Z0-9_\-\.@/]+)(@)?(.+)?$"),
        "winget": re.compile(r"^([a-zA-Z0-9_\-\.]+)(==)?(.+)?$"),
        "chocolatey": re.compile(r"^([a-zA-Z0-9_\-\.]+)(==)?(.+)?$"),
        "homebrew": re.compile(r"^([a-zA-Z0-9_\-\.@/]+)(@)?(.+)?$"),
    }

    def __init__(self, package_string: str, package_type: str = "python"):
        self.original = package_string
        self.package_type = package_type
        self.name, self.operator, self.version = self._parse(
            package_string, package_type
        )

    def _parse(
        self, pkg_str: str, pkg_type: str
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse package string into name, operator, and version."""
        pattern = self.PATTERNS.get(pkg_type, self.PATTERNS["python"])
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

    def to_string(self, format: str = "native") -> str:
        """Convert to package manager specific string format."""
        if not self.has_version():
            return self.name

        if format == "python":
            return f"{self.name}{self.operator or '=='}{self.version}"
        elif format == "debian":
            return f"{self.name}={self.version}" if self.version else self.name
        elif format == "ruby":
            return f"{self.name}:{self.version}" if self.version else self.name
        elif format == "rust":
            return f"{self.name}@{self.version}" if self.version else self.name
        elif format == "npm":
            return f"{self.name}@{self.version}" if self.version else self.name
        elif format == "winget":
            return (
                f"{self.name} --version {self.version}" if self.version else self.name
            )
        elif format == "chocolatey":
            return (
                f"{self.name} --version={self.version}" if self.version else self.name
            )
        elif format == "homebrew":
            return f"{self.name}@{self.version}" if self.version else self.name
        else:
            return self.original

    def to_lockfile_entry(self) -> dict:
        """Convert to lockfile entry format."""
        return {
            "name": self.name,
            "version": self.version,
            "operator": self.operator,
            "original": self.original,
        }

    def __repr__(self):
        return f"PackageSpec(name={self.name}, operator={self.operator}, version={self.version})"


class DotfilesValidator:
    """Validator for config/ and default/ directories."""

    def __init__(self, repo_root: pathlib.Path = None):
        self.repo_root = repo_root or pathlib.Path(__file__).parent
        self.recipes_dir = self.repo_root / "recipes"
        self.config_dir = self.repo_root / "config"
        self.default_dir = self.repo_root / "default"

        # Results
        self.recipes: Dict[str, dict] = {}
        self.config_refs: Dict[str, List[str]] = defaultdict(list)
        self.config_dirs: Set[str] = set()
        self.default_files: Set[str] = set()

    def load_recipes(self) -> None:
        """Load all recipe files and extract config references."""
        if not self.recipes_dir.exists():
            print(f"ERROR: Recipes directory not found: {self.recipes_dir}")
            sys.exit(1)

        for recipe_file in sorted(self.recipes_dir.glob("*.yml")):
            try:
                with open(recipe_file) as f:
                    data = yaml.safe_load(f)

                recipe_name = recipe_file.stem
                self.recipes[recipe_name] = data

                # Track config directory references
                if "config" in data and data["config"]:
                    config_name = data["config"]
                    self.config_refs[config_name].append(recipe_name)

            except Exception as e:
                print(f"WARNING: Failed to load {recipe_file.name}: {e}")

    def scan_config_dirs(self) -> None:
        """Scan config/ directory to find all subdirectories."""
        if not self.config_dir.exists():
            print(f"WARNING: Config directory not found: {self.config_dir}")
            return

        for item in self.config_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                self.config_dirs.add(item.name)

    def scan_default_files(self) -> None:
        """Scan default/ directory to find all files."""
        if not self.default_dir.exists():
            print(f"WARNING: Default directory not found: {self.default_dir}")
            return

        for item in self.default_dir.iterdir():
            if not item.name.startswith(".git"):
                self.default_files.add(item.name)

    def get_config_dir_stats(self, config_name: str) -> Dict:
        """Get statistics about a config directory."""
        config_path = self.config_dir / config_name
        if not config_path.exists():
            return {"exists": False}

        files = list(config_path.rglob("*"))
        file_list = [f for f in files if f.is_file()]

        if not file_list:
            return {
                "exists": True,
                "empty": True,
                "file_count": 0,
                "total_size": 0,
            }

        # Get modification times
        mod_times = [f.stat().st_mtime for f in file_list]
        oldest = min(mod_times)
        newest = max(mod_times)

        # Calculate total size
        total_size = sum(f.stat().st_size for f in file_list)

        return {
            "exists": True,
            "empty": False,
            "file_count": len(file_list),
            "total_size": total_size,
            "oldest_mod": datetime.fromtimestamp(oldest),
            "newest_mod": datetime.fromtimestamp(newest),
            "age_days": (datetime.now() - datetime.fromtimestamp(newest)).days,
        }

    def get_default_file_stats(self, file_name: str) -> Dict:
        """Get statistics about a default file or directory."""
        file_path = self.default_dir / file_name
        if not file_path.exists():
            return {"exists": False}

        stat = file_path.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime)

        result = {
            "exists": True,
            "is_dir": file_path.is_dir(),
            "size": stat.st_size,
            "modified": mod_time,
            "age_days": (datetime.now() - mod_time).days,
        }

        if file_path.is_dir():
            files = list(file_path.rglob("*"))
            file_list = [f for f in files if f.is_file()]
            result["file_count"] = len(file_list)
            result["total_size"] = sum(f.stat().st_size for f in file_list)

        return result

    def find_orphaned_config_dirs(self) -> List[Tuple[str, Dict]]:
        """Find config directories not referenced by any recipe."""
        orphaned = []
        for config_name in sorted(self.config_dirs):
            if config_name not in self.config_refs:
                stats = self.get_config_dir_stats(config_name)
                orphaned.append((config_name, stats))
        return orphaned

    def find_empty_config_dirs(self) -> List[str]:
        """Find config directories that exist but are empty or only have .keep files."""
        empty = []
        for config_name in sorted(self.config_dirs):
            config_path = self.config_dir / config_name
            files = [
                f for f in config_path.rglob("*") if f.is_file() and f.name != ".keep"
            ]
            if not files:
                empty.append(config_name)
        return empty

    def find_missing_config_dirs(self) -> List[Tuple[str, List[str]]]:
        """Find config directories referenced by recipes but don't exist."""
        missing = []
        for config_name, recipe_names in sorted(self.config_refs.items()):
            if config_name not in self.config_dirs:
                missing.append((config_name, recipe_names))
        return missing

    def analyze_config_age(self, max_age_days: int = 365) -> List[Tuple[str, Dict]]:
        """Find config directories that haven't been modified in a long time."""
        old_configs = []
        for config_name in sorted(self.config_dirs):
            stats = self.get_config_dir_stats(config_name)
            if stats.get("exists") and not stats.get("empty"):
                if stats["age_days"] > max_age_days:
                    old_configs.append((config_name, stats))
        return old_configs

    def analyze_default_age(self, max_age_days: int = 365) -> List[Tuple[str, Dict]]:
        """Find default files that haven't been modified in a long time."""
        old_files = []
        for file_name in sorted(self.default_files):
            stats = self.get_default_file_stats(file_name)
            if stats.get("exists"):
                if stats["age_days"] > max_age_days:
                    old_files.append((file_name, stats))
        return old_files

    def check_default_files_platform_specific(self) -> Dict[str, List[str]]:
        """Identify default files that may be platform-specific."""
        platform_indicators = {
            "linux": [".xinitrc", ".gtkrc", ".bashrc", "i3", "awesome"],
            "macos": [".bash_profile", "Brewfile"],
            "windows": [".ps1", "powershell"],
        }

        results = defaultdict(list)
        for file_name in sorted(self.default_files):
            for platform, indicators in platform_indicators.items():
                if any(ind in file_name.lower() for ind in indicators):
                    results[platform].append(file_name)
                    break
            else:
                results["cross-platform"].append(file_name)

        return results

    def generate_report(self, verbose: bool = False) -> str:
        """Generate a comprehensive validation report."""
        lines = []
        lines.append("=" * 80)
        lines.append("DOTFILES VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total recipes: {len(self.recipes)}")
        lines.append(f"Recipes with config field: {len(self.config_refs)}")
        lines.append(f"Config directories found: {len(self.config_dirs)}")
        lines.append(f"Default files/directories: {len(self.default_files)}")
        lines.append("")

        # Config directory usage
        lines.append("CONFIG DIRECTORY USAGE")
        lines.append("-" * 80)
        if self.config_refs:
            for config_name in sorted(self.config_refs.keys()):
                recipes = self.config_refs[config_name]
                exists = "✅" if config_name in self.config_dirs else "❌"
                lines.append(
                    f"{exists} config/{config_name}/ -> used by {len(recipes)} recipe(s): {', '.join(recipes)}"
                )

                if verbose and config_name in self.config_dirs:
                    stats = self.get_config_dir_stats(config_name)
                    if not stats.get("empty"):
                        lines.append(
                            f"     Files: {stats['file_count']}, "
                            f"Size: {stats['total_size']:,} bytes, "
                            f"Last modified: {stats['newest_mod'].strftime('%Y-%m-%d')} "
                            f"({stats['age_days']} days ago)"
                        )
        else:
            lines.append("No recipes reference config directories")
        lines.append("")

        # Orphaned config directories
        orphaned = self.find_orphaned_config_dirs()
        lines.append("ORPHANED CONFIG DIRECTORIES")
        lines.append("-" * 80)
        if orphaned:
            lines.append(
                "These config directories exist but are not referenced by any recipe:"
            )
            for config_name, stats in orphaned:
                if stats.get("empty"):
                    lines.append(f"⚠️  config/{config_name}/ (EMPTY - only .keep file)")
                else:
                    lines.append(
                        f"⚠️  config/{config_name}/ "
                        f"({stats['file_count']} files, "
                        f"{stats['total_size']:,} bytes, "
                        f"last modified {stats['age_days']} days ago)"
                    )
            lines.append("")
            lines.append(
                "RECOMMENDATION: Review these directories for removal or archive"
            )
        else:
            lines.append("✅ No orphaned config directories found")
        lines.append("")

        # Empty config directories
        empty = self.find_empty_config_dirs()
        lines.append("EMPTY CONFIG DIRECTORIES")
        lines.append("-" * 80)
        if empty:
            lines.append(
                "These config directories exist but are empty (only .keep files):"
            )
            for config_name in empty:
                used_by = self.config_refs.get(config_name, [])
                if used_by:
                    lines.append(
                        f"⚠️  config/{config_name}/ (referenced by: {', '.join(used_by)})"
                    )
                else:
                    lines.append(f"⚠️  config/{config_name}/ (not referenced)")
            lines.append("")
            lines.append("RECOMMENDATION: Remove empty directories or populate them")
        else:
            lines.append("✅ No empty config directories found")
        lines.append("")

        # Old config directories
        old_configs = self.analyze_config_age(max_age_days=365)
        lines.append("OLD CONFIG DIRECTORIES (>1 year since modification)")
        lines.append("-" * 80)
        if old_configs:
            for config_name, stats in old_configs:
                used_by = self.config_refs.get(config_name, ["not referenced"])
                lines.append(
                    f"📅 config/{config_name}/ - "
                    f"Last modified: {stats['newest_mod'].strftime('%Y-%m-%d')} "
                    f"({stats['age_days']} days ago) - "
                    f"Used by: {', '.join(used_by)}"
                )
            lines.append("")
            lines.append("RECOMMENDATION: Review for relevance to current OS versions")
        else:
            lines.append("✅ No old config directories found")
        lines.append("")

        # Default files analysis
        lines.append("DEFAULT FILES/DIRECTORIES")
        lines.append("-" * 80)
        platform_files = self.check_default_files_platform_specific()
        for platform in ["linux", "macos", "windows", "cross-platform"]:
            if platform in platform_files:
                lines.append(f"{platform.upper()}:")
                for file_name in platform_files[platform]:
                    stats = self.get_default_file_stats(file_name)
                    if stats.get("is_dir"):
                        lines.append(
                            f"  📁 {file_name}/ "
                            f"({stats.get('file_count', 0)} files, "
                            f"{stats.get('total_size', 0):,} bytes)"
                        )
                    else:
                        lines.append(f"  📄 {file_name} ({stats['size']:,} bytes)")
                lines.append("")
        lines.append("")

        # Old default files
        old_defaults = self.analyze_default_age(max_age_days=365)
        lines.append("OLD DEFAULT FILES (>1 year since modification)")
        lines.append("-" * 80)
        if old_defaults:
            for file_name, stats in old_defaults:
                lines.append(
                    f"📅 {file_name} - "
                    f"Last modified: {stats['modified'].strftime('%Y-%m-%d')} "
                    f"({stats['age_days']} days ago)"
                )
            lines.append("")
            lines.append("RECOMMENDATION: Review for relevance and update or remove")
        else:
            lines.append("✅ No old default files found")
        lines.append("")

        # Recommendations summary
        lines.append("CLEANUP RECOMMENDATIONS")
        lines.append("-" * 80)
        recommendations = []

        if orphaned:
            recommendations.append(
                f"1. Remove or archive {len(orphaned)} orphaned config director{'y' if len(orphaned) == 1 else 'ies'}"
            )
        if empty:
            recommendations.append(
                f"2. Remove {len(empty)} empty config director{'y' if len(empty) == 1 else 'ies'}"
            )
        if old_configs:
            recommendations.append(
                f"3. Review {len(old_configs)} config director{'y' if len(old_configs) == 1 else 'ies'} not modified in >1 year"
            )
        if old_defaults:
            recommendations.append(
                f"4. Review {len(old_defaults)} default file(s) not modified in >1 year"
            )

        if recommendations:
            for rec in recommendations:
                lines.append(rec)
        else:
            lines.append("✅ No cleanup needed - all dotfiles appear to be in use")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def run(self, verbose: bool = False) -> str:
        """Run the complete validation."""
        self.load_recipes()
        self.scan_config_dirs()
        self.scan_default_files()
        return self.generate_report(verbose=verbose)


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
        "debian_packages",
        "python_packages",
        "ruby_packages",
        "rust_packages",
        "rlang_packages",
        "homebrew_packages",
        "shell",
        "winget_packages",
        "chocolatey_packages",
        "powershell",
    }

    # Required recipe fields
    REQUIRED_RECIPE_FIELDS = {"name", "platform", "os", "version", "sections"}

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

    def _validate_recipe(self, recipe: dict, yml_file: pathlib.Path, skip_required: bool = False) -> None:
        """Validate recipe structure and required fields.

        Args:
            recipe: The recipe dictionary to validate
            yml_file: Path to the YAML file for error messages
            skip_required: If True, skip validation of required fields (for child recipes with inheritance)
        """
        # Check required fields (skip if this recipe has inheritance)
        if not skip_required:
            missing_fields = self.REQUIRED_RECIPE_FIELDS - recipe.keys()
            if missing_fields:
                self.log.error(
                    f"Recipe {yml_file} is missing required fields: {missing_fields}"
                )
                raise ValueError(f"Missing required fields: {missing_fields}")

        # Validate sections exist and is a list
        if not isinstance(recipe.get("sections"), list):
            self.log.error(f"Recipe {yml_file} 'sections' must be a list")
            raise ValueError("'sections' must be a list")

        # Validate each section
        for idx, section in enumerate(recipe["sections"]):
            if not isinstance(section, dict):
                self.log.error(f"Recipe {yml_file} section {idx} must be a dict")
                raise ValueError(f"Section {idx} must be a dict")

            # Check section has required fields
            if "name" not in section:
                self.log.error(f"Recipe {yml_file} section {idx} missing 'name' field")
                raise ValueError(f"Section {idx} missing 'name' field")

            if "type" not in section:
                self.log.error(
                    f"Recipe {yml_file} section '{section.get('name', idx)}' missing 'type' field"
                )
                raise ValueError(
                    f"Section '{section.get('name', idx)}' missing 'type' field"
                )

            # Validate section type
            section_type = section["type"]
            if section_type not in self.VALID_SECTION_TYPES:
                self.log.error(
                    f"Recipe {yml_file} section '{section['name']}' has invalid type '{section_type}'. "
                    f"Valid types: {self.VALID_SECTION_TYPES}"
                )
                raise ValueError(f"Invalid section type '{section_type}'")

            # Check install field exists
            if "install" not in section:
                self.log.error(
                    f"Recipe {yml_file} section '{section['name']}' missing 'install' field"
                )
                raise ValueError(f"Section '{section['name']}' missing 'install' field")

    def _load_recipe_from_file(self, name: Optional[str] = None) -> dict:
        """Returns default recipe or a named recipe."""
        yml_file = (
            self.recipe_yml if not name else self.recipe_yml.parent / f"{name}.yml"
        )

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
        # Skip required field validation if recipe has inheritance
        # (required fields will be validated after inheritance is resolved)
        skip_required = "inherits" in recipe
        self._validate_recipe(recipe, yml_file, skip_required=skip_required)

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
        INHERITABLE_FIELDS = {"name", "config", "platform", "os", "version", "release"}

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
        merged["sections"] = child.get("sections", []).copy()
        child_section_names = [s["name"] for s in merged["sections"]]

        if "sections" in parent:
            for parent_section in parent["sections"]:
                if parent_section["name"] not in child_section_names:
                    merged["sections"].append(parent_section)

        # Don't inherit the 'inherits' field itself
        if "inherits" in child:
            merged["inherits"] = child["inherits"]

        return merged

    def _get_recipe(self, recipe: Optional[dict[str, Any]] = None) -> dict:
        if not recipe:
            recipe = self._load_recipe_from_file()

        # Process inheritance with configuration inheritance
        if "inherits" in recipe:
            if isinstance(recipe["inherits"], str):
                parents = [recipe["inherits"]]
            else:
                parents = recipe["inherits"]

            # Build up merged parent config from all parents
            # Process parents in order (left to right), later parents override earlier ones
            merged_parent = {}
            for parent_name in parents:
                parent_recipe = self._load_recipe_from_file(parent_name)

                # Recursively process parent's inheritance first
                if "inherits" in parent_recipe:
                    parent_recipe = self._get_recipe(parent_recipe)

                # Merge this parent into the accumulated parent config
                # Treat parent_recipe as child so it overrides previous parents
                if merged_parent:
                    merged_parent = self._merge_configs(merged_parent, parent_recipe)
                else:
                    merged_parent = parent_recipe

                self.log.debug(f"Inherited configuration from parent '{parent_name}'")

            # Finally merge the accumulated parent config with the child
            recipe = self._merge_configs(merged_parent, recipe)

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

        # Validate the final merged recipe (after inheritance is complete)
        # Use a dummy path since we've already merged inheritance
        self._validate_recipe(recipe, pathlib.Path(self.recipe_yml), skip_required=False)

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
                self.log.error(
                    f"Command failed with exit code {result.returncode}: {shell_cmd}"
                )

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
                subprocess.run(
                    ["shfmt", "-w", str(path)], check=True, capture_output=True
                )
            except FileNotFoundError:
                self.log.warning(f"shfmt not found in PATH, skipping format for {path}")
            except subprocess.CalledProcessError as e:
                self.log.warning(
                    f"Could not format {path}: {e.stderr.decode() if e.stderr else str(e)}"
                )

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
                self.log.error(
                    f"Section '{name}' failed with exit code {result.returncode}"
                )
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
            self.prefix = "-".join(
                [
                    self.recipe["platform"],
                    self.recipe["os"],
                    self.recipe["version"],
                    self.recipe["name"],
                ]
            )
            # self.prefix = "-".join(self.recipe["platform"].split(":"))

        if self.options.dry_run:
            self.log.info(
                f"[DRY-RUN] Would write {len(rendered)} bytes to {self.setup / self.target}"
            )
            self.log.info(
                f"[DRY-RUN] Recipe contains {len(self.recipe['sections'])} sections"
            )
            for section in self.recipe["sections"]:
                self.log.info(f"[DRY-RUN]   - {section['name']} ({section['type']})")
        else:
            self.write_file(rendered)

    def generate_lockfile(self) -> str:
        """Generate lockfile with pinned package versions."""
        lockfile = {
            "generated_at": datetime.now().isoformat(),
            "recipe": {
                "name": self.recipe.get("name"),
                "platform": self.recipe.get("platform"),
                "os": self.recipe.get("os"),
                "version": self.recipe.get("version"),
                "release": self.recipe.get("release"),
            },
            "packages": {},
        }

        # Map section types to package manager formats
        type_to_format = {
            "python_packages": "python",
            "debian_packages": "debian",
            "ruby_packages": "ruby",
            "rust_packages": "rust",
            "homebrew_packages": "homebrew",
            "winget_packages": "winget",
            "chocolatey_packages": "chocolatey",
        }

        for section in self.recipe.get("sections", []):
            section_type = section.get("type")
            section_name = section.get("name")

            if section_type not in type_to_format:
                continue

            pkg_format = type_to_format[section_type]
            packages_list = []

            if isinstance(section.get("install"), list):
                for pkg_str in section["install"]:
                    pkg_spec = PackageSpec(pkg_str, pkg_format)
                    packages_list.append(pkg_spec.to_lockfile_entry())

            if packages_list:
                lockfile["packages"][section_name] = {
                    "type": section_type,
                    "packages": packages_list,
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
    """Builds a Python script with data-driven architecture."""

    suffix = ".py"
    template = "setup.py"

    def build(self):
        """Override build to construct data structures in Python."""
        import pprint

        # Construct FILE_SETS data structure
        file_sets = {
            'defaults': self.recipe.get('defaults', []),
            'configs': self.recipe.get('configs', []),
        }

        # Construct SECTIONS data structure
        sections = []
        for section in self.recipe.get('sections', []):
            sec_dict = {
                'name': section['name'],
                'type': section['type'],
            }

            if section.get('pre_install'):
                sec_dict['pre_install'] = section['pre_install']

            if section['type'] in ('shell', 'powershell'):
                sec_dict['install'] = section.get('install', '')
            else:
                sec_dict['install'] = section.get('install', [])

            if section.get('purge'):
                sec_dict['purge'] = section['purge']

            if section.get('post_install'):
                sec_dict['post_install'] = section['post_install']

            sections.append(sec_dict)

        # Pretty print the data structures
        file_sets_str = pprint.pformat(file_sets, indent=4, width=80)
        sections_str = pprint.pformat(sections, indent=4, width=80)

        # Add pretty-printed data to recipe context
        self.recipe['file_sets_data'] = file_sets_str
        self.recipe['sections_data'] = sections_str

        # Call parent build method
        super().build()

    def run(self):
        path = self.setup.joinpath(self.target)
        self.cmd("python3 {} install", path)


def commandline():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Install Packages")
    option = parser.add_argument

    # fmt: off
    option("recipe", nargs="*", help="recipes to install")
    option("-b", "--shell", action="store_true", help="generate shell file (Linux/macOS)")
    option("-c", "--conditional", action="store_true", help="add conditional steps")
    option("-d", "--docker", action="store_true", help="generate dockerfile")
    option("-dr", "--dry-run", action="store_true", help="show commands without executing")
    option("-e", "--executable", default=True, action="store_true", help="make setup file executable")
    option("-f", "--format", action="store_true", help="format using shfmt")
    option("-p", "--python", action="store_true", help="generate Python setup script (cross-platform)")
    option("-ps", "--powershell", action="store_true", help="generate PowerShell file (Windows)")
    option("-r", "--run", action="store_true", help="run generated file")
    option("-s", "--strip", default=False, action="store_true", help="strip empty lines")
    option("-v", "--verbose", action="store_true", help="verbose output (for --validate)")
    option("--debug", action="store_true", help="enable debug logging")
    option("--lockfile", action="store_true", help="generate lockfile with pinned versions")
    option("--section", type=str, help="run section")
    option("--validate", action="store_true", help="validate config/ and default/ directories")
    # fmt: on

    args = parser.parse_args()

    # Configure logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Handle validation mode (doesn't require recipes)
    if args.validate:
        validator = DotfilesValidator()
        report = validator.run(verbose=args.verbose)
        print(report)
        return

    # Check if recipes were provided for non-validate operations
    if not args.recipe:
        parser.error(
            "the following arguments are required: recipe (unless using --validate)"
        )

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
