# Troubleshooting Guide

This guide helps you resolve common issues when working with start-vm.

## Table of Contents

- [Script Generation Issues](#script-generation-issues)
- [Script Execution Issues](#script-execution-issues)
- [Package Installation Issues](#package-installation-issues)
- [File Installation Issues](#file-installation-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debugging Techniques](#debugging-techniques)
- [Getting Help](#getting-help)

## Script Generation Issues

### Error: Recipe file not found

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'recipes/my-recipe.yml'
```

**Causes**:
- Recipe file path is incorrect
- Working directory is wrong
- Recipe file doesn't exist

**Solutions**:

1. Verify file exists:
   ```bash
   ls recipes/my-recipe.yml
   ```

2. Check working directory:
   ```bash
   pwd  # Should be start-vm project root
   ```

3. Use correct path:
   ```bash
   python3 start_vm.py --shell recipes/my-recipe.yml  # Not just my-recipe.yml
   ```

### Error: Missing required fields

**Symptoms**:
```
ERROR Recipe recipes/my-recipe.yml is missing required fields: {'version', 'platform'}
```

**Causes**:
- Recipe is missing required fields
- YAML structure is incorrect

**Solutions**:

1. Add missing fields:
   ```yaml
   name: my-recipe
   platform: linux        # ADD THIS
   os: ubuntu
   version: "22.04"       # ADD THIS
   sections:
     - name: core
       type: debian_packages
       install: [vim]
   ```

2. Verify all required fields are present:
   - `name`
   - `platform`
   - `os`
   - `version`
   - `sections`

### Error: Invalid section type

**Symptoms**:
```
ERROR Invalid section type 'invalid_type' in section 'my-section'
```

**Causes**:
- Section type not supported
- Typo in section type

**Solutions**:

1. Check valid section types:
   - Linux: `debian_packages`, `python_packages`, `ruby_packages`, `rust_packages`, `homebrew_packages`, `shell`
   - Windows: `winget_packages`, `chocolatey_packages`, `python_packages`, `powershell`, `shell`
   - macOS: `homebrew_packages`, `python_packages`, `ruby_packages`, `rust_packages`, `shell`

2. Fix typo:
   ```yaml
   # Wrong
   type: debain_packages

   # Correct
   type: debian_packages
   ```

### Error: YAML syntax error

**Symptoms**:
```
yaml.scanner.ScannerError: while scanning a simple key
  in "recipes/my-recipe.yml", line 5, column 1
```

**Causes**:
- Invalid YAML syntax
- Incorrect indentation
- Missing colons

**Solutions**:

1. Check YAML syntax online: https://www.yamllint.com/

2. Common YAML mistakes:
   ```yaml
   # Wrong: missing colon
   name ubuntu-base

   # Correct
   name: ubuntu-base

   # Wrong: inconsistent indentation
   sections:
     - name: core
         type: debian_packages  # 4 spaces instead of 2

   # Correct
   sections:
     - name: core
       type: debian_packages

   # Wrong: tabs instead of spaces
   sections:
   ⇥- name: core  # Tab character

   # Correct: use spaces
   sections:
     - name: core  # 2 spaces
   ```

3. Use YAML validator:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('recipes/my-recipe.yml'))"
   ```

## Script Execution Issues

### Error: Permission denied

**Symptoms**:
```bash
./setup/linux_ubuntu_22.04_base.sh: Permission denied
```

**Causes**:
- Script is not executable

**Solutions**:

1. Make script executable:
   ```bash
   chmod +x setup/linux_ubuntu_22.04_base.sh
   ```

2. Or run with interpreter:
   ```bash
   bash setup/linux_ubuntu_22.04_base.sh install
   python3 setup/linux_ubuntu_22.04_base.py install
   ```

### Error: Command not found

**Symptoms**:
```
sudo: command not found
apt-get: command not found
```

**Causes**:
- Command not installed
- Command not in PATH
- Wrong platform (e.g., running Ubuntu recipe on macOS)

**Solutions**:

1. Verify platform matches recipe:
   ```bash
   # Check current platform
   uname -s  # Linux, Darwin, or MINGW64_NT-* (Windows)

   # Check recipe platform
   grep "platform:" recipes/my-recipe.yml
   ```

2. Install missing command:
   ```bash
   # Debian/Ubuntu
   apt-get update && apt-get install sudo

   # macOS (for brew)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

### Error: sudo requires password

**Symptoms**:
```
[sudo] password for user:
```

**Causes**:
- User needs to enter password for sudo commands

**Solutions**:

1. Run script interactively and enter password when prompted

2. Configure passwordless sudo (not recommended for security):
   ```bash
   # Add to /etc/sudoers using visudo
   username ALL=(ALL) NOPASSWD: ALL
   ```

3. Run script as root (if appropriate):
   ```bash
   sudo bash setup/linux_ubuntu_22.04_base.sh install
   ```

### Error: Script fails on specific section

**Symptoms**:
```
[ERROR] Installing core packages failed
```

**Causes**:
- Package not available
- Network issue
- Dependency conflict

**Solutions**:

1. Run with verbose flag:
   ```bash
   ./setup/linux_ubuntu_22.04_base.sh install --verbose
   ```

2. Check specific error message

3. Test specific package:
   ```bash
   # Debian/Ubuntu
   apt-cache policy package-name
   sudo apt-get install package-name

   # macOS
   brew info package-name
   brew install package-name
   ```

## Package Installation Issues

### Error: Package not found

**Symptoms**:
```
E: Unable to locate package package-name
```

**Causes**:
- Package name is incorrect
- Package not in repository
- Repository not updated

**Solutions**:

1. Update package lists:
   ```bash
   # Debian/Ubuntu
   sudo apt update

   # macOS
   brew update
   ```

2. Search for correct package name:
   ```bash
   # Debian/Ubuntu
   apt-cache search keyword

   # macOS
   brew search keyword

   # Windows
   winget search keyword
   ```

3. Add required repository:
   ```bash
   # Example: Add PPA for Ubuntu
   sudo add-apt-repository ppa:repository/name
   sudo apt update
   ```

### Error: Unmet dependencies

**Symptoms**:
```
The following packages have unmet dependencies:
  package-name : Depends: dependency-name but it is not going to be installed
```

**Causes**:
- Dependency not available
- Version conflict
- Repository misconfiguration

**Solutions**:

1. Fix broken dependencies:
   ```bash
   sudo apt --fix-broken install
   ```

2. Install dependencies manually:
   ```bash
   sudo apt install dependency-name
   ```

3. Use aptitude for better dependency resolution:
   ```bash
   sudo apt install aptitude
   sudo aptitude install package-name
   ```

### Error: Package installation fails

**Symptoms**:
```
Errors were encountered while processing:
  package-name
```

**Causes**:
- Post-installation script failed
- Configuration error
- Disk space issue

**Solutions**:

1. Check disk space:
   ```bash
   df -h
   ```

2. Check detailed error:
   ```bash
   sudo apt install package-name  # Run manually to see full error
   ```

3. Reconfigure package:
   ```bash
   sudo dpkg --configure -a
   sudo apt --fix-broken install
   ```

## File Installation Issues

### Error: Source not found

**Symptoms**:
```
[WARN] Source not found: default/.bashrc
```

**Causes**:
- File doesn't exist in default/ or config/ directory
- Recipe references non-existent file

**Solutions**:

1. Check if file exists:
   ```bash
   ls default/.bashrc
   ```

2. Create missing file:
   ```bash
   touch default/.bashrc
   ```

3. Remove from recipe if not needed:
   ```yaml
   # Edit recipe to remove non-existent file
   ```

### Error: Failed to copy file

**Symptoms**:
```
[ERROR] Failed to copy .bashrc: Permission denied
```

**Causes**:
- Insufficient permissions
- Destination directory doesn't exist
- File is in use

**Solutions**:

1. Check destination permissions:
   ```bash
   ls -la $HOME
   ```

2. Create destination directory:
   ```bash
   mkdir -p $HOME/.config
   ```

3. Close programs using the file

### Backup directory not created

**Symptoms**:
- No backup message shown
- Backup directory doesn't exist

**Causes**:
- No existing files to backup
- Dry-run mode enabled
- Backup disabled with --no-backup

**Solutions**:

1. Check if files exist to backup:
   ```bash
   ls -la ~/  # Check for dotfiles
   ```

2. Verify backup is enabled:
   ```bash
   # Should show "Backup enabled" message
   ./setup/script.sh install --verbose
   ```

3. Check backup directory after installation:
   ```bash
   ls -la ~/.dotfiles_backup_*
   ```

## Platform-Specific Issues

### Linux Issues

#### apt-get: command not found

**Cause**: Not using Debian/Ubuntu-based distribution

**Solution**: Use appropriate package manager recipe:
- Fedora/RHEL: Use `dnf` or `yum`
- Arch: Use `pacman`
- openSUSE: Use `zypper`

**Note**: start-vm currently supports Debian/Ubuntu. Contributions for other distros welcome!

#### Repository errors

**Symptoms**:
```
W: Failed to fetch http://archive.ubuntu.com/ubuntu/...
```

**Solutions**:
```bash
# Change to different mirror
sudo sed -i 's/archive.ubuntu.com/mirror.example.com/g' /etc/apt/sources.list

# Or use main server
sudo sed -i 's/[a-z]*.archive.ubuntu.com/archive.ubuntu.com/g' /etc/apt/sources.list
```

### macOS Issues

#### Xcode Command Line Tools not installed

**Symptoms**:
```
xcrun: error: invalid active developer path
```

**Solution**:
```bash
xcode-select --install
```

#### Homebrew not installed

**Symptoms**:
```
brew: command not found
```

**Solution**:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Permission denied on /usr/local

**Symptoms**:
```
Error: Permission denied @ dir_s_mkdir - /usr/local/Frameworks
```

**Solution**:
```bash
sudo chown -R $(whoami) /usr/local/*
```

#### M1/M2 Mac architecture issues

**Symptoms**:
- Package not available for ARM
- Binary incompatibility

**Solutions**:
```bash
# Install Rosetta 2
softwareupdate --install-rosetta

# Run under Rosetta
arch -x86_64 brew install package-name
```

### Windows Issues

#### PowerShell execution policy

**Symptoms**:
```
execution of scripts is disabled on this system
```

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Not running as Administrator

**Symptoms**:
```
ERROR: Administrator privileges required
```

**Solution**:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Run script again

#### Winget not available

**Symptoms**:
```
winget: The term 'winget' is not recognized
```

**Solutions**:
1. Update Windows to latest version
2. Install App Installer from Microsoft Store
3. Or install manually: https://github.com/microsoft/winget-cli/releases

#### Chocolatey installation fails

**Symptoms**:
```
Exception calling "DownloadString"
```

**Solutions**:
```powershell
# Try alternative installation
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

## Debugging Techniques

### Enable Verbose Output

Get detailed information about what's happening:

```bash
# Bash
./setup/script.sh install --verbose

# Python
python3 setup/script.py install --verbose

# PowerShell
.\setup\script.ps1 install -Verbose
```

### Use Dry-Run Mode

Preview actions without executing:

```bash
# Bash
./setup/script.sh install --dry-run

# Python
python3 setup/script.py install --dry-run

# PowerShell
.\setup\script.ps1 install -DryRun
```

### Check Generated Scripts

Examine generated scripts for issues:

```bash
# View bash script
less setup/linux_ubuntu_22.04_base.sh

# View Python script
less setup/linux_ubuntu_22.04_base.py

# Search for specific function
grep -A 10 "install_section_1" setup/linux_ubuntu_22.04_base.sh
```

### Test Individual Commands

Run commands manually to isolate issues:

```bash
# Test package installation
sudo apt-get install package-name

# Test file copy
cp -rf default/.bashrc $HOME/.bashrc

# Test shell command
eval "command from recipe"
```

### Check Logs

System logs may contain useful information:

```bash
# Debian/Ubuntu
tail -f /var/log/apt/history.log
tail -f /var/log/dpkg.log

# macOS
log show --predicate 'process == "install"' --last 10m

# Windows
Get-EventLog -LogName Application -Newest 50
```

### Validate Recipe

Check recipe structure:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('recipes/my-recipe.yml'))"

# Check for required fields
python3 start_vm.py --dry-run --shell recipes/my-recipe.yml
```

### Test in Clean Environment

Use container or VM to test:

```bash
# Docker (Linux only)
docker run -it ubuntu:22.04 bash
# Then clone repo and test

# Or use generated Dockerfile
python3 start_vm.py --docker recipes/ubuntu-base.yml
docker build -t test -f setup/Dockerfile.ubuntu-base .
```

## Common Error Messages

### "ValueError: Missing required fields"

**Fix**: Add required fields to recipe (name, platform, os, version, sections)

### "FileNotFoundError: config/ubuntu"

**Fix**: Either create the directory or remove `config: ubuntu` from recipe

### "Command not found: python3"

**Fix**: Use `python` instead of `python3`, or install Python 3

### "Permission denied"

**Fix**: Run with sudo (Linux/macOS) or as Administrator (Windows)

### "Package has unmet dependencies"

**Fix**: Run `sudo apt update && sudo apt --fix-broken install`

### "No such file or directory: default/.bashrc"

**Fix**: Either create the file or remove it from DEFAULT_FILES in recipe

### "Recipe file is empty or invalid"

**Fix**: Check YAML syntax, ensure file is not empty

### "Section <name> not found"

**Fix**: Ensure section exists in recipe when using `--section` flag

## Getting Help

If you can't resolve your issue:

1. **Check Documentation**:
   - [README.md](README.md) - Overview and quick start
   - [RECIPE_SCHEMA.md](RECIPE_SCHEMA.md) - Recipe specification
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

2. **Search Issues**: Check if someone else had the same problem:
   https://github.com/shakfu/start-vm/issues

3. **Create Issue**: If problem persists, create a new issue with:
   - start-vm version
   - Platform and OS version
   - Recipe file (or relevant parts)
   - Complete error message
   - Steps to reproduce
   - What you've tried

4. **Provide Context**:
   ```bash
   # Include this information in your issue
   python3 --version
   uname -a  # or: ver (Windows)
   cat recipes/my-recipe.yml
   ```

## Additional Resources

- **Recipe Schema**: [RECIPE_SCHEMA.md](RECIPE_SCHEMA.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issue Tracker**: https://github.com/shakfu/start-vm/issues
- **Discussions**: https://github.com/shakfu/start-vm/discussions
