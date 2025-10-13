# Recipe Schema Documentation

This document provides the formal specification for start-vm recipe files.

## Table of Contents

- [Overview](#overview)
- [Recipe Structure](#recipe-structure)
- [Required Fields](#required-fields)
- [Optional Fields](#optional-fields)
- [Section Types](#section-types)
- [Inheritance Behavior](#inheritance-behavior)
- [Package Version Pinning](#package-version-pinning)
- [Complete Examples](#complete-examples)

## Overview

Recipes are YAML files that describe system configurations. They specify:
- Target platform and OS details
- Files to install (dotfiles, config files)
- Packages to install from various package managers
- Custom shell commands to execute
- Pre/post-install hooks

## Recipe Structure

### Minimal Recipe

```yaml
name: minimal-example
platform: linux
os: ubuntu
version: "22.04"
sections:
  - name: core
    type: debian_packages
    install:
      - vim
      - git
```

### Complete Recipe

```yaml
name: full-example
config: ubuntu
platform: linux
os: ubuntu
version: "22.04"
release: jammy
inherits: base-recipe

sections:
  - name: core-packages
    type: debian_packages
    pre_install: |
      sudo apt update
      sudo apt dist-upgrade -y
    install:
      - build-essential
      - curl
      - wget
    purge:
      - nano
    post_install: |
      echo "Core packages installed"
```

## Required Fields

### `name`
- **Type**: String
- **Description**: Unique identifier for the recipe
- **Example**: `"ubuntu-dev"`, `"macos-minimal"`
- **Constraints**: Used in generated filenames, avoid spaces and special characters

### `platform`
- **Type**: String
- **Description**: Target operating system platform
- **Valid Values**:
  - `linux` - Linux systems (Debian, Ubuntu, etc.)
  - `darwin` - macOS systems
  - `windows` - Windows systems
- **Example**: `"linux"`

### `os`
- **Type**: String
- **Description**: Specific operating system distribution
- **Examples**:
  - Linux: `"debian"`, `"ubuntu"`
  - macOS: `"macos"`
  - Windows: `"windows"`

### `version`
- **Type**: String
- **Description**: OS version number
- **Examples**:
  - Ubuntu: `"22.04"`, `"20.04"`
  - Debian: `"11"`, `"12"`
  - macOS: `"13"`, `"14"`
  - Windows: `"11"`, `"10"`
- **Note**: Use string format to preserve leading zeros and decimals

### `sections`
- **Type**: Array of Section objects
- **Description**: List of installation sections
- **Minimum**: At least one section required
- **See**: [Section Types](#section-types) for details

## Optional Fields

### `config`
- **Type**: String
- **Description**: Name of subdirectory under `config/` containing files to copy to `~/.config`
- **Example**: `"ubuntu"` maps to `config/ubuntu/`
- **Default**: None (no config files installed)

### `release`
- **Type**: String
- **Description**: OS release codename
- **Examples**:
  - Ubuntu: `"jammy"`, `"focal"`, `"bionic"`
  - Debian: `"bookworm"`, `"bullseye"`
  - Windows: `"23H2"`, `"22H2"`
- **Default**: Empty string

### `inherits`
- **Type**: String or Array of Strings
- **Description**: Parent recipe(s) to inherit sections from
- **Examples**:
  - Single: `"base-recipe"`
  - Multiple: `["base-recipe", "dev-tools"]`
- **See**: [Inheritance Behavior](#inheritance-behavior) for details

## Section Types

Each section must have `name`, `type`, and type-specific fields.

### Common Section Fields

All section types support these optional fields:

#### `pre_install`
- **Type**: String (multiline)
- **Description**: Shell commands to run before section installation
- **Example**:
  ```yaml
  pre_install: |
    sudo apt update
    sudo apt dist-upgrade -y
  ```

#### `post_install`
- **Type**: String (multiline)
- **Description**: Shell commands to run after section installation
- **Example**:
  ```yaml
  post_install: |
    sudo systemctl restart service
    echo "Installation complete"
  ```

### Linux Package Managers

#### `debian_packages`

Install packages using apt-get (Debian, Ubuntu).

**Required Fields**:
- `install`: Array of package names

**Optional Fields**:
- `purge`: Array of packages to remove

**Example**:
```yaml
- name: core
  type: debian_packages
  pre_install: |
    sudo apt update
    sudo apt dist-upgrade -y
  install:
    - build-essential
    - curl
    - wget
    - git
    - vim
    - htop
    - ncdu
  purge:
    - nano
    - vim-tiny
  post_install: |
    echo "Core packages installed"
```

**Version Pinning**:
```yaml
install:
  - python3=3.9.5-1
  - nginx=1.18.0-0ubuntu1
```

**Generated Commands**:
- Install: `sudo apt-get install -y <packages>`
- Uninstall: `sudo apt-get remove -y <packages>`
- Purge: `sudo apt-get purge -y <packages>`

#### `python_packages`

Install Python packages using pip3.

**Required Fields**:
- `install`: Array of package names

**Example**:
```yaml
- name: python-tools
  type: python_packages
  install:
    - pip
    - wheel
    - virtualenv
    - black
    - flake8
    - pytest
```

**Version Pinning**:
```yaml
install:
  - requests==2.28.0
  - django>=4.0,<5.0
  - numpy~=1.21.0
```

**Generated Commands**:
- Install: `sudo -H pip3 install <packages>`
- Uninstall: `sudo -H pip3 uninstall -y <packages>`

#### `ruby_packages`

Install Ruby gems.

**Required Fields**:
- `install`: Array of gem names

**Example**:
```yaml
- name: ruby-tools
  type: ruby_packages
  install:
    - bundler
    - rails
    - jekyll
```

**Version Pinning**:
```yaml
install:
  - rails:7.0.0
  - jekyll:4.2.0
```

**Generated Commands**:
- Install: `gem install <package>` (per package)
- Uninstall: `gem uninstall -x <package>` (per package)

#### `rust_packages`

Install Rust crates using cargo.

**Required Fields**:
- `install`: Array of crate names

**Example**:
```yaml
- name: rust-tools
  type: rust_packages
  install:
    - ripgrep
    - fd-find
    - bat
    - exa
```

**Version Pinning**:
```yaml
install:
  - ripgrep@13.0.0
  - fd-find@8.3.0
```

**Generated Commands**:
- Install: `cargo install <crate>` (per crate)
- Uninstall: `cargo uninstall <crate>` (per crate)

### macOS Package Managers

#### `homebrew_packages`

Install packages using Homebrew.

**Required Fields**:
- `install`: Array of formula/cask names

**Example**:
```yaml
- name: dev-tools
  type: homebrew_packages
  install:
    - git
    - python3
    - node
    - wget
    - ripgrep
```

**Version Pinning**:
```yaml
install:
  - python@3.9
  - node@16
```

**Generated Commands**:
- Install: `brew install <packages>`
- Uninstall: `brew uninstall <packages>`

### Windows Package Managers

#### `winget_packages`

Install packages using Windows Package Manager.

**Required Fields**:
- `install`: Array of package IDs

**Example**:
```yaml
- name: dev-tools
  type: winget_packages
  install:
    - Microsoft.VisualStudioCode
    - Git.Git
    - Python.Python.3.11
    - Microsoft.PowerShell
```

**Version Pinning**:
```yaml
install:
  - Python.Python.3.11==3.11.0
  - Git.Git==2.40.0
```

**Generated Commands**:
- Install: `winget install --id <package> --silent --accept-package-agreements`
- Uninstall: `winget uninstall --id <package> --silent`

#### `chocolatey_packages`

Install packages using Chocolatey.

**Required Fields**:
- `install`: Array of package names

**Example**:
```yaml
- name: utilities
  type: chocolatey_packages
  install:
    - 7zip
    - notepadplusplus
    - googlechrome
    - firefox
```

**Version Pinning**:
```yaml
install:
  - 7zip==19.00
  - notepadplusplus==8.4.0
```

**Generated Commands**:
- Install: `choco install <package> -y`
- Uninstall: `choco uninstall <package> -y`
- **Note**: Chocolatey is auto-installed if not present

### Cross-Platform

#### `shell`

Execute arbitrary shell commands.

**Required Fields**:
- `install`: String (multiline shell script)

**Platform Notes**:
- Linux/macOS: Bash commands
- Windows: PowerShell commands

**Example (Linux/macOS)**:
```yaml
- name: custom-setup
  type: shell
  install: |
    # Clone dotfiles repo
    git clone https://github.com/user/dotfiles.git ~/dotfiles

    # Setup custom tools
    curl -fsSL https://example.com/install.sh | bash

    # Create symlinks
    ln -sf ~/dotfiles/.zshrc ~/.zshrc
```

**Example (Windows)**:
```yaml
- name: custom-setup
  type: shell
  install: |
    # Clone dotfiles repo
    git clone https://github.com/user/dotfiles.git $env:USERPROFILE\dotfiles

    # Setup custom tools
    Invoke-WebRequest -Uri https://example.com/install.ps1 | iex
```

**Generated Behavior**:
- Install: Executes the shell script
- Uninstall: Displays warning (cannot be automatically uninstalled)

#### `powershell`

Execute PowerShell commands (Windows only).

**Required Fields**:
- `install`: String (multiline PowerShell script)

**Example**:
```yaml
- name: windows-config
  type: powershell
  install: |
    # Configure Windows settings
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "HideFileExt" -Value 0

    # Install Windows features
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

**Generated Behavior**:
- Install: Executes PowerShell script
- Uninstall: Displays warning (cannot be automatically uninstalled)

## Inheritance Behavior

Recipes can inherit sections from one or more parent recipes using the `inherits` field.

### Single Inheritance

```yaml
# recipes/base.yml
name: base
platform: linux
os: ubuntu
version: "22.04"
sections:
  - name: core
    type: debian_packages
    install:
      - build-essential
      - git

# recipes/dev.yml
name: dev
inherits: base
platform: linux
os: ubuntu
version: "22.04"
sections:
  - name: python
    type: python_packages
    install:
      - pytest
```

**Result**: `dev` recipe has both `core` (from base) and `python` sections.

### Multiple Inheritance

```yaml
# recipes/advanced.yml
name: advanced
inherits:
  - base
  - dev-tools
  - docker
platform: linux
os: ubuntu
version: "22.04"
sections:
  - name: custom
    type: shell
    install: echo "Custom setup"
```

**Precedence**: Left-to-right, then child
1. Sections from `base`
2. Sections from `dev-tools`
3. Sections from `docker`
4. Sections from `advanced` (child)

### Section Override

Child recipes can override parent sections by matching the `name` field:

```yaml
# recipes/parent.yml
sections:
  - name: core
    type: debian_packages
    install:
      - vim

# recipes/child.yml
inherits: parent
sections:
  - name: core
    type: debian_packages
    install:
      - neovim  # Replaces vim
```

**Result**: `child` recipe has `core` section with `neovim` (parent's `vim` is replaced).

### Configuration Field Inheritance

Configuration fields (`name`, `config`, `platform`, `os`, `version`, `release`) are also inherited:

```yaml
# recipes/ubuntu-base.yml
name: ubuntu-base
config: ubuntu
platform: linux
os: ubuntu
version: "22.04"
release: jammy
sections:
  - name: core
    type: debian_packages
    install: [vim]

# recipes/ubuntu-dev.yml
inherits: ubuntu-base
name: ubuntu-dev  # Override name
# config, platform, os, version, release inherited
sections:
  - name: python
    type: python_packages
    install: [pytest]
```

**Result**: `ubuntu-dev` inherits all fields from parent except `name`.

### Nested Inheritance

Inheritance can be nested (grandparent → parent → child):

```yaml
# recipes/grandparent.yml
name: grandparent
platform: linux
os: ubuntu
version: "22.04"
sections:
  - name: base
    type: debian_packages
    install: [curl]

# recipes/parent.yml
inherits: grandparent
name: parent
sections:
  - name: dev
    type: debian_packages
    install: [git]

# recipes/child.yml
inherits: parent
name: child
sections:
  - name: tools
    type: debian_packages
    install: [htop]
```

**Result**: `child` has all three sections: `base`, `dev`, `tools`.

### Inheritance Rules Summary

1. **Section Inheritance**: Child inherits all parent sections unless overridden
2. **Section Override**: Matching section names causes child to replace parent
3. **Section Append**: Non-matching sections are appended
4. **Multiple Parents**: Sections merged left-to-right
5. **Config Inheritance**: All config fields inherited with child override
6. **Nested Inheritance**: Recursive resolution through inheritance chain
7. **File Lookup**: Parent recipes must exist in same `recipes/` directory

## Package Version Pinning

All package manager types support version pinning for reproducible installations.

### Syntax by Package Manager

| Package Manager | Syntax | Example |
|----------------|--------|---------|
| Debian/Ubuntu | `=` | `python3=3.9.5-1` |
| Python (pip) | `==`, `>=`, `<=`, `>`, `<`, `~=`, `!=` | `requests==2.28.0` |
| Ruby (gem) | `:` | `rails:7.0.0` |
| Rust (cargo) | `@` | `ripgrep@13.0.0` |
| Homebrew | `@` | `python@3.9` |
| Winget | `==` | `Python.Python.3.11==3.11.0` |
| Chocolatey | `==` | `7zip==19.00` |

### Lockfile Generation

Generate a lockfile to capture exact package versions:

```bash
python3 start_vm.py --shell --lockfile recipes/ubuntu-dev.yml
```

Creates `recipes/ubuntu-dev.lock.json`:

```json
{
  "timestamp": "2025-10-13T10:30:00",
  "recipe": "ubuntu-dev",
  "platform": "linux",
  "os": "ubuntu",
  "version": "22.04",
  "sections": {
    "core": {
      "type": "debian_packages",
      "packages": [
        {
          "name": "build-essential",
          "version": "12.9ubuntu3",
          "operator": "==",
          "original": "build-essential==12.9ubuntu3"
        }
      ]
    }
  }
}
```

### Uninstall with Version Specs

During uninstall, version specifiers are automatically stripped:

```yaml
install:
  - python3==3.9.5
  - numpy>=1.21.0
```

**Uninstall command**: Removes `python3` and `numpy` (versions stripped).

## Complete Examples

### Minimal Ubuntu Recipe

```yaml
name: ubuntu-minimal
platform: linux
os: ubuntu
version: "22.04"
release: jammy

sections:
  - name: essentials
    type: debian_packages
    install:
      - vim
      - git
      - curl
```

### Full-Featured Development Environment

```yaml
name: ubuntu-dev-full
config: ubuntu
platform: linux
os: ubuntu
version: "22.04"
release: jammy
inherits: ubuntu-base

sections:
  - name: core
    type: debian_packages
    pre_install: |
      sudo apt update
      sudo apt dist-upgrade -y
    install:
      - build-essential
      - cmake
      - pkg-config
      - libssl-dev
    post_install: |
      echo "Core tools installed"

  - name: python
    type: debian_packages
    install:
      - python3
      - python3-pip
      - python3-venv
      - python3-dev

  - name: python-packages
    type: python_packages
    install:
      - pip>=21.0
      - wheel
      - virtualenv
      - black
      - flake8
      - pytest>=7.0
      - requests==2.28.0

  - name: rust
    type: shell
    install: |
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
      source $HOME/.cargo/env

  - name: rust-tools
    type: rust_packages
    install:
      - ripgrep
      - fd-find
      - bat

  - name: cleanup
    type: debian_packages
    purge:
      - nano
      - vim-tiny
```

### Windows Development Environment

```yaml
name: windows-dev
config: windows
platform: windows
os: windows
version: "11"
release: "23H2"

sections:
  - name: winget-tools
    type: winget_packages
    install:
      - Microsoft.VisualStudioCode
      - Git.Git
      - Python.Python.3.11
      - Microsoft.PowerShell
      - Microsoft.WindowsTerminal

  - name: chocolatey-utilities
    type: chocolatey_packages
    install:
      - 7zip
      - notepadplusplus
      - googlechrome

  - name: python-packages
    type: python_packages
    install:
      - pip
      - virtualenv
      - pytest

  - name: windows-features
    type: powershell
    install: |
      # Enable WSL2
      wsl --install

      # Configure Explorer settings
      Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "HideFileExt" -Value 0
```

### macOS Development Environment

```yaml
name: macos-dev
config: macos
platform: darwin
os: macos
version: "14"
release: sonoma

sections:
  - name: homebrew-core
    type: homebrew_packages
    pre_install: |
      # Install Xcode Command Line Tools
      xcode-select --install || true
    install:
      - git
      - python@3.11
      - node@18
      - wget
      - curl
      - ripgrep
      - fd
      - bat

  - name: python-tools
    type: python_packages
    install:
      - pip
      - virtualenv
      - black
      - pytest

  - name: shell-setup
    type: shell
    install: |
      # Install oh-my-zsh
      sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

      # Configure Git
      git config --global core.editor "vim"
      git config --global init.defaultBranch main
```

## Validation

Recipes are automatically validated on load. Required checks:

1. **Required Fields**: `name`, `platform`, `os`, `version`, `sections`
2. **Section Structure**: Each section has `name`, `type`, and type-appropriate fields
3. **Valid Section Types**: Must be one of the documented types
4. **Inheritance**: Parent recipes must exist

**Error Example**:
```
ERROR Recipe recipes/invalid.yml is missing required fields: {'version', 'platform'}
```

## File Structure

Default and config files referenced by recipes:

```
project/
├── recipes/
│   ├── ubuntu-base.yml
│   └── ubuntu-dev.yml
├── default/              # Files copied to $HOME
│   ├── .bashrc
│   ├── .vimrc
│   └── bin/
│       └── script.sh
├── config/
│   ├── ubuntu/           # Files copied to ~/.config (if config: ubuntu)
│   │   ├── nvim/
│   │   └── tmux/
│   └── macos/            # Files copied to ~/.config (if config: macos)
│       └── alacritty/
└── setup/                # Generated scripts
    ├── linux_ubuntu_22.04_ubuntu-base.sh
    └── linux_ubuntu_22.04_ubuntu-base.py
```

## Best Practices

1. **Naming**: Use descriptive recipe names (`ubuntu-minimal`, `macos-dev`, not `recipe1`)
2. **Inheritance**: Use base recipes for common configurations, child recipes for specialization
3. **Version Pinning**: Pin versions for production/critical systems, use unpinned for development
4. **Section Organization**: Group related packages (core tools, dev tools, languages)
5. **Pre/Post Hooks**: Use for system updates, service restarts, verification
6. **Purge Carefully**: Only purge packages you're certain aren't dependencies
7. **Testing**: Always test with `--dry-run` before actual installation
8. **Backups**: Keep backups enabled (default) when installing on existing systems

## Related Documentation

- [README.md](README.md) - Project overview and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute recipes
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes
