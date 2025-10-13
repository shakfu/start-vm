# start-vm: single-step setups for fresh machines

Generates bash scripts and dockerfiles from yaml `recipe` files to provide sigle-step setups of virtual or physical machines.

## ⚠️ SECURITY WARNING

**READ THIS BEFORE RUNNING ANY RECIPES OR GENERATED SCRIPTS**

- **Recipes execute arbitrary code**: Recipe files can contain shell commands, install packages, and modify system configurations with elevated privileges.
- **Only use trusted recipes**: Never run recipes or generated scripts from untrusted sources.
- **Review before execution**: Always inspect recipe files and generated scripts before running them.
- **Test with dry-run first**: Use `--dry-run` or `--no-run` flags to preview actions without execution.
- **Backup critical data**: By default, backups are enabled, but ensure you have separate backups of critical data.
- **Elevated privileges required**: Generated scripts often require sudo/administrator access.

**Do NOT use on a pre-existing installation** without carefully reviewing what will be installed and which files will be overwritten. Existing dotfiles and config files are backed up by default, but this program can still significantly alter your system. **You have been warned!**

## Features

- Setup specifications are captured in a yaml `recipe` file.

- Generation of shell setup scripts derived from the `recipe` file in one of two modes:

    1. Auto-mode: without asking for permission (default)

    2. Conditional mode: asks for permission to install at each step.

- Generation of Dockerfiles derived from the `recipe` file

- Many example recipes are provided in the projects with corresponding bash setup files.

## Basic Usage Patterns

### Clone and Install

For example, one can install a fresh ubuntu server 24.04 LTS distro on a virtual or physical machine engine and then:

```bash
git clone https://github.com/shakfu/start-vm

cd start-vm

./setup/linx_ubuntu_22.04_base.sh
```

This is the most common usage, clone start-vm and run one of its pre-generated and saved bash `setup_*` scripts. No python code is run or requirements installed.

### Clone, Generate and Install

For this case, `start_vm`'s requirements (`Jinja2` and `PyYAML`) should be installed:

```bash

pip install -r requirements.txt

```

To generate a `setup/<platform-recipt>.sh` file from a `recipes/<recipe>.yml` file:

```bash
start_vm.py --shell --conditional recipes/<recipe>.yml
```

The generated shell setup files are created in the `setup` folder

**IMPORTANT NOTE**: As of the current implementation *everything* in `default` is copied into `$HOME`.

What is copied out of config is a function of which recipe is used such that *everything* in `config/<recipe>` is copied into `$HOME/.config`.

A minimal ubuntu 24.04 LTS `base.yml` is implemented. Forks and pull requests for other variations are of course wellcome.

## Command-line Usage

```text
usage: start_vm.py [-h] [-d] [-b] [-p] [-y] [-c] [-f] [-r] [-s] [-e] [--section SECTION]
                   [--debug] [-n] [--lockfile]
                   recipe [recipe ...]

Install Packages

positional arguments:
  recipe                recipes to install

options:
  -h, --help            show this help message and exit
  -d, --docker          generate dockerfile
  -b, --shell           generate shell file (Linux/macOS)
  -p, --powershell      generate PowerShell file (Windows)
  -y, --python          generate Python install/uninstall script
  -c, --conditional     add conditional steps
  -f, --format          format using shfmt
  -r, --run             run generated file
  -s, --strip           strip empty lines
  -e, --executable      make setup file executable
  --section SECTION     run section
  --debug               enable debug logging
  -n, --dry-run         show commands without executing
  --lockfile            generate lockfile with pinned versions
```

## The Model

```yaml
recipe:
  name: str
  config: str
  platform: str
  os: str
  version: str
  release: str
  inherits: Optional[str, list[str]]
  sections: list[section]
```

A `section` provides all the details for the installation and setup of a group of related installation targets which could be debian or ubuntu package, python modules, R packages or an application or library that is downloaded, configured and compiled from source.

It has the following structure:

```yaml
section:
  name: str
  type: str
  pre_install: Optional[str]
  install: list[str]
  purge: Optional[list[str]]
  post_install: Optional[str]
```

The optional `inherits` field provides for inheriting both configuration and sections from parent recipes.

### Configuration Inheritance

As of v0.2.0, **full configuration inheritance** is supported. Child recipes inherit all configuration fields from their parent(s):

**Inheritable Fields:**
- `name`: Recipe identifier
- `config`: Config directory name
- `platform`: Target platform (linux, darwin, windows)
- `os`: OS distribution
- `version`: OS version
- `release`: OS release codename

**Override Rules:**
1. **Child precedence**: Child values always override parent values
2. **Multiple inheritance**: Later parents override earlier parents (processed left-to-right)
3. **Nested inheritance**: Supported with recursive resolution (grandparent → parent → child)
4. **Minimal recipes**: Child can specify only `inherits` and `sections`, inheriting all config from parent

**Example: Minimal child recipe**

```yaml
# ubuntu-dev.yml - inherits all config from ubuntu-base
inherits: ubuntu-base
sections:
    - name: dev-tools
      type: debian_packages
      install:
        - nodejs
        - docker.io
```

