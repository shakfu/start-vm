# Dotfiles Validation Guide

This document explains how to use the built-in validation feature to audit and maintain the `config/` and `default/` directories.

**Note**: Validation is now integrated directly into `start_vm.py`. The standalone `validate_dotfiles.py` script is deprecated but still available for backwards compatibility.

## Purpose

The validation script helps identify:

1. **Orphaned config directories**: Config directories that exist but aren't referenced by any recipe
2. **Empty config directories**: Config directories that exist but contain no actual files (only `.keep`)
3. **Missing config directories**: Config directories referenced by recipes but don't exist
4. **Old/stale files**: Files that haven't been modified in over a year
5. **Platform-specific files**: Identifies which default files are platform-specific vs cross-platform
6. **Usage statistics**: File counts, sizes, modification dates for all dotfiles

## Usage

### Basic validation

```bash
python3 start_vm.py --validate
```

This generates a comprehensive report showing:
- Summary statistics
- Config directory usage by recipe
- Orphaned/empty config directories
- Old config directories and default files
- Cleanup recommendations

### Verbose mode

```bash
python3 start_vm.py --validate --verbose
# or short form:
python3 start_vm.py --validate -v
```

Shows additional statistics for each config directory:
- File count
- Total size in bytes
- Last modification date
- Age in days

### Legacy standalone script

The standalone script is still available but deprecated:

```bash
python3 validate_dotfiles.py              # basic mode
python3 validate_dotfiles.py --verbose    # verbose mode
python3 validate_dotfiles.py --max-age 180  # custom age threshold
```

**Note**: The `--max-age` option is not available in the integrated version (uses fixed 365 days threshold).

## Understanding the Report

### Config Directory Usage Section

```
CONFIG DIRECTORY USAGE
--------------------------------------------------------------------------------
✅ config/base/ -> used by 1 recipe(s): base
     Files: 120, Size: 303,146 bytes, Last modified: 2025-10-12 (0 days ago)
```

- **✅** = Directory exists and is referenced
- **❌** = Directory referenced but doesn't exist
- Shows which recipes use each config directory
- Verbose mode shows file stats

### Orphaned Config Directories

```
ORPHANED CONFIG DIRECTORIES
--------------------------------------------------------------------------------
⚠️  config/foo/ (42 files, 10,240 bytes, last modified 450 days ago)
```

These directories exist but no recipe references them. They may be:
- Left over from removed recipes
- Old configurations that are no longer needed
- Abandoned experiments

**Action**: Review for archival or removal.

### Empty Config Directories

```
EMPTY CONFIG DIRECTORIES
--------------------------------------------------------------------------------
⚠️  config/console/ (referenced by: prynth, terminal_tedium)
```

These directories exist but contain no actual configuration files (only `.keep` files).

**Action**: Either populate with actual config files or remove the config field from recipes.

### Old Files

```
OLD CONFIG DIRECTORIES (>1 year since modification)
--------------------------------------------------------------------------------
📅 config/jessie/ - Last modified: 2020-03-15 (1825 days ago) - Used by: jessie

OLD DEFAULT FILES (>1 year since modification)
--------------------------------------------------------------------------------
📅 .bashrc_old - Last modified: 2019-11-22 (2147 days ago)
```

Files that haven't been modified in over a year may be outdated or irrelevant for current OS versions.

**Action**: Review for updates or removal.

### Default Files Platform Analysis

```
DEFAULT FILES/DIRECTORIES
--------------------------------------------------------------------------------
LINUX:
  📄 .bashrc (9,275 bytes)
  📄 .xinitrc (329 bytes)

MACOS:
  📄 .bash_profile (1,234 bytes)

CROSS-PLATFORM:
  📄 .vimrc (1,933 bytes)
  📁 bin/ (20 files, 38,911 bytes)
```

Shows which files are platform-specific vs cross-platform based on naming patterns:
- **Linux indicators**: `.xinitrc`, `.gtkrc`, `.bashrc`, `i3`, `awesome`
- **macOS indicators**: `.bash_profile`, `Brewfile`
- **Windows indicators**: `.ps1`, `powershell`
- **Cross-platform**: Everything else (vim, git, etc.)

### Cleanup Recommendations

```
CLEANUP RECOMMENDATIONS
--------------------------------------------------------------------------------
1. Remove or archive 2 orphaned config directories
2. Remove 1 empty config directory
3. Review 1 config directory not modified in >1 year
```

Actionable summary of issues found.

## Typical Workflow

### 1. Regular Audits

Run validation monthly or quarterly:

```bash
python3 start_vm.py --validate > dotfiles_report.txt
```

Review the report and address any issues.

### 2. After Removing Recipes

After removing old recipes, check for orphaned config directories:

```bash
python3 start_vm.py --validate | grep "ORPHANED"
```

Archive or remove any orphaned directories:

```bash
# Archive orphaned config
mkdir -p archive/config
mv config/old-recipe archive/config/

# Or remove entirely
rm -rf config/old-recipe
```

### 3. Before Adding New Config Directories

Check if a config directory already exists:

```bash
python3 start_vm.py --validate | grep "config/myrecipe"
```

### 4. Identifying Stale Content

The integrated validation uses a fixed 365-day (1 year) threshold for identifying old files. To see which files haven't been modified in over a year:

```bash
python3 start_vm.py --validate | grep "📅"
```

For custom age thresholds (e.g., 2 years), use the standalone script:

```bash
python3 validate_dotfiles.py --max-age 730 | grep "📅"
```

## Integration with Repository Maintenance

