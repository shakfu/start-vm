# Contributing to start-vm

Thank you for your interest in contributing to start-vm! This guide will help you create high-quality recipes and contribute to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Recipe Development Workflow](#recipe-development-workflow)
- [Recipe Style Guide](#recipe-style-guide)
- [Testing Recipes](#testing-recipes)
- [Platform-Specific Considerations](#platform-specific-considerations)
- [Submitting Contributions](#submitting-contributions)
- [Code Contributions](#code-contributions)

## Getting Started

### Prerequisites

1. Python 3.8 or higher
2. Git
3. Target platform for testing (Linux, macOS, or Windows)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/shakfu/start-vm.git
cd start-vm

# Install dependencies
pip install -r requirements.txt

# Run tests
make test
```

## Recipe Development Workflow

### 1. Plan Your Recipe

Before writing a recipe, clearly define:

- **Target Platform**: Linux (debian/ubuntu), macOS (darwin), or Windows
- **Purpose**: What environment does this recipe create?
- **Audience**: Who is this recipe for? (developers, data scientists, minimal setups, etc.)
- **Dependencies**: Does it build on an existing recipe via inheritance?

### 2. Create Recipe File

Create a new YAML file in the `recipes/` directory:

```bash
touch recipes/my-recipe.yml
```

### 3. Write Recipe

Follow the [Recipe Schema Documentation](RECIPE_SCHEMA.md) and [Style Guide](#recipe-style-guide).

**Minimal Template**:

```yaml
name: my-recipe
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
```

### 4. Generate Scripts

Generate scripts for testing:

```bash
# Generate bash script
python3 start_vm.py --shell recipes/my-recipe.yml

# Generate Python script
python3 start_vm.py --python recipes/my-recipe.yml

# Generate PowerShell script (Windows only)
python3 start_vm.py --powershell recipes/my-recipe.yml
```

### 5. Test with Dry-Run

Always test with dry-run first:

```bash
# Bash
./setup/linux_ubuntu_22.04_my-recipe.sh install --dry-run

# Python
python3 setup/linux_ubuntu_22.04_my-recipe.py install --dry-run
```

### 6. Test Installation

Test on a clean system:

- Use a virtual machine (VirtualBox, VMware, Hyper-V)
- Use a container (Docker)
- Use a cloud instance (AWS, GCP, Azure)

**Never test on your primary development machine!**

### 7. Test Uninstallation

Verify uninstall works correctly:

```bash
./setup/linux_ubuntu_22.04_my-recipe.sh uninstall --dry-run
```

### 8. Document

Add comments in your recipe explaining:
- Purpose of each section
- Why specific packages are included
- Any special configuration steps

## Recipe Style Guide

### File Naming

- **Recipe files**: `recipes/<platform>-<purpose>.yml`
  - Examples: `ubuntu-minimal.yml`, `macos-dev.yml`, `windows-base.yml`
- **Use lowercase and hyphens**: Not `Ubuntu_Dev.yml` or `ubuntuDev.yml`

### Recipe Structure

#### Required Fields Order

```yaml
name: recipe-name
config: config-dir
platform: linux
os: ubuntu
version: "22.04"
release: jammy
inherits: parent-recipe

sections:
  # sections here
```

#### Section Organization

Group related packages logically:

```yaml
sections:
  # 1. System updates and core utilities
  - name: core
    type: debian_packages
    pre_install: |
      sudo apt update
      sudo apt dist-upgrade -y
    install:
      - build-essential
      - curl
      - wget

  # 2. Programming languages
  - name: python
    type: debian_packages
    install:
      - python3
      - python3-pip

  # 3. Language-specific packages
  - name: python-packages
    type: python_packages
    install:
      - pip
      - virtualenv

  # 4. Development tools
  - name: dev-tools
    type: debian_packages
    install:
      - git
      - vim

  # 5. Optional: cleanup
  - name: cleanup
    type: debian_packages
    purge:
      - nano
```

### Naming Conventions

#### Recipe Names

- **Descriptive**: Clearly indicate platform and purpose
- **Pattern**: `<platform>-<purpose>`
  - Good: `ubuntu-minimal`, `macos-dev`, `debian-server`
  - Bad: `recipe1`, `test`, `my-setup`

#### Section Names

- **Lowercase with hyphens**: `python-packages`, not `Python_Packages`
- **Descriptive**: Clearly indicate what the section installs
  - Good: `core-utils`, `python-tools`, `dev-dependencies`
  - Bad: `section1`, `stuff`, `misc`

### Comments

Add comments for clarity:

```yaml
sections:
  - name: core
    type: debian_packages
    # Essential build tools for compiling from source
    install:
      - build-essential
      - cmake
      - pkg-config

  - name: custom-setup
    type: shell
    install: |
      # Install Rust toolchain
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

      # Add cargo to PATH for current session
      source $HOME/.cargo/env
```

### Package Lists

- **Alphabetical order**: Makes it easier to find and avoid duplicates
- **One package per line**: Improves readability and diffs

```yaml
# Good
install:
  - black
  - flake8
  - mypy
  - pytest
  - requests

# Bad
install:
  - pytest
  - black
  - requests
  - mypy
  - flake8
```

### Version Pinning

- **Use for production recipes**: Ensures reproducibility
- **Document why**: Explain why specific versions are required

```yaml
install:
  - requests==2.28.0  # Required for compatibility with legacy API
  - django>=4.0,<5.0  # LTS version, tested with project
```

### Shell Commands

- **Use multiline format**: More readable than single line
- **Add comments**: Explain what each command does
- **Check for errors**: Use `set -e` or error handling

```yaml
# Good
- name: rust-setup
  type: shell
  install: |
    # Download and install Rust toolchain
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

    # Source cargo environment
    source $HOME/.cargo/env

    # Verify installation
    rustc --version

# Bad
- name: rust-setup
  type: shell
  install: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && source $HOME/.cargo/env
```

## Testing Recipes

### Test Environments

#### Option 1: Virtual Machines

**VirtualBox** (recommended for beginners):
```bash
# 1. Download ISO for target OS
# 2. Create new VM
# 3. Install OS
# 4. Take snapshot before testing
# 5. Test recipe
# 6. Restore snapshot for retesting
```

**VMware / Hyper-V**: Similar workflow to VirtualBox

#### Option 2: Docker Containers

**Linux recipes only**:

```bash
# Generate Dockerfile
python3 start_vm.py --docker recipes/ubuntu-minimal.yml

# Build image
docker build -t test-recipe -f setup/Dockerfile.ubuntu-minimal .

# Run container
docker run -it test-recipe bash
```

#### Option 3: Cloud Instances

**AWS, GCP, Azure**:

1. Create instance with target OS
2. SSH into instance
3. Clone repository
4. Test recipe
5. Terminate instance

### Testing Checklist

Before submitting a recipe, verify:

- [ ] Recipe generates without errors: `python3 start_vm.py --shell recipes/my-recipe.yml`
- [ ] Syntax is valid: Check for YAML errors
- [ ] Dry-run shows expected actions: `./setup/*.sh install --dry-run`
- [ ] Installation succeeds on clean system
- [ ] All packages are installed correctly
- [ ] Config files are in correct locations
- [ ] Pre/post-install hooks execute successfully
- [ ] Uninstall works correctly: `./setup/*.sh uninstall --dry-run`
- [ ] Backup system works as expected
- [ ] No sensitive data in recipe (passwords, keys, tokens)
- [ ] Recipe follows style guide
- [ ] Documentation is complete

### Common Testing Issues

#### Package Not Found

**Problem**: Package name is incorrect or not available in repository

**Solution**:
```bash
# Search for correct package name
apt-cache search <package>     # Debian/Ubuntu
brew search <package>           # macOS
winget search <package>         # Windows
```

#### Permission Denied

**Problem**: Script needs elevated privileges

**Solution**:
- Bash/Python: Run with `sudo` or as root
- PowerShell: Run as Administrator

#### Pre-install Hook Fails

**Problem**: Pre-install script returns non-zero exit code

**Solution**:
- Add error handling
- Use `|| true` for non-critical commands
- Check command availability before running

```yaml
pre_install: |
  # Will fail if command doesn't exist
  some-command

  # Better: check first
  if command -v some-command &> /dev/null; then
    some-command
  fi
```

## Platform-Specific Considerations

### Linux (Debian/Ubuntu)

#### Package Availability

- Check package exists: `apt-cache search <package>`
- Verify version: `apt-cache policy <package>`
- Consider PPAs for newer versions

#### System Updates

Always update package lists before installation:

```yaml
pre_install: |
  sudo apt update
  sudo apt dist-upgrade -y
```

#### Dependencies

Some packages require specific dependencies:

```yaml
- name: python-build-deps
  type: debian_packages
  install:
    - python3-dev
    - libssl-dev
    - libffi-dev
    - libbz2-dev
```

### macOS (darwin)

#### Homebrew

- Xcode Command Line Tools required: `xcode-select --install`
- Homebrew must be installed first (or use pre_install)

```yaml
pre_install: |
  # Install Homebrew if not present
  if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
```

#### Architecture

- M1/M2 Macs use ARM architecture
- Some packages may need `arch` prefix for Intel compatibility

#### Permissions

- May need to grant Full Disk Access for some operations
- System Integrity Protection (SIP) may block certain modifications

### Windows

#### Package Managers

**Winget**:
- Built into Windows 11 and Windows 10 (recent versions)
- Use full package IDs: `Microsoft.VisualStudioCode`, not `vscode`

**Chocolatey**:
- Auto-installed by generated scripts
- Requires administrator privileges

#### PowerShell Execution Policy

Users may need to enable script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Administrator Rights

- Most installations require administrator privileges
- Scripts check for admin rights automatically

#### Path Separators

Use Windows path separators in PowerShell sections:

```yaml
type: powershell
install: |
  # Use backslashes for Windows paths
  Copy-Item "C:\Source\file.txt" "C:\Destination\file.txt"

  # Or use PowerShell path methods
  $dest = Join-Path $env:USERPROFILE "Documents\file.txt"
```

## Submitting Contributions

### Recipe Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b recipe/ubuntu-data-science`
3. **Add your recipe**: `recipes/ubuntu-data-science.yml`
4. **Generate scripts**: Run script generation to verify
5. **Test thoroughly**: Use the testing checklist
6. **Commit changes**:
   ```bash
   git add recipes/ubuntu-data-science.yml
   git commit -m "Add Ubuntu data science recipe

   - Includes Python data science stack
   - Jupyter notebook setup
   - Common ML libraries
   "
   ```
7. **Push to your fork**: `git push origin recipe/ubuntu-data-science`
8. **Create Pull Request**: Describe recipe purpose and testing performed

### Pull Request Guidelines

**PR Title Format**: `Add <platform> recipe for <purpose>`

**Example**: `Add Ubuntu recipe for data science environment`

**PR Description Should Include**:
- Purpose of the recipe
- Target platform and version
- Testing performed (environment, commands run)
- Any special notes or limitations

**Example PR Description**:

```markdown
## Description
Adds a comprehensive Ubuntu 22.04 recipe for data science work.

## Details
- Python 3.11 with data science stack (numpy, pandas, scikit-learn)
- Jupyter notebook with extensions
- R with common statistical packages
- Database tools (PostgreSQL client, SQLite)

## Testing
- [x] Generated bash script successfully
- [x] Tested on clean Ubuntu 22.04 VM (VirtualBox)
- [x] All packages installed without errors
- [x] Jupyter launches correctly
- [x] Uninstall tested with dry-run

## Notes
- Recipe inherits from ubuntu-base for core utilities
- Includes 8GB of downloads (mostly ML libraries)
- Estimated install time: 15-20 minutes
```

## Code Contributions

### Areas for Contribution

- **New section types**: Add support for new package managers
- **Template improvements**: Enhance generated script quality
- **Bug fixes**: Fix issues in existing code
- **Tests**: Add test cases for better coverage
- **Documentation**: Improve guides and examples

### Development Workflow

1. **Create issue**: Discuss changes before implementing
2. **Follow code style**: Run `make test` before committing
3. **Add tests**: All new features must have tests
4. **Update documentation**: Update relevant docs
5. **Run tests**: Ensure `make test` passes

### Code Style

- **Python**: Follow PEP 8
- **Bash**: Use shellcheck for linting
- **PowerShell**: Follow PowerShell best practices
- **YAML**: 2-space indentation, no tabs

### Testing Requirements

All code changes must:
- Pass existing tests: `make test`
- Add tests for new functionality
- Achieve reasonable code coverage

```bash
# Run tests
make test

# Run specific test
pytest tests/test_builder.py::TestBuilderValidation
```

## Getting Help

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Refer to [RECIPE_SCHEMA.md](RECIPE_SCHEMA.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## License

By contributing to start-vm, you agree that your contributions will be licensed under the project's license.

Thank you for contributing to start-vm!
