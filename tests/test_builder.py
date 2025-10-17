#!/usr/bin/env python3
"""
Test suite for start_vm.py Builder classes

Run with: pytest tests/test_builder.py
"""

import argparse
import json
import pathlib
import tempfile
import sys
from unittest import mock

import pytest
import yaml

# Add parent directory to path to import start_vm
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from start_vm import Builder, ShellBuilder, DockerFileBuilder, PythonBuilder


@pytest.fixture
def mock_options():
    """Create mock options for Builder initialization."""
    options = argparse.Namespace(
        run=False,
        dry_run=False,
        strip=False,
        executable=True,
        format=False,
        conditional=False,
        debug=False,
    )
    return options


@pytest.fixture
def temp_recipe_dir(tmp_path):
    """Create temporary directory structure with recipes and templates."""
    # Create directory structure
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir()
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    setup_dir = tmp_path / "setup"
    setup_dir.mkdir()
    default_dir = tmp_path / "default"
    default_dir.mkdir()
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create a simple recipe
    recipe = {
        "name": "test",
        "platform": "linux",
        "os": "ubuntu",
        "version": "20.04",
        "release": "focal",
        "config": None,
        "sections": [
            {
                "name": "core",
                "type": "debian_packages",
                "install": ["vim", "git"],
            }
        ],
    }
    recipe_path = recipes_dir / "test.yml"
    with recipe_path.open("w") as f:
        yaml.dump(recipe, f)

    # Create a simple template
    template_content = """#!/usr/bin/env bash
echo "{{name}}"
"""
    (templates_dir / "shell.sh").write_text(template_content)
    (templates_dir / "Dockerfile").write_text("FROM ubuntu:{{version}}\n")

    return tmp_path, recipe_path


class TestBuilderValidation:
    """Test recipe validation functionality."""

    def test_validate_missing_required_fields(self, mock_options, tmp_path):
        """Test that validation catches missing required fields."""
        recipe_path = tmp_path / "invalid.yml"
        recipe = {"name": "test"}  # Missing required fields
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with pytest.raises(ValueError, match="Missing required fields"):
            builder = ShellBuilder(str(recipe_path), mock_options)

    def test_validate_invalid_section_type(self, mock_options, tmp_path):
        """Test that validation catches invalid section types."""
        recipe_path = tmp_path / "invalid.yml"
        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "sections": [
                {
                    "name": "bad",
                    "type": "invalid_type",
                    "install": ["something"],
                }
            ],
        }
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with pytest.raises(ValueError, match="Invalid section type"):
            builder = ShellBuilder(str(recipe_path), mock_options)

    def test_validate_section_missing_name(self, mock_options, tmp_path):
        """Test that validation catches sections missing name field."""
        recipe_path = tmp_path / "invalid.yml"
        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "sections": [
                {
                    "type": "debian_packages",
                    "install": ["vim"],
                }
            ],
        }
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with pytest.raises(ValueError, match="missing 'name' field"):
            builder = ShellBuilder(str(recipe_path), mock_options)

    def test_validate_section_missing_install(self, mock_options, tmp_path):
        """Test that validation catches sections missing install field."""
        recipe_path = tmp_path / "invalid.yml"
        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "sections": [
                {
                    "name": "core",
                    "type": "debian_packages",
                }
            ],
        }
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with pytest.raises(ValueError, match="missing 'install' field"):
            builder = ShellBuilder(str(recipe_path), mock_options)


class TestBuilderRecipeLoading:
    """Test recipe loading and inheritance."""

    def test_load_simple_recipe(self, mock_options, temp_recipe_dir):
        """Test loading a simple recipe."""
        tmp_path, recipe_path = temp_recipe_dir

        # Change to temp directory for relative paths
        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)

        assert builder.recipe["name"] == "test"
        assert builder.recipe["platform"] == "linux"
        assert len(builder.recipe["sections"]) == 1

    def test_load_recipe_with_inheritance(self, mock_options, tmp_path):
        """Test recipe inheritance functionality."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create parent recipe
        parent = {
            "name": "parent",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]},
                {"name": "python", "type": "python_packages", "install": ["pytest"]},
            ],
        }
        (recipes_dir / "parent.yml").write_text(yaml.dump(parent))

        # Create child recipe that inherits and overrides
        child = {
            "name": "child",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "inherits": "parent",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["emacs"]},
            ],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # Should have 2 sections: overridden core + inherited python
        assert len(builder.recipe["sections"]) == 2
        section_names = [s["name"] for s in builder.recipe["sections"]]
        assert "core" in section_names
        assert "python" in section_names

        # Core should be from child (emacs), not parent (vim)
        core_section = next(s for s in builder.recipe["sections"] if s["name"] == "core")
        assert "emacs" in core_section["install"]


class TestBuilderTemplateRendering:
    """Test template rendering functionality."""

    def test_shell_builder_rendering(self, mock_options, temp_recipe_dir):
        """Test ShellBuilder renders templates correctly."""
        tmp_path, recipe_path = temp_recipe_dir

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)
                builder.setup = tmp_path / "setup"

                with mock.patch.object(builder, "write_file") as mock_write:
                    builder.build()

                mock_write.assert_called_once()
                rendered = mock_write.call_args[0][0]
                assert "test" in rendered

    def test_docker_builder_rendering(self, mock_options, temp_recipe_dir):
        """Test DockerFileBuilder renders templates correctly."""
        tmp_path, recipe_path = temp_recipe_dir

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = DockerFileBuilder(str(recipe_path), mock_options)
                builder.setup = tmp_path / "setup"

                with mock.patch.object(builder, "write_file") as mock_write:
                    builder.build()

                mock_write.assert_called_once()
                rendered = mock_write.call_args[0][0]
                # Check that the template rendered section content correctly
                assert "section: core" in rendered
                assert "apt-get" in rendered


class TestBuilderDryRun:
    """Test dry-run functionality."""

    def test_dry_run_no_file_creation(self, mock_options, temp_recipe_dir):
        """Test that dry-run doesn't create files."""
        tmp_path, recipe_path = temp_recipe_dir
        mock_options.dry_run = True

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)
                builder.setup = tmp_path / "setup"
                builder.build()

        # Check that no files were written
        setup_files = list((tmp_path / "setup").glob("*"))
        assert len(setup_files) == 0

    def test_dry_run_logging(self, mock_options, temp_recipe_dir, caplog):
        """Test that dry-run logs what would be done."""
        import logging
        caplog.set_level(logging.INFO, logger="ShellBuilder")

        tmp_path, recipe_path = temp_recipe_dir
        mock_options.dry_run = True

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)
                builder.setup = tmp_path / "setup"
                builder.build()

        assert "[DRY-RUN]" in caplog.text


class TestBuilderFilters:
    """Test custom Jinja2 filters."""

    def test_sequence_filter(self):
        """Test the sequence filter for R packages."""
        from start_vm import Builder

        filter_func = Builder.filters["sequence"]
        result = filter_func(["pkg1", "pkg2", "pkg3"])
        assert result == "'pkg1', 'pkg2', 'pkg3'"

    def test_nosudo_filter(self):
        """Test the nosudo filter for Docker."""
        from start_vm import Builder

        filter_func = Builder.filters["nosudo"]
        result = filter_func("sudo apt-get update")
        assert "sudo" not in result
        assert "&&" in result


class TestBuilderErrorHandling:
    """Test error handling."""

    def test_file_not_found_error(self, mock_options):
        """Test error handling for non-existent recipe file."""
        with pytest.raises(FileNotFoundError):
            builder = ShellBuilder("/nonexistent/recipe.yml", mock_options)

    def test_invalid_yaml_error(self, mock_options, tmp_path):
        """Test error handling for invalid YAML."""
        recipe_path = tmp_path / "invalid.yml"
        recipe_path.write_text("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            builder = ShellBuilder(str(recipe_path), mock_options)

    def test_missing_section_in_run_section(self, mock_options, temp_recipe_dir):
        """Test error handling for missing section."""
        tmp_path, recipe_path = temp_recipe_dir

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)

                with pytest.raises(SystemExit):
                    builder.run_section("nonexistent")