This child recipe will inherit `platform`, `os`, `version`, `release`, `config`, and `name` from `ubuntu-base.yml`, plus all its sections. The child only needs to define what's **additional** or **different**.

**Example: Override specific fields**

```yaml
# ubuntu-24.04-dev.yml - inherits from ubuntu-dev but updates version
inherits: ubuntu-dev
version: '24.04'
release: noble
sections:
    - name: modern-tools
      type: debian_packages
      install:
        - ripgrep
        - bat
```

This creates a 3-level hierarchy: `ubuntu-base` → `ubuntu-dev` → `ubuntu-24.04-dev`, where each level can override specific fields while inheriting the rest.

### Section Inheritance

Sections are inherited from parent recipes using the following algorithm:

```python
child_section_names = [section['name'] for section in child_recipe['sections']]
for parent in parent_recipes:
    for section in parent['sections']:
      if section['name'] in child_section_names:
          continue
      child_recipe['sections'].append(section)
```

**Section Override**: If a child defines a section with the same `name` as a parent section, the child's version completely replaces the parent's.

This inheritance system enables:
- **DRY recipes**: Define common configuration once in a base recipe
- **Recipe families**: Create variations (e.g., Ubuntu 20.04, 22.04, 24.04) from one base
- **Composition**: Combine multiple base recipes with multiple inheritance
- **Maintainability**: Update base recipe, all children automatically inherit changes

## Package Version Pinning

As of v0.2.1, start-vm supports **package version pinning** for reproducible installations. You can specify exact versions, version ranges, or leave packages unpinned.

### Supported Syntax by Package Manager

**Python packages** (`python_packages`):
```yaml
install:
  - requests==2.31.0          # Exact version
  - flask>=2.3.0,<3.0         # Version range
  - django~=4.2.0             # Compatible version
  - pytest                    # Latest version (unpinned)
```

**Debian/Ubuntu packages** (`debian_packages`):
```yaml
install:
  - git=1:2.34.1-1ubuntu1.10  # Exact version with epoch
  - vim=2:8.2.3995-1ubuntu2.15
  - htop                      # Latest version
```

**Ruby gems** (`ruby_packages`):
```yaml
install:
  - rails:7.0.4               # Specific version
  - bundler                   # Latest version
```

**Rust crates** (`rust_packages`):
```yaml
install:
  - ripgrep@13.0.0            # Specific version
  - fd-find                   # Latest version
```

**Windows winget** (`winget_packages`):
```yaml
install:
  - Git.Git==2.42.0           # Specific version
  - Microsoft.VisualStudioCode # Latest version
```

**Chocolatey** (`chocolatey_packages`):
```yaml
install:
  - nodejs-lts==20.10.0       # Specific version
  - docker-desktop            # Latest version
```

**Homebrew** (`homebrew_packages`):
```yaml
install:
  - python@3.12               # Specific version
  - git                       # Latest version
```

### Lockfile Generation

Generate a lockfile to record exact versions used for reproducibility:

```bash
# Generate recipe and lockfile together
python3 start_vm.py --shell --lockfile recipes/ubuntu-pinned.yml

# This creates both:
# - setup/linux_ubuntu_22.04_ubuntu-pinned.sh
# - setup/linux_ubuntu_22.04_ubuntu-pinned.lock.json
```

The lockfile contains:
- Timestamp of generation
- Recipe metadata (name, platform, OS, version)
- All packages with their versions, operators, and original specifications
- Organized by section for easy reference

**Example lockfile structure**:
```json
{
  "generated_at": "2025-10-13T10:30:45.123456",
  "recipe": {
    "name": "ubuntu-pinned",
    "platform": "linux",
    "os": "ubuntu",
    "version": "22.04",
    "release": "jammy"
  },
  "packages": {
    "python-packages": {
      "type": "python_packages",
      "packages": [
        {
          "name": "requests",
          "version": "2.31.0",
          "operator": "==",
          "original": "requests==2.31.0"
        }
      ]
    }
  }
}
```

### Benefits of Version Pinning

1. **Reproducibility**: Same versions across different machines and time
2. **Stability**: Avoid breaking changes from automatic updates
3. **Testing**: Test against specific versions before upgrading
4. **Auditing**: Know exactly what versions are installed
5. **Documentation**: Lockfiles serve as version documentation

### Example Recipes

- `recipes/ubuntu-pinned.yml`: Comprehensive example with pinned Python and Debian packages
- `recipes/windows-pinned.yml`: Windows example with winget and Chocolatey version pinning

## Creating new recipes

Recipe files are yaml files with a certain structure. The easiest way to learn is look at the provided recipes in this project. You can then pick a recipe and just customize it or or create a new recipe and inherit from a pre-existing one as above.

## Windows Support

Windows is now fully supported via PowerShell scripts! You can generate PowerShell setup scripts for Windows using the `-p` or `--powershell` flag.

### Windows-specific Features

