# Scotton AWS Utilities

A comprehensive Python package for AWS service operations, providing a unified interface for S3, Lambda, EC2, IAM, and DynamoDB operations with simplified error handling and best practices built-in.

## Features

- **S3 Operations**: Bucket management, file uploads/downloads, versioning
- **Lambda Functions**: Invoke, update code, manage configurations
- **EC2 Management**: Create, start, stop, and manage EC2 instances
- **IAM Operations**: Role validation and management
- **DynamoDB**: Full CRUD operations, queries, scans, batch operations, transactions
- **Advanced DynamoDB**: Key/Attr condition builders, streams, GSI/LSI support
- **Unified Error Handling**: Consistent error handling across all services
- **Local DynamoDB Support**: Easy testing with DynamoDB Local

## Installation

### From Source (Editable Mode for Development)

```bash
# Clone or navigate to the package directory
cd ~/dev/projects/scotton-aws-utils

# Install in editable mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### From Source (Standard Installation)

```bash
cd ~/dev/projects/scotton-aws-utils
pip install .
```

### From Git Repository (if published)

```bash
pip install git+https://github.com/Bytes0211/scotton-aws-utils.git
```

## Quick Start

```python
from scotton_aws_utils import Aws

# Initialize AWS client
aws = Aws()

# S3 Operations
aws.list_buckets()
aws.add_file_to_bucket('my-bucket', 'file.txt', 'uploaded-file.txt')

# Lambda Operations
aws.list_functions()
response = aws.invoke_function('my-function', {'key': 'value'})

# DynamoDB Operations
aws.create_dynamodb_table(
    table_name='MyTable',
    key_schema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
    attribute_definitions=[{'AttributeName': 'id', 'AttributeType': 'S'}]
)

# DynamoDB with Key/Attr conditions
from boto3.dynamodb.conditions import Key, Attr

items = aws.query_dynamodb(
    table_name='Orders',
    key_condition_expression=Key('customer_id').eq('CUST-123'),
    filter_expression=Attr('status').eq('completed')
)

# EC2 Operations
aws.list_ec2s()
status, instance_ids = aws.create_ec2(image_id='ami-12345678')
```

## Advanced DynamoDB Features

### Query with Conditions

```python
from scotton_aws_utils import Aws
from boto3.dynamodb.conditions import Key, Attr

aws = Aws()

# Query with complex conditions
orders = aws.query_dynamodb(
    table_name='Orders',
    key_condition_expression=Key('customer_id').eq('CUST-123') & 
                            Key('order_date').begins_with('2025'),
    filter_expression=Attr('total').gt(100),
    scan_index_forward=False,  # Most recent first
    limit=50
)
```

### Conditional Updates

```python
# Update only if condition is met
aws.update_item_dynamodb(
    table_name='Inventory',
    key={'id': 'item-123'},
    update_expression='SET stock = stock - :qty',
    expression_attribute_values={':qty': 5, ':min': 0},
    condition_expression='stock >= :min'
)
```

### Atomic Transactions

```python
# All operations succeed or all fail
transaction = [
    {
        'Put': {
            'TableName': 'Orders',
            'Item': {'id': {'S': 'order-1'}, 'total': {'N': '100'}}
        }
    },
    {
        'Update': {
            'TableName': 'Inventory',
            'Key': {'product_id': {'S': 'prod-1'}},
            'UpdateExpression': 'SET stock = stock - :qty',
            'ExpressionAttributeValues': {':qty': {'N': '1'}}
        }
    }
]

status, response = aws.transact_write_dynamodb(transaction)
```

### Batch Operations

```python
# Batch get multiple items
keys = [{'id': 'item-1'}, {'id': 'item-2'}, {'id': 'item-3'}]
items = aws.batch_get_dynamodb('Products', keys)

# Batch write multiple items
items = [
    {'id': 'item-1', 'name': 'Product 1'},
    {'id': 'item-2', 'name': 'Product 2'}
]
aws.batch_write_dynamodb('Products', items)
```

## Local DynamoDB Support

```python
# Connect to local DynamoDB for testing
aws = Aws(use_local_dynamodb=True)