class TestBuilderConfigHandling:
    """Test config directory handling."""

    def test_missing_default_directory(self, mock_options, temp_recipe_dir, caplog):
        """Test handling of missing default directory."""
        import logging
        import os
        caplog.set_level(logging.WARNING, logger="ShellBuilder")

        tmp_path, recipe_path = temp_recipe_dir

        # Remove default directory
        (tmp_path / "default").rmdir()

        # Change to tmp_path directory so pathlib.Path("default") resolves correctly
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            builder = ShellBuilder(str(recipe_path), mock_options)
        finally:
            os.chdir(orig_cwd)

        assert "Default directory not found" in caplog.text
        assert builder.recipe["defaults"] == []

    def test_missing_config_directory(self, mock_options, tmp_path, caplog):
        """Test handling of missing config directory."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "config": "nonexistent",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        recipe_path = recipes_dir / "test.yml"
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", side_effect=[[], FileNotFoundError()]):
                builder = ShellBuilder(str(recipe_path), mock_options)

        assert "Config directory not found" in caplog.text
        assert builder.recipe["configs"] == []


class TestConfigurationInheritance:
    """Test configuration field inheritance functionality."""

    def test_inherit_all_config_fields(self, mock_options, tmp_path):
        """Test that child inherits all config fields from parent."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create parent recipe with full configuration
        parent = {
            "name": "parent",
            "config": "parent_config",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "release": "focal",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        (recipes_dir / "parent.yml").write_text(yaml.dump(parent))

        # Create child with minimal config (only inherits field)
        child = {
            "inherits": "parent",
            "sections": [],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # Child should inherit all config fields from parent
        assert builder.recipe["name"] == "parent"
        assert builder.recipe["config"] == "parent_config"
        assert builder.recipe["platform"] == "linux"
        assert builder.recipe["os"] == "ubuntu"
        assert builder.recipe["version"] == "20.04"
        assert builder.recipe["release"] == "focal"

    def test_child_overrides_parent_config(self, mock_options, tmp_path):
        """Test that child config values override parent values."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create parent recipe
        parent = {
            "name": "parent",
            "config": "parent_config",
            "platform": "linux",
            "os": "debian",
            "version": "11",
            "release": "bullseye",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        (recipes_dir / "parent.yml").write_text(yaml.dump(parent))

        # Create child that overrides some fields
        child = {
            "inherits": "parent",
            "name": "child",
            "version": "12",
            "release": "bookworm",
            "sections": [],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # Child values should override parent
        assert builder.recipe["name"] == "child"
        assert builder.recipe["version"] == "12"
        assert builder.recipe["release"] == "bookworm"
        # Parent values should be inherited where not overridden
        assert builder.recipe["config"] == "parent_config"
        assert builder.recipe["platform"] == "linux"
        assert builder.recipe["os"] == "debian"

    def test_multiple_inheritance_config_precedence(self, mock_options, tmp_path):
        """Test config inheritance with multiple parents (later overrides earlier)."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create first parent
        parent1 = {
            "name": "parent1",
            "config": "config1",
            "platform": "linux",
            "os": "ubuntu",
            "version": "20.04",
            "release": "focal",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        (recipes_dir / "parent1.yml").write_text(yaml.dump(parent1))

        # Create second parent with different values
        parent2 = {
            "name": "parent2",
            "config": "config2",
            "platform": "linux",
            "os": "debian",
            "version": "11",
            "release": "bullseye",
            "sections": [
                {"name": "python", "type": "python_packages", "install": ["pytest"]}
            ],
        }
        (recipes_dir / "parent2.yml").write_text(yaml.dump(parent2))

        # Create child inheriting from both
        child = {
            "inherits": ["parent1", "parent2"],
            "name": "child",
            "sections": [],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # Later parent (parent2) should override earlier (parent1)
        assert builder.recipe["name"] == "child"  # Child overrides both
        assert builder.recipe["config"] == "config2"  # From parent2
        assert builder.recipe["os"] == "debian"  # From parent2
        assert builder.recipe["version"] == "11"  # From parent2
        assert builder.recipe["release"] == "bullseye"  # From parent2
        assert builder.recipe["platform"] == "linux"  # Same in both
        # Should have sections from both parents
        assert len(builder.recipe["sections"]) == 2

    def test_nested_inheritance_config(self, mock_options, tmp_path):
        """Test configuration inheritance with nested hierarchy (grandparent->parent->child)."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create grandparent
        grandparent = {
            "name": "grandparent",
            "config": "base_config",
            "platform": "linux",
            "os": "debian",
            "version": "10",
            "release": "buster",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        (recipes_dir / "grandparent.yml").write_text(yaml.dump(grandparent))

        # Create parent inheriting from grandparent
        parent = {
            "inherits": "grandparent",
            "name": "parent",
            "version": "11",
            "release": "bullseye",
            "sections": [
                {"name": "python", "type": "python_packages", "install": ["pytest"]}
            ],
        }
        (recipes_dir / "parent.yml").write_text(yaml.dump(parent))

        # Create child inheriting from parent
        child = {
            "inherits": "parent",
            "name": "child",
            "config": "child_config",
            "sections": [],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # Should have config from all levels with proper precedence
        assert builder.recipe["name"] == "child"  # From child
        assert builder.recipe["config"] == "child_config"  # From child
        assert builder.recipe["version"] == "11"  # From parent
        assert builder.recipe["release"] == "bullseye"  # From parent
        assert builder.recipe["platform"] == "linux"  # From grandparent
        assert builder.recipe["os"] == "debian"  # From grandparent
        # Should have sections from all levels
        assert len(builder.recipe["sections"]) == 2

    def test_minimal_child_recipe(self, mock_options, tmp_path):
        """Test that child can be minimal with just inherits and sections."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        # Create comprehensive parent
        parent = {
            "name": "ubuntu-base",
            "config": "ubuntu",
            "platform": "linux",
            "os": "ubuntu",
            "version": "22.04",
            "release": "jammy",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim", "git"]},
                {"name": "python", "type": "python_packages", "install": ["pytest"]},
            ],
        }
        (recipes_dir / "parent.yml").write_text(yaml.dump(parent))

        # Create minimal child that just adds one section
        child = {
            "inherits": "parent",
            "sections": [
                {"name": "extra", "type": "debian_packages", "install": ["htop"]}
            ],
        }
        child_path = recipes_dir / "child.yml"
        child_path.write_text(yaml.dump(child))

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(child_path), mock_options)

        # All parent config should be inherited
        assert builder.recipe["name"] == "ubuntu-base"
        assert builder.recipe["config"] == "ubuntu"
        assert builder.recipe["platform"] == "linux"
        assert builder.recipe["os"] == "ubuntu"
        assert builder.recipe["version"] == "22.04"
        assert builder.recipe["release"] == "jammy"
        # Should have sections from both
        assert len(builder.recipe["sections"]) == 3
        section_names = [s["name"] for s in builder.recipe["sections"]]
        assert "extra" in section_names
        assert "core" in section_names
        assert "python" in section_names


class TestPackageVersionPinning:
    """Test package version pinning functionality."""

    def test_package_spec_python_equal(self):
        """Test parsing Python package with == operator."""
        from start_vm import PackageSpec

        pkg = PackageSpec("requests==2.28.1", "python")
        assert pkg.name == "requests"
        assert pkg.operator == "=="
        assert pkg.version == "2.28.1"
        assert pkg.has_version()
        assert pkg.to_string("python") == "requests==2.28.1"

    def test_package_spec_python_operators(self):
        """Test parsing Python packages with various operators."""
        from start_vm import PackageSpec

        specs = {
            "django>=4.0": ("django", ">=", "4.0"),
            "flask<=2.3.0": ("flask", "<=", "2.3.0"),
            "numpy~=1.24": ("numpy", "~=", "1.24"),
            "pytest!=7.0.0": ("pytest", "!=", "7.0.0"),
        }

        for pkg_str, expected in specs.items():
            pkg = PackageSpec(pkg_str, "python")
            assert pkg.name == expected[0]
            assert pkg.operator == expected[1]
            assert pkg.version == expected[2]

    def test_package_spec_debian(self):
        """Test parsing Debian package with version."""
        from start_vm import PackageSpec

        pkg = PackageSpec("vim=2:8.2.3995-1ubuntu2", "debian")
        assert pkg.name == "vim"
        assert pkg.operator == "="
        assert pkg.version == "2:8.2.3995-1ubuntu2"
        assert pkg.to_string("debian") == "vim=2:8.2.3995-1ubuntu2"

    def test_package_spec_no_version(self):
        """Test parsing package without version."""
        from start_vm import PackageSpec

        pkg = PackageSpec("requests", "python")
        assert pkg.name == "requests"
        assert pkg.operator is None
        assert pkg.version is None
        assert not pkg.has_version()
        assert pkg.to_string("python") == "requests"

    def test_package_spec_ruby(self):
        """Test parsing Ruby gem with version."""
        from start_vm import PackageSpec

        pkg = PackageSpec("rails:7.0.4", "ruby")
        assert pkg.name == "rails"
        assert pkg.operator == ":"
        assert pkg.version == "7.0.4"

    def test_package_spec_rust(self):
        """Test parsing Rust crate with version."""
        from start_vm import PackageSpec

        pkg = PackageSpec("ripgrep@13.0.0", "rust")
        assert pkg.name == "ripgrep"
        assert pkg.operator == "@"
        assert pkg.version == "13.0.0"

    def test_package_spec_to_lockfile_entry(self):
        """Test conversion to lockfile entry format."""
        from start_vm import PackageSpec

        pkg = PackageSpec("pytest==7.4.0", "python")
        entry = pkg.to_lockfile_entry()

        assert entry["name"] == "pytest"
        assert entry["version"] == "7.4.0"
        assert entry["operator"] == "=="
        assert entry["original"] == "pytest==7.4.0"

    def test_lockfile_generation(self, mock_options, tmp_path):
        """Test lockfile generation from recipe."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()

        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "22.04",
            "release": "jammy",
            "sections": [
                {
                    "name": "python-pkgs",
                    "type": "python_packages",
                    "install": [
                        "requests==2.28.1",
                        "flask>=2.3.0",
                        "pytest",
                    ]
                },
                {
                    "name": "debian-pkgs",
                    "type": "debian_packages",
                    "install": [
                        "vim=2:8.2.3995-1ubuntu2",
                        "git",
                    ]
                }
            ],
        }
        recipe_path = recipes_dir / "test.yml"
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)

        lockfile_json = builder.generate_lockfile()
        lockfile = json.loads(lockfile_json)

        # Verify lockfile structure
        assert "generated_at" in lockfile
        assert lockfile["recipe"]["name"] == "test"
        assert lockfile["recipe"]["platform"] == "linux"
        assert "packages" in lockfile

        # Verify python packages
        assert "python-pkgs" in lockfile["packages"]
        python_pkgs = lockfile["packages"]["python-pkgs"]["packages"]
        assert len(python_pkgs) == 3
        assert python_pkgs[0]["name"] == "requests"
        assert python_pkgs[0]["version"] == "2.28.1"
        assert python_pkgs[2]["name"] == "pytest"
        assert python_pkgs[2]["version"] is None

        # Verify debian packages
        assert "debian-pkgs" in lockfile["packages"]
        debian_pkgs = lockfile["packages"]["debian-pkgs"]["packages"]
        assert len(debian_pkgs) == 2
        assert debian_pkgs[0]["name"] == "vim"
        assert debian_pkgs[0]["version"] == "2:8.2.3995-1ubuntu2"

    def test_lockfile_write(self, mock_options, tmp_path):
        """Test writing lockfile to disk."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()
        setup_dir = tmp_path / "setup"
        setup_dir.mkdir()

        recipe = {
            "name": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "22.04",
            "sections": [
                {
                    "name": "python",
                    "type": "python_packages",
                    "install": ["requests==2.28.1"]
                }
            ],
        }
        recipe_path = recipes_dir / "test.yml"
        with recipe_path.open("w") as f:
            yaml.dump(recipe, f)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = ShellBuilder(str(recipe_path), mock_options)
                builder.setup = setup_dir
                builder.prefix = "linux-ubuntu-22.04-test"
                builder.write_lockfile()

        lockfile_path = setup_dir / "linux-ubuntu-22.04-test.lock.json"
        assert lockfile_path.exists()

        with lockfile_path.open() as f:
            lockfile = json.load(f)

        assert lockfile["recipe"]["name"] == "test"
        assert "python" in lockfile["packages"]


class TestPythonBuilder:
    """Test PythonBuilder functionality."""

    def test_python_builder_creates_py_file(self, mock_options, temp_recipe_dir):
        """Test that PythonBuilder generates .py file."""
        tmp_path, recipe_path = temp_recipe_dir
        templates_dir = tmp_path / "templates"
        setup_dir = tmp_path / "setup"

        # Create minimal shell template for setup.py
        template_content = """#!/usr/bin/env python3
\"\"\"
Setup script for {{name}}
Platform: {{platform}}
OS: {{os}} {{version}}

Generated by start-vm
Python 3.8+ compatible, uses only standard library
\"\"\"

import argparse
import sys

RECIPE_NAME = "{{name}}"
PLATFORM = "{{platform}}"

def main():
    parser = argparse.ArgumentParser(description=f"Setup script for {RECIPE_NAME}")
    parser.add_argument('action', choices=['install', 'uninstall'])
    args = parser.parse_args()
    print(f"Action: {args.action}")

if __name__ == '__main__':
    main()
"""
        (templates_dir / "setup.py").write_text(template_content)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = PythonBuilder(str(recipe_path), mock_options)
                builder.setup = setup_dir
                builder.build()

        # Check that .py file was created
        generated_files = list(setup_dir.glob("*.py"))
        assert len(generated_files) == 1
        assert generated_files[0].suffix == ".py"
        assert "linux-ubuntu-20.04-test" in generated_files[0].name

    def test_python_builder_template_rendering(self, mock_options, temp_recipe_dir):
        """Test that PythonBuilder correctly renders template variables."""
        tmp_path, recipe_path = temp_recipe_dir
        templates_dir = tmp_path / "templates"
        setup_dir = tmp_path / "setup"

        template_content = """#!/usr/bin/env python3
RECIPE_NAME = "{{name}}"
PLATFORM = "{{platform}}"
OS_NAME = "{{os}}"
OS_VERSION = "{{version}}"
OS_RELEASE = "{{release}}"
"""
        (templates_dir / "setup.py").write_text(template_content)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = PythonBuilder(str(recipe_path), mock_options)
                builder.setup = setup_dir
                builder.build()

        generated_file = list(setup_dir.glob("*.py"))[0]
        content = generated_file.read_text()

        # Verify template variables were rendered correctly (new data-driven structure)
        assert "'name': \"test\"" in content
        assert "'platform': \"linux\"" in content
        assert "'os': \"ubuntu\"" in content
        assert "'version': \"20.04\"" in content
        assert "'release': \"focal\"" in content

    def test_python_builder_with_sections(self, mock_options, tmp_path):
        """Test PythonBuilder with various section types using data structures."""
        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        setup_dir = tmp_path / "setup"
        setup_dir.mkdir()

        # Create recipe with multiple section types
        recipe = {
            "name": "multi-section",
            "config": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "22.04",
            "release": "jammy",
            "sections": [
                {
                    "name": "debian-pkgs",
                    "type": "debian_packages",
                    "install": ["vim", "git"],
                },
                {
                    "name": "python-pkgs",
                    "type": "python_packages",
                    "install": ["pytest", "requests"],
                },
                {
                    "name": "shell-cmds",
                    "type": "shell",
                    "install": "echo 'test'",
                },
            ],
        }
        recipe_path = recipes_dir / "multi.yml"
        recipe_path.write_text(yaml.dump(recipe))

        # Create template that uses data structures (new approach)
        template_content = """#!/usr/bin/env python3
# Section definitions
SECTIONS = [
{% for section in sections %}
    {
        "name": "{{section.name}}",
        "type": "{{section.type}}",
        {% if section.type == "shell" %}"install": \"\"\"{{section.install}}\"\"\",
        {% else %}"install": [
            {% for package in section.install %}"{{package}}",
            {% endfor %}
        ],
        {% endif %}
    },
{% endfor %}
]

def install_section(section, dry_run=False):
    \"\"\"Install a section based on its type.\"\"\"
    pass
"""
        (templates_dir / "setup.py").write_text(template_content)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = PythonBuilder(str(recipe_path), mock_options)
                builder.setup = setup_dir
                builder.build()

        generated_file = list(setup_dir.glob("*.py"))[0]
        content = generated_file.read_text()

        # Verify SECTIONS data structure contains all sections (new Python pprint format)
        assert "SECTIONS =" in content
        assert "debian-pkgs" in content
        assert "python-pkgs" in content
        assert "shell-cmds" in content
        assert "vim" in content
        assert "git" in content
        assert "pytest" in content
        assert "requests" in content
        assert "echo 'test'" in content
        # Verify data-driven execution approach with Executor class
        assert "class Executor" in content
        assert "def exec_section" in content

    def test_python_builder_valid_python_syntax(self, mock_options, tmp_path):
        """Test that generated Python script has valid syntax."""
        import py_compile

        recipes_dir = tmp_path / "recipes"
        recipes_dir.mkdir()
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        setup_dir = tmp_path / "setup"
        setup_dir.mkdir()

        recipe = {
            "name": "syntax-test",
            "config": "test",
            "platform": "linux",
            "os": "ubuntu",
            "version": "22.04",
            "release": "jammy",
            "sections": [
                {"name": "core", "type": "debian_packages", "install": ["vim"]}
            ],
        }
        recipe_path = recipes_dir / "syntax.yml"
        recipe_path.write_text(yaml.dump(recipe))

        # Create minimal valid Python template
        template_content = """#!/usr/bin/env python3
import sys

def main():
    print("{{name}}")

if __name__ == '__main__':
    main()
"""
        (templates_dir / "setup.py").write_text(template_content)

        with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
            with mock.patch("os.listdir", return_value=[]):
                builder = PythonBuilder(str(recipe_path), mock_options)
                builder.setup = setup_dir
                builder.build()

        generated_file = list(setup_dir.glob("*.py"))[0]

        # Should not raise SyntaxError
        py_compile.compile(str(generated_file), doraise=True)

    def test_python_builder_suffix(self, mock_options, temp_recipe_dir):
        """Test that PythonBuilder uses .py suffix."""
        builder = PythonBuilder.__new__(PythonBuilder)
        assert builder.suffix == ".py"

    def test_python_builder_template(self, mock_options, temp_recipe_dir):
        """Test that PythonBuilder uses setup.py template."""
        builder = PythonBuilder.__new__(PythonBuilder)
        assert builder.template == "setup.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