- **winget package manager**: Install packages using Windows Package Manager (winget)
- **Chocolatey support**: Install packages using Chocolatey package manager
- **PowerShell commands**: Execute native PowerShell scripts in sections
- **Python packages**: Install Python packages via pip on Windows
- **Automatic privilege checking**: Scripts check for Administrator privileges

### Windows Section Types

Windows recipes support the following section types:

- `winget_packages`: Install packages via Windows Package Manager
- `chocolatey_packages`: Install packages via Chocolatey (auto-installs Chocolatey if needed)
- `python_packages`: Install Python packages via pip
- `powershell`: Execute PowerShell commands
- `shell`: Execute shell commands (for cross-platform compatibility)

### Example: Generating a Windows Setup Script

```bash
# Generate PowerShell script for Windows 11
python start_vm.py --powershell recipes/windows11.yml

# Run the generated script (requires Administrator privileges)
# In PowerShell (as Administrator):
.\setup\windows_windows_11_base.ps1
```

### Example Windows Recipes

Two example Windows recipes are provided:

- `recipes/windows11.yml`: Comprehensive Windows 11 setup with development tools
- `recipes/windows10.yml`: Basic Windows 10 setup

### Windows Usage Notes

1. **Administrator privileges required**: Most package installations require running PowerShell as Administrator
2. **Execution Policy**: The scripts automatically set the execution policy to allow script execution
3. **WSL Support**: The Windows 11 recipe includes optional WSL 2 installation
4. **Chocolatey auto-install**: If Chocolatey is not installed, it will be automatically installed when needed
5. **winget availability**: Windows Package Manager (winget) comes pre-installed on Windows 11 and recent Windows 10 builds

## Python Install/Uninstall Scripts

In addition to shell scripts, Dockerfiles, and PowerShell scripts, start-vm can generate standalone Python 3.8+ install/uninstall scripts. These scripts are self-contained (standard library only) and provide a user-friendly argparse interface.

### Python Script Features

- **Python 3.8+ compatible**: Uses only standard library (no external dependencies)
- **Install/Uninstall commands**: Full bidirectional setup management
- **argparse interface**: Professional CLI with --help, --dry-run, --verbose options
- **Color-coded output**: Clear visual feedback during execution
- **Platform checking**: Warns if running on mismatched platform
- **Confirmation prompts**: Safety checks before uninstall
- **Error handling**: Comprehensive try/except blocks with clear error messages

### Generating Python Scripts

```bash
# Generate Python install/uninstall script
python3 start_vm.py --python recipes/ubuntu-base.yml

# This creates: setup/linux_ubuntu_22.04_ubuntu-base.py
```

### Using Generated Python Scripts

```bash
# View help
python3 setup/linux_ubuntu_22.04_ubuntu-base.py --help

# Dry-run to see what would be installed
python3 setup/linux_ubuntu_22.04_ubuntu-base.py install --dry-run

# Install packages and files
python3 setup/linux_ubuntu_22.04_ubuntu-base.py install

# Install with verbose output
python3 setup/linux_ubuntu_22.04_ubuntu-base.py install --verbose

# Uninstall (with confirmation prompt)
python3 setup/linux_ubuntu_22.04_ubuntu-base.py uninstall

# Uninstall dry-run
python3 setup/linux_ubuntu_22.04_ubuntu-base.py uninstall --dry-run
```

### Python Script Command-Line Options

Each generated Python script supports:

- `install`: Install all packages and copy configuration files
- `uninstall`: Remove packages and delete configuration files
- `-n, --dry-run`: Show what would be done without executing
- `-v, --verbose`: Enable verbose output with detailed logging
- `--version`: Display script and recipe information

### Supported Package Types

Python scripts support all section types:
- `debian_packages`: apt-get install/remove
- `python_packages`: pip install/uninstall
- `ruby_packages`: gem install/uninstall
- `rust_packages`: cargo install/uninstall
- `homebrew_packages`: brew install/uninstall
- `shell`: Execute custom shell commands

### Python Script Benefits

1. **Cross-platform**: Works on any system with Python 3.8+
2. **No external dependencies**: Uses only Python standard library
3. **Bidirectional**: Full install AND uninstall support
4. **Safe**: Dry-run mode and confirmation prompts
5. **Professional**: argparse interface with comprehensive help
6. **Portable**: Single self-contained script file

## TODO

- [x] Generate python install/uninstall scripts

- [ ] create uninstall scripts for shell/PowerShell (reverse the install)

- [x] add powershell template for windows and windows pkg manager support

- [ ] add parameters which can be interpolated initially at the yaml level

- [ ] Possibly add Pydantic models (might be too heavy a download):

    ```python
    from pydantic import BaseModel, Field

    class Section(BaseModel):
        name: str
        type: Literal['debian_packages', 'python_packages', ...]
        pre_install: Optional[str] = None
        install: Union[List[str], str]
        purge: Optional[List[str]] = None
        post_install: Optional[str] = None

    class Recipe(BaseModel):
        name: str
        config: Optional[str] = None
        platform: str
        os: str
        version: str
        release: str
        inherits: Optional[Union[str, List[str]]] = None
        sections: List[Section]
    ```
