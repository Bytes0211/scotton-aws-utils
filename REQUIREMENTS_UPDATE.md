# Requirements.txt Update Guide

## Overview

The `requirements.txt` files in both `aws-manager` and `github-download` have been updated to include the `scotton-aws-utils` package. This ensures consistent package installation across development environments.

---

## What Was Updated

### 1. aws-manager/requirements.txt

**Location**: `~/dev/projects/aws-manager/requirements.txt`

**Added**:
```
# Scotton AWS Utilities Package
-e file:///home/scotton/dev/projects/scotton-aws-utils
```

**Position**: Top of file (before other dependencies)

### 2. github-download/requirements.txt

**Location**: `~/dev/projects/github-download/requirements.txt`

**Added**:
```
# Scotton AWS Utilities Package (for local development)
# Note: For Lambda deployment, package dependencies will be bundled
-e file:///home/scotton/dev/projects/scotton-aws-utils
```

**Position**: After header comments, before AWS libraries

---

## Why Use `-e` (Editable Install)?

The `-e` flag installs the package in "editable" or "development" mode:

### Benefits:
- ✅ **Live Updates**: Changes to the package source are immediately available
- ✅ **No Reinstall**: Don't need to reinstall after package updates
- ✅ **Local Development**: Perfect for active development
- ✅ **Same Code**: All projects use the exact same code

### How It Works:
Instead of copying the package to `site-packages`, pip creates a link to the source directory. Any changes you make to files in `~/dev/projects/scotton-aws-utils/` are immediately reflected in all projects.

---

## Installation Commands

### Fresh Installation (New Environment)

**For aws-manager**:
```bash
cd ~/dev/projects/aws-manager
pip install -r requirements.txt
```

**For github-download**:
```bash
cd ~/dev/projects/github-download
pip install -r requirements.txt
```

### Verify Installation

```bash
python3 -c "from scotton_aws_utils import Aws; print('✅ Package installed')"
```

---

## For New Developers / CI/CD

When a new developer clones the projects or in a CI/CD pipeline:

```bash
# Clone the projects
git clone <repo-url> aws-manager
git clone <repo-url> github-download
git clone <repo-url> scotton-aws-utils

# Install dependencies (package will be automatically installed)
cd aws-manager
pip install -r requirements.txt

cd ../github-download  
pip install -r requirements.txt
```

The `-e file://` syntax will work as long as the `scotton-aws-utils` directory exists at the specified path.

---

## Alternative: Install from Git (Future)

If you later push `scotton-aws-utils` to a Git repository, you can update requirements.txt to:

```
# Install from Git repository
-e git+https://github.com/<username>/scotton-aws-utils.git#egg=scotton-aws-utils
```

Or for a specific branch/tag:
```
-e git+https://github.com/<username>/scotton-aws-utils.git@v1.0.0#egg=scotton-aws-utils
```

---

## Special Note: Lambda Deployment

### For github-download Lambda Functions

The `requirements.txt` includes `scotton-aws-utils` for **local development only**.

For Lambda deployment, you have two options:

### Option 1: Bundle Package Dependencies (Current)
When creating the Lambda deployment package, include the `scotton_aws_utils` package in the zip file:

```bash
# Install package to local directory
pip install -e ~/dev/projects/scotton-aws-utils -t ./package

# Create deployment zip
zip -r github_function.zip github_function.py package/
```

### Option 2: Use Lambda Layers (Recommended for Production)
Create a Lambda Layer with `scotton-aws-utils`:

```bash
# Create layer directory structure
mkdir -p lambda-layer/python

# Install package to layer
pip install ~/dev/projects/scotton-aws-utils -t lambda-layer/python/

# Create layer zip
cd lambda-layer
zip -r scotton-aws-utils-layer.zip python/
```

Then attach the layer to your Lambda function.

---

## Updating the Package Version

If you want to pin to a specific version (after publishing to PyPI):

**Standard install**:
```
scotton-aws-utils==1.0.0
```

**Latest version**:
```
scotton-aws-utils>=1.0.0
```

**Local editable (current)**:
```
-e file:///home/scotton/dev/projects/scotton-aws-utils
```

---

## Troubleshooting

### Issue: "No such file or directory" error

**Problem**: The path to scotton-aws-utils is incorrect or the package doesn't exist.

**Solution**:
```bash
# Verify the package exists
ls -la ~/dev/projects/scotton-aws-utils/

# If missing, clone or create the package
cd ~/dev/projects
git clone <repo-url> scotton-aws-utils  # If in Git
# OR
# Recreate the package directory
```

### Issue: Package changes not reflected

**Problem**: Changes to package source aren't showing up.

**Solution**:
```bash
# Verify editable install
pip list | grep scotton-aws-utils
# Should show: scotton-aws-utils 1.0.0 /home/scotton/dev/projects/scotton-aws-utils

# If not editable, reinstall
pip install -e ~/dev/projects/scotton-aws-utils
```

### Issue: Import errors in production

**Problem**: Lambda or production environment can't find the package.

**Solution**:
- For Lambda: Include package in deployment zip or use Lambda Layers
- For production servers: Install from PyPI or Git repository
- Never use `-e file://` in production requirements

---

## Best Practices

### Development
✅ **DO**: Use `-e file://` for local development
✅ **DO**: Keep package path absolute
✅ **DO**: Document the package location

### Production
✅ **DO**: Use versioned packages (`==1.0.0`)
✅ **DO**: Install from PyPI or private package repository
✅ **DO**: Pin exact versions for reproducibility

❌ **DON'T**: Use `-e file://` in production
❌ **DON'T**: Use relative paths
❌ **DON'T**: Mix development and production requirements

---

## Verification Checklist

After updating requirements.txt:

- [x] Package path is correct (`file:///home/scotton/dev/projects/scotton-aws-utils`)
- [x] Package can be installed (`pip install -r requirements.txt`)
- [x] Imports work (`from scotton_aws_utils import Aws`)
- [x] Projects run correctly
- [x] Tests pass (if applicable)

---

## Summary

**What Changed**:
- ✅ Added `scotton-aws-utils` to aws-manager requirements.txt
- ✅ Added `scotton-aws-utils` to github-download requirements.txt
- ✅ Used editable install (`-e`) for development workflow
- ✅ Documented Lambda deployment considerations

**Benefits**:
- Consistent package installation across environments
- Automatic dependency resolution
- Easy onboarding for new developers
- Version control of dependencies

**Status**: ✅ Complete and tested

---

**Updated**: 2025-10-31  
**Package Version**: 1.0.0