# All DynamoDB operations now use localhost:8000
aws.create_dynamodb_table(...)
aws.put_item_dynamodb(...)
```

## Utility Functions

```python
from scotton_aws_utils import util

# Get AWS clients
s3_client = util.get_s3_client()
lambda_client = util.get_lambda_client()
dynamodb_client = util.get_dynamodb_client()
dynamodb_resource = util.get_dynamodb_resource()

# With custom region/endpoint
dynamodb_client = util.get_dynamodb_client(
    region_name='us-west-2',
    endpoint_url='http://localhost:8000'
)

# Environment variables
app_name = util.get_appName()
env = util.get_env()
```

## Configuration

The package uses environment variables for configuration. Create a `.env` file:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Application-specific
env=development
appName=my-app
```

## Requirements

- Python >= 3.8
- boto3 >= 1.26.0
- python-dotenv >= 0.19.0
- requests >= 2.28.0

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=scotton_aws_utils --cov-report=html
```

## API Reference

### Main Classes

#### `Aws`
Main class for AWS operations with lazy-initialized clients.

**Constructor**:
- `Aws(use_local_dynamodb=False)`: Initialize with optional local DynamoDB support

**S3 Methods**:
- `create_bucket(bucket_prefix)`: Create S3 bucket
- `list_buckets()`: List all buckets
- `add_file_to_bucket(bucket_name, file_name, object_name, url=None)`: Upload file
- `delete_files_from_bucket(bucket_name, file_list)`: Delete multiple files
- `enable_bucket_versioning(bucket_name)`: Enable versioning

**Lambda Methods**:
- `list_functions()`: List Lambda functions
- `invoke_function(function_name, function_params, get_log=False)`: Invoke function
- `update_function_code(function_name, deployment_package)`: Update code
- `update_function_configuration(function_name, env_vars)`: Update configuration

**DynamoDB Methods**:
- `create_dynamodb_table(...)`: Create table with GSI/LSI/streams support
- `put_item_dynamodb(table_name, item)`: Insert/update item
- `get_item_dynamodb(table_name, key)`: Get item by key
- `update_item_dynamodb(table_name, key, update_expression, ...)`: Update with conditions
- `delete_item_dynamodb(table_name, key)`: Delete item
- `query_dynamodb(table_name, key_condition_expression, ...)`: Query with Key/Attr
- `scan_dynamodb(table_name, filter_expression, ...)`: Scan with filters
- `batch_get_dynamodb(table_name, keys)`: Batch get up to 100 items
- `batch_write_dynamodb(table_name, items)`: Batch write up to 25 items
- `transact_write_dynamodb(transact_items)`: Atomic transactions
- `list_dynamodb_tables()`: List all tables
- `delete_dynamodb_table(table_name)`: Delete table
- `get_table_schema(table_name)`: Get table schema
- `copy_table_to_aws(source_table_name, destination_table_name)`: Migrate table

**EC2 Methods**:
- `create_ec2(image_id, ...)`: Create EC2 instance
- `list_ec2s()`: List all instances
- `start_ec2(instance_ids)`: Start instances
- `stop_ec2(instance_ids)`: Stop instances
- `remove_ec2s(instance_ids)`: Terminate instances

**IAM Methods**:
- `list_iam_roles()`: List IAM roles
- `validate_iam_role(role)`: Validate role exists

## Migration Guide

### From Local aws.py/util.py

If you're migrating from local `aws.py` and `util.py` files:

**Before**:
```python
from resources.aws import Aws
import resources.util as util
```

**After**:
```python
from scotton_aws_utils import Aws
from scotton_aws_utils import util
```

## License

MIT License

## Author

Scott On

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Version 1.0.0 (2025-10-31)
- Initial release
- Full S3, Lambda, EC2, IAM, DynamoDB support
- Advanced DynamoDB features (Key/Attr conditions, transactions, batch operations)
- Local DynamoDB support
- Comprehensive test coverage
- Documentation and examples
