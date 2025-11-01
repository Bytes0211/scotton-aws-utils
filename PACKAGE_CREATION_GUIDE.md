# Python Package Creation Guide: scotton-aws-utils

This document details the complete process of creating the `scotton-aws-utils` Python package from existing `aws.py` and `util.py` files.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Creation Process](#step-by-step-creation-process)
4. [Package Structure](#package-structure)
5. [Installation Methods](#installation-methods)
6. [Testing the Package](#testing-the-package)
7. [Migrating Existing Projects](#migrating-existing-projects)
8. [Publishing (Optional)](#publishing-optional)
9. [Maintenance](#maintenance)

---

## Overview

**Package Name**: `scotton-aws-utils`  
**Version**: 1.0.0  
**Purpose**: Unified AWS operations package for S3, Lambda, EC2, IAM, and DynamoDB  
**Source Files**: `aws.py`, `util.py`, `lambdadeployer.py` from `aws-manager/resources/`

### Why Create a Package?

- ✅ **Reusability**: Install once, use in multiple projects
- ✅ **Version Control**: Track changes and maintain compatibility
- ✅ **Dependency Management**: Automatic handling of requirements
- ✅ **Easy Updates**: Update once, affects all projects
- ✅ **Professional Distribution**: Can be shared via PyPI or Git

---

## Prerequisites

### System Requirements
- Python >= 3.8
- pip >= 21.0
- setuptools >= 61.0

### Check Your Environment
```bash
python3 --version  # Should be >= 3.8
pip --version      # Should be >= 21.0
```

---

## Step-by-Step Creation Process

### Step 1: Create Package Directory Structure

```bash
cd ~/dev/projects
mkdir -p scotton-aws-utils/scotton_aws_utils
```

**Why this structure?**
- `scotton-aws-utils/` - Project root (with hyphens for PyPI)
- `scotton_aws_utils/` - Python package (with underscores for import)

### Step 2: Copy Source Files

```bash
# Copy the main modules
cp ~/dev/projects/aws-manager/resources/aws.py \
   ~/dev/projects/scotton-aws-utils/scotton_aws_utils/aws.py

cp ~/dev/projects/aws-manager/resources/util.py \
   ~/dev/projects/scotton-aws-utils/scotton_aws_utils/util.py

cp ~/dev/projects/aws-manager/resources/lambdadeployer.py \
   ~/dev/projects/scotton-aws-utils/scotton_aws_utils/lambdadeployer.py
```

### Step 3: Fix Package Imports

Edit `scotton_aws_utils/aws.py` to use relative imports:

**Before**:
```python
from resources import util, lambdadeployer  # type: ignore
```

**After**:
```python
from . import util, lambdadeployer
```

### Step 4: Add Missing Initialization

In `scotton_aws_utils/aws.py`, add `_lambda_deployer` to `__init__`:

```python
def __init__(self, use_local_dynamodb: bool = False) -> None:
    self._s3_client = None 
    self._s3_resource = None
    self._iam_client = None
    self._lambda_client = None
    self._lambda_deployer = None  # ← Add this line
    self._ec2_client = None
    self._ec2_resource = None
    self._dynamodb_client = None
    self._dynamodb_resource = None
    self._use_local_dynamodb = use_local_dynamodb
```

### Step 5: Create `__init__.py`

File: `scotton_aws_utils/__init__.py`

```python
"""
Scotton AWS Utilities
=====================

A Python package for AWS service operations including S3, Lambda, EC2, IAM, and DynamoDB.
"""

__version__ = '1.0.0'
__author__ = 'Scott On'

from .aws import Aws
from . import util
from . import lambdadeployer

__all__ = ['Aws', 'util', 'lambdadeployer']
```

### Step 6: Create `pyproject.toml`

File: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "scotton-aws-utils"
version = "1.0.0"
description = "A unified Python package for AWS service operations"
readme = "README.md"
authors = [
    {name = "Scott On"}
]
license = {text = "MIT"}
requires-python = ">=3.8"

dependencies = [
    "boto3>=1.26.0",
    "python-dotenv>=0.19.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "moto[dynamodb]>=5.0.0",
]

[tool.setuptools]
packages = ["scotton_aws_utils"]
```

### Step 7: Create README.md

Create a comprehensive README with:
- Installation instructions
- Quick start examples
- API reference
- Migration guide

(See full README.md in the package)

### Step 8: Create LICENSE

File: `LICENSE`

```
MIT License

Copyright (c) 2025 Scott On

Permission is hereby granted, free of charge...
(full MIT license text)
```

### Step 9: Create MANIFEST.in

File: `MANIFEST.in`

```
include README.md
include LICENSE
include pyproject.toml
recursive-include scotton_aws_utils *.py
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

---

## Package Structure

Final directory structure:

```
scotton-aws-utils/
├── scotton_aws_utils/
│   ├── __init__.py
│   ├── aws.py
│   ├── util.py
│   └── lambdadeployer.py
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
└── PACKAGE_CREATION_GUIDE.md (this file)
```

---

## Installation Methods

### Method 1: Editable Install (Recommended for Development)

```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

**Benefits**:
- Changes to source files immediately reflected
- No need to reinstall after edits
- Perfect for active development

### Method 2: Standard Install

```bash
cd ~/dev/projects/scotton-aws-utils
pip install .
```

### Method 3: Install with Dev Dependencies

```bash
pip install -e ".[dev]"
```

**Includes**: pytest, pytest-cov, moto, black, mypy, ruff

### Method 4: Uninstall

```bash
pip uninstall scotton-aws-utils
```

---

## Testing the Package

### Basic Import Test

```python
# test_import.py
from scotton_aws_utils import Aws, util
print("✅ Import successful!")
print(f"Aws: {Aws}")
print(f"util: {util}")
```

### Functionality Test

```python
# test_functionality.py
from scotton_aws_utils import Aws
from boto3.dynamodb.conditions import Key, Attr

# Test instantiation
aws = Aws()
print("✅ Aws instance created")

# Test conditions import
key_condition = Key('id').eq('test-123')
attr_condition = Attr('status').eq('active')
print("✅ DynamoDB conditions working")

# List methods
methods = [m for m in dir(aws) if not m.startswith('_')]
print(f"✅ {len(methods)} methods available")
```

### Run Tests

```bash
python3 test_import.py
python3 test_functionality.py
```

---

## Migrating Existing Projects

### Projects Using the Package

Identified projects:
1. `aws-manager` - Uses `resources.aws` and `resources.util`
2. `github-download` - Uses local `aws.py` and `util.py`

### Migration Steps for aws-manager

#### 1. Install Package in Project

```bash
cd ~/dev/projects/aws-manager
pip install -e ~/dev/projects/scotton-aws-utils
```

#### 2. Update Imports

**Before**:
```python
from resources.aws import Aws
from resources import util
```

**After**:
```python
from scotton_aws_utils import Aws
from scotton_aws_utils import util
```

#### 3. Update Test Files

Update `test_dynamodb.py`:

```python
# Before
from resources.aws import Aws

# After
from scotton_aws_utils import Aws
```

#### 4. Update Application Files

Update `aws_manager.py`:

```python
# Before
from resources.aws import Aws

# After
from scotton_aws_utils import Aws
```

#### 5. Test Project

```bash
cd ~/dev/projects/aws-manager
python3 aws_manager.py
# Or run tests
pytest test_dynamodb.py -v
```

### Migration Steps for github-download

#### 1. Install Package

```bash
cd ~/dev/projects/github-download
pip install -e ~/dev/projects/scotton-aws-utils
```

#### 2. Update github_function.py

**Before**:
```python
import util
import aws

boto = aws.Aws(
    util.get_s3_client(),
    util.get_s3_resource(),
    util.get_iam_client(),
    util.get_lambda_client()
)
```

**After**:
```python
from scotton_aws_utils import Aws, util

# The new Aws class initializes clients lazily
aws = Aws()
```

**Note**: The new `Aws` class doesn't require passing clients to the constructor. They're initialized lazily when first accessed.

#### 3. Remove Old Files (After Verification)

```bash
# Only after confirming everything works!
cd ~/dev/projects/github-download
rm aws.py util.py  # Backup first if needed
```

---

## Publishing (Optional)

### To PyPI

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI (requires account)
twine upload dist/*
```

### To GitHub/GitLab

```bash
cd ~/dev/projects/scotton-aws-utils
git init
git add .
git commit -m "Initial commit: scotton-aws-utils v1.0.0"
git remote add origin <your-repo-url>
git push -u origin main
```

Then install from Git:
```bash
pip install git+https://github.com/<username>/scotton-aws-utils.git
```

---

## Maintenance

### Updating the Package

#### 1. Make Changes

```bash
cd ~/dev/projects/scotton-aws-utils
# Edit files in scotton_aws_utils/
```

#### 2. Update Version

Edit `pyproject.toml` and `__init__.py`:
```python
__version__ = '1.1.0'  # Increment version
```

#### 3. Rebuild (if not using editable install)

```bash
pip install --upgrade .
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **1.0.0** → **1.0.1**: Bug fixes
- **1.0.0** → **1.1.0**: New features (backward compatible)
- **1.0.0** → **2.0.0**: Breaking changes

### Adding New Features

1. Add new methods to `scotton_aws_utils/aws.py` or `util.py`
2. Update `__all__` in `__init__.py` if adding new modules
3. Update `README.md` with new examples
4. Increment version
5. Reinstall/rebuild

### Updating Dependencies

Edit `pyproject.toml`:
```toml
dependencies = [
    "boto3>=1.28.0",  # Update version
    "python-dotenv>=1.0.0",
]
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'scotton_aws_utils'`

**Solution**:
```bash
pip install -e ~/dev/projects/scotton-aws-utils
```

### Relative Import Errors

**Problem**: `ImportError: attempted relative import with no known parent package`

**Solution**: Ensure `__init__.py` exists and uses correct relative imports (`from .`)

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'boto3'`

**Solution**:
```bash
pip install boto3 python-dotenv requests
# Or reinstall package
pip install -e ~/dev/projects/scotton-aws-utils
```

### Attribute Errors

**Problem**: `AttributeError: 'Aws' object has no attribute '_lambda_deployer'`

**Solution**: Ensure all `_private` attributes are initialized in `__init__()`

---

## Best Practices

### 1. Always Use Editable Install During Development
```bash
pip install -e .
```

### 2. Pin Dependencies for Production
```toml
dependencies = [
    "boto3==1.28.0",  # Exact version
]
```

### 3. Test Before Migrating
- Install package
- Test imports
- Run existing tests
- Verify functionality

### 4. Keep Backward Compatibility
- Don't remove methods
- Don't change signatures without deprecation
- Version bump appropriately

### 5. Document Changes
- Update README.md
- Update CHANGELOG (if you create one)
- Update version in multiple places

---

## Summary Checklist

- [x] Create package directory structure
- [x] Copy source files
- [x] Fix imports (relative imports)
- [x] Create `__init__.py`
- [x] Create `pyproject.toml`
- [x] Create README.md
- [x] Create LICENSE
- [x] Create MANIFEST.in
- [x] Install package (`pip install -e .`)
- [x] Test imports
- [x] Test functionality
- [ ] Migrate aws-manager project
- [ ] Migrate github-download project
- [ ] Test migrated projects
- [ ] Remove old files (optional)

---

## Next Steps

1. ✅ Package created and tested
2. **Install in aws-manager**
3. **Install in github-download**
4. **Update imports in both projects**
5. **Test both projects**
6. **(Optional) Publish to PyPI or Git**

---

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PEP 517/518 - Modern Python Packaging](https://peps.python.org/pep-0517/)
- [Semantic Versioning](https://semver.org/)

---

**Created**: 2025-10-31  
**Author**: Scott On  
**Package Version**: 1.0.0
