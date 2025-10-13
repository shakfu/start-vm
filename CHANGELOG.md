# CHANGELOG

All notable project-wide changes will be documented in this file. Note that each subproject has its own CHANGELOG.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and [Commons Changelog](https://common-changelog.org). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of Changes

- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.

---

## [Unreleased]

### Added

- **Integrated Dotfiles Validation**: Validation functionality now built into start_vm.py
  - New `--validate` flag to audit config/ and default/ directories
  - New `-v, --verbose` flag for detailed validation statistics
  - `DotfilesValidator` class integrated into start_vm.py (370 lines)
  - Identifies orphaned config directories (exist but not referenced by recipes)
  - Identifies empty config directories (only .keep files)
  - Finds old/stale files not modified in >1 year
  - Platform-specific file classification (Linux/macOS/Windows/cross-platform)
  - Detailed statistics: file counts, sizes, modification dates
  - Cleanup recommendations based on findings
  - Usage: `python3 start_vm.py --validate [-v]`
  - Standalone `validate_dotfiles.py` now deprecated (still available for --max-age option)
  - **DOTFILES_VALIDATION.md**: Complete guide to using validation
    - Usage examples with integrated and legacy commands
    - Understanding validation reports
    - Common scenarios and solutions
    - Integration with repository maintenance workflows
    - Advanced usage patterns and filtering
    - Current repository status snapshot

- **Comprehensive Documentation Suite**: Four new documentation files for better project understanding and contribution
  - **RECIPE_SCHEMA.md**: Formal specification of recipe file structure
    - Complete field reference with types and descriptions
    - Detailed section type documentation with examples
    - Inheritance behavior explained with multiple examples
    - Package version pinning syntax for all package managers
    - Lockfile generation documentation
    - Complete recipe examples for each platform
    - Validation rules and error messages
    - Best practices and style recommendations
  - **CONTRIBUTING.md**: Guide for contributing recipes and code
    - Recipe development workflow (plan, create, generate, test)
    - Comprehensive style guide for recipes
    - Testing checklist and procedures
    - Platform-specific considerations (Linux, macOS, Windows)
    - Pull request guidelines with examples
    - Code contribution guidelines
  - **TROUBLESHOOTING.md**: Solutions for common issues
    - Script generation issues and fixes
    - Script execution problems
    - Package installation errors
    - File installation issues
    - Platform-specific troubleshooting (Linux, macOS, Windows)
    - Debugging techniques (verbose mode, dry-run, manual testing)
    - Common error messages with solutions
  - **README.md**: Enhanced with prominent security warning section
    - Warning about arbitrary code execution in recipes
    - Advice to only use trusted recipes
    - Recommendation to review before execution
    - Reminder to use dry-run for testing
    - Notes about backup system and elevated privileges
  - All documentation cross-referenced for easy navigation
  - Comprehensive examples and troubleshooting scenarios
  - Enables community contributions with clear guidelines

- **Automatic Backup System**: All three script generation targets (Python, bash, PowerShell) now include automatic backup functionality
  - **Backup by default**: Existing dotfiles and config files are automatically backed up before being overwritten
  - **Timestamped backups**: Backups are stored in `~/.dotfiles_backup_<timestamp>/` (or `%USERPROFILE%\.dotfiles_backup_<timestamp>\` on Windows)
  - **Opt-out capability**: New `--no-backup` / `-NoBackup` flag to disable backups if desired
  - **Smart backup creation**: Backup directory is only created if there are actually files to backup
  - **Dry-run support**: `--dry-run` mode shows which files would be backed up without actually creating backups
  - **Verbose mode**: `--verbose` flag shows detailed backup operations including destination paths
  - **Backup location reporting**: Script displays backup directory location at end of installation
  - **Implementation details**:
    - Python: `backup_file_or_dir()` function with global `BACKUP_DIR` variable
    - Bash: `backup_file_or_dir()` function with `BACKUP_DIR` environment variable
    - PowerShell: `Backup-FileOrDir` function with script-scoped `$BACKUP_DIR` variable
  - All three implementations maintain feature parity and consistent user experience
  - Protects against accidental data loss during system configuration
  - Enables easy rollback by restoring files from backup directory

- **Bash and PowerShell Bidirectional Setup Management**: Both bash and PowerShell script templates now support full install/uninstall functionality
  - **Bash Script (`templates/shell.sh`)** completely rewritten with 371 lines:
    - Command-line argument parsing for `install` and `uninstall` commands
    - `--dry-run` and `--verbose` flags for safe testing
    - Data-driven architecture with `DEFAULT_FILES` and `CONFIG_FILES` arrays
    - Helper functions: `copy_file_or_dir()`, `remove_file_or_dir()`, `strip_version_spec()`
    - Section-specific install/uninstall functions for all package manager types
    - Confirmation prompt before destructive uninstall operations
    - Version spec stripping to handle pinned packages (e.g., `python3==3.9.5` → `python3`)
    - Reverse-order section processing during uninstall (last installed, first removed)
    - Comprehensive help output with usage examples
  - **PowerShell Script (`templates/shell.ps1`)** completely rewritten with 387 lines:
    - Parameter-based interface with `ValidateSet` for install/uninstall
    - `-DryRun`, `-Verbose`, `-Help` switches
    - Data-driven architecture with `$DEFAULT_FILES` and `$CONFIG_FILES` arrays
    - PowerShell functions: `Copy-FileOrDir`, `Remove-FileOrDir`, `Get-PackageNameWithoutVersion`
    - Section-specific Install-SectionN/Uninstall-SectionN functions
    - Confirmation prompt before uninstall
    - Version spec stripping using PowerShell regex
    - Reverse-order section processing during uninstall
    - Administrator privilege checking (install only)
    - Comprehensive help with `Show-Help` function
  - Both templates maintain feature parity with Python script generation
  - Enables reproducible, reversible system configurations
  - Safe testing with dry-run mode before making system changes

- **Python Install/Uninstall Script Generation**: Generate standalone Python 3.8+ scripts with full install/uninstall support
  - New `PythonBuilder` class for generating Python setup scripts
  - Python template (`templates/setup.py`) with data-driven architecture
  - New `--python` / `-y` CLI flag for Python script generation
  - **Clean Code Generation**: Uses data structures and functions instead of repetitive code
    - `DEFAULT_FILES` list for dotfiles (not hardcoded loops)
    - `CONFIG_FILES` list for config files
    - `SECTIONS` list of dicts for all installation sections
    - Single `install_section()` function that processes any section type
    - Single `uninstall_section()` function for removals
    - `copy_file_or_dir()` and `remove_file_or_dir()` helper functions
    - No code repetition - all logic is in reusable functions
  - Features:
    - Python 3.8+ compatible (standard library only)
    - argparse interface with `install` and `uninstall` commands
    - `--dry-run` and `--verbose` flags
    - Color-coded output with `Colors` class
    - Platform compatibility checking with warnings
    - Confirmation prompts for uninstall operations
    - Comprehensive error handling with try/except blocks
  - Support for all section types:
    - `debian_packages`: apt-get install/remove
    - `python_packages`: pip install/uninstall
    - `ruby_packages`: gem install/uninstall
    - `rust_packages`: cargo install/uninstall
    - `homebrew_packages`: brew install/uninstall
    - `shell`: Execute custom shell commands
  - Bidirectional setup management (install AND uninstall)
  - Default dotfiles and config files installation/removal
  - Version spec stripping in uninstall (handles `==`, `>=`, etc.)
  - 6 comprehensive test cases for PythonBuilder
  - Documentation in README.md and CLAUDE.md

- **Package Version Pinning**: Full support for version pinning across all package managers
  - New `PackageSpec` class for parsing package specifications with versions
  - Support for all major package manager syntaxes:
    - Python: `==`, `>=`, `<=`, `>`, `<`, `~=`, `!=` operators
    - Debian/Ubuntu: `=` operator with epoch support
    - Ruby: `:` separator for versions
    - Rust: `@` separator for versions
    - Winget: `==` operator with `--version` flag
    - Chocolatey: `==` operator with `--version=` flag
    - Homebrew: `@` separator for versions
  - Lockfile generation with `--lockfile` flag
  - JSON lockfiles include:
    - Timestamp of generation
    - Recipe metadata
    - All packages with name, version, operator, original spec
    - Organized by section
  - `generate_lockfile()` and `write_lockfile()` methods in Builder class
  - Example recipes: `ubuntu-pinned.yml`, `windows-pinned.yml`
  - 10 comprehensive test cases for parsing and lockfile generation
  - Enables reproducible installations across time and machines

- **Configuration Inheritance**: Full configuration field inheritance in recipe system
  - Child recipes now inherit all configuration fields from parent(s)
  - Inheritable fields: `name`, `config`, `platform`, `os`, `version`, `release`
  - Child values override parent values (child precedence)
  - Multiple inheritance supported with left-to-right precedence
  - Nested inheritance with recursive resolution (grandparent → parent → child)
  - Minimal child recipes possible (specify only `inherits` and `sections`)
  - New `_merge_configs()` method handles configuration merging with override rules
  - Example recipes demonstrating inheritance: `ubuntu-base.yml`, `ubuntu-dev.yml`, `ubuntu-24.04-dev.yml`
  - 5 comprehensive test cases covering all inheritance scenarios
  - Enables DRY recipes, recipe families, and better maintainability

## [0.2.0] - 2025-10-13

### Added

- **Windows Support**: Complete Windows platform support via PowerShell scripts
  - New `PowerShellBuilder` class for generating PowerShell setup scripts
  - PowerShell template (`templates/shell.ps1`) with Windows-specific features
  - Support for Windows Package Manager (winget)
  - Support for Chocolatey package manager with auto-installation
  - Three new section types: `winget_packages`, `chocolatey_packages`, `powershell`
  - Example recipes for Windows 11 and Windows 10
  - Administrator privilege checking in generated scripts
  - Windows-specific path handling (`%USERPROFILE%` instead of `$HOME`)

- **Comprehensive Test Suite**: Added pytest-based testing framework
  - 20+ test cases covering validation, loading, rendering, and error handling
  - Tests for recipe validation, inheritance, template rendering
  - Tests for dry-run mode, custom filters, and error scenarios
  - Makefile with `make test`, `make install`, and `make clean` targets
  - Added pytest to requirements.txt

- **Dry-run Mode**: New `--dry-run` / `-n` flag
  - Shows what would be done without executing commands
  - Displays file operations without creating files
  - Shows recipe structure and sections
  - Works with all builder types (Shell, PowerShell, Docker)

- **Recipe Validation**: Comprehensive validation system
  - Validates required recipe fields: name, platform, os, version, sections
  - Validates section structure and required fields
  - Validates section types against allowed values
  - Clear error messages with file paths and field names
  - Validation runs automatically on recipe load

- **New CLI Options**:
  - `--powershell` / `-p`: Generate PowerShell scripts for Windows
  - `--debug`: Enable debug-level logging
  - `--dry-run` / `-n`: Show commands without executing

### Deprecated

- **validate_dotfiles.py**: Standalone validation script deprecated in favor of integrated validation
  - Validation now built into start_vm.py via `--validate` flag
  - Standalone script still available for backwards compatibility
  - Only unique feature: `--max-age` option for custom age thresholds
  - Will be removed in future version
  - Displays deprecation warning when run

### Changed

- **CLI Arguments**: Recipe argument now optional when using `--validate` flag
  - Changed `recipe` from required (`nargs="+"`) to optional (`nargs="*"`)
  - Allows `python3 start_vm.py --validate` without specifying recipes
  - Error shown if recipes not provided for non-validate operations

- **Config Field Cleanup**: Removed config field from 9 recipes that referenced non-existent directories
  - Removed config field from: ubuntu-base, ubuntu-dev, ubuntu-24.04-dev, ubuntu-pinned
  - Removed config field from: focal, console (Linux recipes)
  - Removed config field from: windows10, windows11, windows-pinned (Windows recipes)
  - All remaining config field references now point to existing directories
  - See CONFIG_CLEANUP_COMPLETED.md for details

- **Error Handling**: Dramatically improved throughout codebase
  - YAML loading with specific error handling for FileNotFoundError and YAMLError
  - Template loading with Jinja2-specific error handling
  - File writing with OSError handling for setup directory creation
  - subprocess operations replaced os.system() calls
  - Section lookup validates existence before execution
  - Missing config/default directories handled gracefully with warnings

- **Security Improvements**:
  - Replaced all `os.system()` calls with `subprocess.run()` for better security
  - Replaced bare `except:` clause with specific exception types
  - Added input validation before command execution
  - Better error reporting with exit codes

- **Template Improvements**:
  - Shell template: Changed shebang from `#!/usr/bin/env sh` to `#!/usr/bin/env bash`
  - Shell template: Fixed variable quoting to prevent word splitting
  - Shell template: All variables now properly quoted with `${var}` syntax
  - Better POSIX compliance overall

- **Builder Class Enhancements**:
  - Added `VALID_SECTION_TYPES` class variable with all supported types
  - Added `REQUIRED_RECIPE_FIELDS` class variable
  - New `_validate_recipe()` method for comprehensive validation
  - Improved `_load_recipe_from_file()` with error handling
  - Updated `_get_recipe()` to handle missing directories gracefully
  - Enhanced `write_file()` with setup directory creation
  - Enhanced `build()` with template error handling

- **Logging System**:
  - DEBUG flag now configurable via `--debug` CLI argument instead of hardcoded
  - More informative log messages throughout
  - Warnings for non-critical issues (missing directories, format failures)
  - Errors for critical issues with proper exit codes

### Fixed

- **Python 3 Compatibility** (`default/bin/normalize.py`):
  - Fixed `hashlib.md5()` to accept bytes instead of string
  - Changed from `md5(str(datetime.now()))` to `md5(str(datetime.now()).encode())`

- **String Manipulation Bug** (`default/bin/normalize.py`):
  - Fixed incorrect use of `strip()` method which removes characters, not suffixes
  - Changed from `p.strip(HASH)` to `p[:-len(HASH)]` for proper suffix removal
  - Added conditional check with `endswith()` for safety

- **Recipe Data Error** (`recipes/focal.yml`):
  - Fixed release name from "disco" (19.04) to "focal" (20.04) to match version
  - Fixed config directory name to match release name

- **Section Validation**:
  - Fixed `run_section()` to validate section exists before running
  - Proper error messages and exit codes when section not found

### Security

- Replaced `os.system()` with `subprocess.run()` in all command execution paths
- Added specific exception handling instead of bare `except:` clauses
- Improved input validation for recipe files and sections
- Better error reporting to avoid information leakage

### Documentation

- Comprehensive Windows support section added to README.md
- Updated command-line usage documentation
- Updated CLAUDE.md with Windows support details
- Added example usage for Windows platform
- Documented all new section types
- Updated development setup instructions with test information
- Marked Windows support TODO as completed

## [0.1.1]

### Changed

- Minor improvements and bug fixes



## [0.1.0] - Previous Release

### Added

- Added support for Dockefile generation

- Added shell script generation from yaml specifications

- Initial project creation