### Recommended Schedule

- **Weekly**: Run basic validation during development
- **Monthly**: Review verbose output for storage/complexity issues
- **Quarterly**: Deep review of old files (>1 year)
- **Annually**: Major cleanup based on EOL OS versions

### Adding to CI/CD

You can add validation to your CI pipeline:

```bash
# Fail if there are orphaned or empty directories
python3 start_vm.py --validate | grep -q "⚠️" && exit 1 || exit 0
```

Or just report warnings without failing:

```bash
# Report issues but don't fail
python3 start_vm.py --validate
```

## Common Scenarios

### Scenario 1: Found Orphaned Config Directory

You removed `ubuntu-18.04.yml` but `config/bionic/` still exists.

**Solution**:
```bash
# Archive it
mkdir -p archive/config
mv config/bionic archive/config/

# Document in PRUNING_COMPLETED.md
```

### Scenario 2: Empty Config Directory Referenced by Recipe

`config/console/` exists but only has `.keep` file, yet `prynth.yml` references it.

**Options**:
1. **Remove config field**: Edit recipes to remove `config: console`
2. **Populate directory**: Add actual config files to `config/console/`

**Recommended**: Option 1 (remove config field) if no GUI configs are needed.

### Scenario 3: Config Directory Hasn't Been Updated in Years

`config/jessie/` last modified 2019, Debian 8 is EOL.

**Solution**:
1. Check if any recipes still reference it
2. If referenced, update the recipe to newer OS version
3. Archive the old config directory
4. Remove or update associated recipes

### Scenario 4: Platform-Specific File in Wrong Section

`.bash_profile` appears in Linux section but it's macOS-specific.

**Note**: The platform detection is heuristic-based. Files may be misclassified. Use the report as a guide, not absolute truth.

## What the Script Does NOT Check

This script does not:

1. **Validate file contents**: It doesn't check if config files are syntactically valid
2. **Check for broken symlinks**: Only checks file existence and age
3. **Detect duplicate content**: Doesn't identify identical files in different locations
4. **Test recipes**: Doesn't generate or test actual setup scripts
5. **Check git history**: Doesn't use git to determine last real modification

## Advanced Usage

### Filter for Specific Issues

```bash
# Only show orphaned directories
python3 start_vm.py --validate | awk '/ORPHANED/,/^$/'

# Only show cleanup recommendations
python3 start_vm.py --validate | awk '/CLEANUP RECOMMENDATIONS/,/^==/'

# Show only config directories
python3 start_vm.py --validate | awk '/CONFIG DIRECTORY USAGE/,/^$/'
```

### Export to JSON (Future Enhancement)

Currently the script outputs text. A future enhancement could add:

```bash
python3 validate_dotfiles.py --format json > report.json
```

### Automated Cleanup (Dangerous!)

**NOT RECOMMENDED** but possible:

```bash
# Remove all empty config directories (DANGEROUS - review first!)
python3 -c "
from validate_dotfiles import DotfilesValidator
v = DotfilesValidator()
v.load_recipes()
v.scan_config_dirs()
empty = v.find_empty_config_dirs()
for d in empty:
    print(f'Would remove: config/{d}/')
"
```

## Current Repository Status

As of the most recent validation (2025-10-13):

- **Total recipes**: 18
- **Recipes with config field**: 6
- **Config directories**: 6
- **Default files/directories**: 10
- **Issues**: 1 empty config directory (`config/console/`)

### Config Directory Mappings

| Config Dir | Used By | File Count | Size |
|------------|---------|------------|------|
| base/ | base | 120 | 303 KB |
| bookworm/ | bookworm | 67 | 147 KB |
| bullseye/ | bullseye-audio, bullseye-ttplus | 63 | 397 KB |
| buster/ | buster-audio | 63 | 397 KB |
| console/ | prynth, terminal_tedium | 0 | 0 (empty) |
| patchbox/ | patchbox | 63 | 397 KB |

## Related Documentation

- **PRUNING_RECOMMENDATION.md**: Analysis of old recipes to remove
- **PRUNING_COMPLETED.md**: Record of removed recipes
- **CONFIG_CLEANUP_COMPLETED.md**: Record of config field cleanup
- **RECIPE_SCHEMA.md**: Recipe file format specification

## Troubleshooting

### Script fails with YAML error

```
WARNING: Failed to load recipe.yml: ...
```

One of your recipe files has invalid YAML syntax. Fix the syntax and re-run.

### "Config directory not found" warning

The `config/` directory doesn't exist. This is fine if you don't use any recipes with config fields.

### Unexpected platform classification

The platform detection uses simple heuristics (filename patterns). Files may be misclassified. Review the actual file content to determine correct platform.

## Future Enhancements

Potential improvements to the validation script:

1. **JSON/CSV output**: Machine-readable formats for further processing
2. **Config content validation**: Parse and validate awesome/i3/conky configs
3. **Git integration**: Use git log to find truly last modified date
4. **Duplicate detection**: Find identical files across config directories
5. **Size alerts**: Warn if config directories exceed certain size thresholds
6. **Symlink validation**: Check for broken symlinks in default/
7. **Cross-reference default files**: Check which default files are actually used vs unused
8. **Recipe validation**: Validate that recipes actually reference files that exist

## Contributing

To improve the validation script:

1. Add new platform indicators to `check_default_files_platform_specific()`
2. Add new validation checks as methods in `DotfilesValidator`
3. Update report generation to include new checks
4. Update this documentation

---

**Last Updated**: 2025-10-13
**Script Version**: 1.0
