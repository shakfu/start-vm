import pytest
import pathlib
import argparse
from start_vm import Builder, ShellBuilder, DockerFileBuilder

@pytest.fixture
def sample_recipe():
    return """
    name: oblivion
    platform: ubuntu:20.04
    config: linux-base
    packages:
        - python3
        - git
    steps:
        - echo "Hello World"
    """

@pytest.fixture
def mock_args():
    args = argparse.Namespace()
    args.docker = False
    args.shell = True
    args.conditional = False
    args.format = False
    args.run = False
    args.strip = False
    args.executable = True
    args.section = None
    return args


def test_shell_builder_init(tmp_path, sample_recipe, mock_args):
    recipe_file = tmp_path / "test.yml"
    recipe_file.write_text(sample_recipe)
    builder = ShellBuilder(str(recipe_file), mock_args)
    assert builder.suffix == ".sh"
    assert builder.template == "shell.sh"
    assert builder.target == "oblivion.sh"
    assert isinstance(builder.setup, pathlib.Path)

def test_docker_builder_init(tmp_path, sample_recipe, mock_args):
    recipe_file = tmp_path / "test.yml"
    recipe_file.write_text(sample_recipe)
    builder = DockerFileBuilder(str(recipe_file), mock_args)
    assert builder.suffix == ".Dockerfile"
    assert builder.template == "Dockerfile"
    assert builder.prefix == ""

def test_builder_filters(tmp_path, sample_recipe, mock_args):
    recipe_file = tmp_path / "dummy.yml"
    recipe_file.write_text(sample_recipe)
    builder = ShellBuilder(str(recipe_file), mock_args)
    # Test sequence filter
    assert builder.filters["sequence"]([1, 2, 3]) == "1, 2, 3"
    # Test nosudo filter
    assert builder.filters["nosudo"]("sudo apt-get update") == " && apt-get update"
    # Test junction filter
    input_str = "line1\nline2"
    expected = " && line1 \\\n && line2 \\"
    assert builder.filters["junction"](input_str) == expected

def test_builder_recipe_loading(tmp_path, sample_recipe, mock_args):
    recipe_file = tmp_path / "test.yml"
    recipe_file.write_text(sample_recipe)
    builder = ShellBuilder(str(recipe_file), mock_args)
    assert builder.recipe["name"] == "oblivion"
    assert builder.recipe["platform"] == "ubuntu:20.04"
    assert "python3" in builder.recipe["packages"]
    assert "git" in builder.recipe["packages"]
    assert builder.recipe["steps"] == ['echo "Hello World"']
