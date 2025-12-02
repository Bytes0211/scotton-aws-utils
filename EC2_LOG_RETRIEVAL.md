# EC2 Log Retrieval

This module provides functionality to retrieve CloudWatch logs from EC2 instances and save them to disk in various formats.

## Features

- **Multiple Output Formats**: Save logs as TXT, JSON, or CSV
- **Flexible Filtering**: Filter logs by pattern and time range
- **Batch Processing**: Retrieve logs from multiple instances
- **Automatic Discovery**: Finds all log groups associated with an instance
- **Error Handling**: Comprehensive error handling with meaningful messages

## Prerequisites

### CloudWatch Agent

For EC2 instances to send logs to CloudWatch, you must have the CloudWatch agent installed and configured on your instances. 

**Installation Guide**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html

**Quick Start**:
```bash
# Download and install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure agent (creates config file)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
```

### IAM Permissions

Your AWS credentials need the following CloudWatch Logs permissions:

- `logs:DescribeLogGroups`
- `logs:DescribeLogStreams`
- `logs:GetLogEvents`
- `logs:FilterLogEvents`

## Installation

```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

## Usage

### Basic Usage

#### As a Python Module

```python
from scotton_aws_utils import EC2LogRetriever

# Initialize retriever
retriever = EC2LogRetriever()

# Retrieve and save logs
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs',
    format='txt',
    num_events=1000
)

print(f"Status: {status}")
print(f"Result: {message}")
```

#### As a Command-Line Tool

```bash
# Basic usage - saves to ./ec2_logs directory as text
python -m scotton_aws_utils.ec2_log_retriever i-1234567890abcdef0

# Specify output path and format
python -m scotton_aws_utils.ec2_log_retriever i-1234567890abcdef0 \
    --output ./my_logs/ec2.json \
    --format json

# Get more events
python -m scotton_aws_utils.ec2_log_retriever i-1234567890abcdef0 \
    --num-events 5000

# Filter logs
python -m scotton_aws_utils.ec2_log_retriever i-1234567890abcdef0 \
    --filter-pattern "ERROR"

# Custom log group prefix
python -m scotton_aws_utils.ec2_log_retriever i-1234567890abcdef0 \
    --log-group-prefix "/custom/logs"
```

### Output Formats

#### Text Format (Default)
Human-readable format with timestamps and log groups:

```
EC2 CloudWatch Logs
================================================================================
Total Events: 150
Generated: 2025-12-01T02:30:00
================================================================================

[2025-12-01T02:15:00] [/aws/ec2/i-1234567890abcdef0/var/log/syslog] [stream-1]
Dec  1 02:15:00 ip-10-0-1-100 systemd[1]: Started Session 123 of user ubuntu.

[2025-12-01T02:15:05] [/aws/ec2/i-1234567890abcdef0/var/log/syslog] [stream-1]
Dec  1 02:15:05 ip-10-0-1-100 kernel: [UFW BLOCK] IN=eth0 OUT=...
```

#### JSON Format
Structured data for programmatic processing:

```json
{
  "metadata": {
    "total_events": 150,
    "generated_at": "2025-12-01T02:30:00"
  },
  "events": [
    {
      "timestamp": 1701394500000,
      "timestamp_iso": "2025-12-01T02:15:00",
      "logGroup": "/aws/ec2/i-1234567890abcdef0/var/log/syslog",
      "logStreamName": "stream-1",
      "message": "Dec  1 02:15:00 ip-10-0-1-100 systemd[1]: Started Session 123..."
    }
  ]
}
```

#### CSV Format
Spreadsheet-compatible format:

```csv
timestamp,timestamp_iso,log_group,log_stream,message
1701394500000,2025-12-01T02:15:00,/aws/ec2/i-1234567890abcdef0/var/log/syslog,stream-1,"Dec  1 02:15:00..."
```

### Advanced Examples

#### Time-Based Filtering

```python
from datetime import datetime, timedelta
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()

# Get logs from last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs/last_24h.json',
    format='json',
    start_time=int(start_time.timestamp() * 1000),
    end_time=int(end_time.timestamp() * 1000),
    num_events=5000
)
```

#### Pattern Filtering

```python
# Get only ERROR logs
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs/errors.txt',
    filter_pattern='ERROR',
    num_events=1000
)

# Complex filter pattern (CloudWatch Logs syntax)
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs/filtered.txt',
    filter_pattern='[time, request_id, event_type = ERROR*, ...]',
    num_events=1000
)
```

#### Multiple Instances

```python
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()

instance_ids = [
    'i-1234567890abcdef0',
    'i-0987654321fedcba0',
    'i-abcdef1234567890'
]

results = retriever.retrieve_logs_for_multiple_instances(
    instance_ids=instance_ids,
    output_dir='./logs/all_instances',
    format='json',
    num_events=1000
)

# Check results
for instance_id, (status, message) in results.items():
    print(f"{instance_id}: {status} - {message}")
```

#### Custom Log Group Prefix

```python
# If your CloudWatch agent uses a custom configuration
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs/custom.txt',
    log_group_prefix='/myapp/logs/ec2',  # Custom prefix
    num_events=1000
)
```

#### Reusing AWS Client

```python
from scotton_aws_utils import Aws, EC2LogRetriever

# Create AWS client once
aws = Aws()

# Reuse for multiple operations
retriever = EC2LogRetriever(aws_client=aws)

status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs',
    num_events=1000
)
```

## API Reference

### EC2LogRetriever Class

#### `__init__(aws_client=None)`
Initialize the retriever.

**Parameters**:
- `aws_client` (Aws, optional): Reuse existing Aws client instance

#### `retrieve_and_save_logs(instance_id, output_path, ...)`
Retrieve logs from an EC2 instance and save to disk.

**Parameters**:
- `instance_id` (str): EC2 instance ID (e.g., 'i-1234567890abcdef0')
- `output_path` (str): File path or directory for saving logs
- `log_group_prefix` (str): CloudWatch log group prefix (default: '/aws/ec2')
- `num_events` (int): Max events to retrieve (default: 1000)
- `format` (str): Output format - 'txt', 'json', or 'csv' (default: 'txt')
- `filter_pattern` (str): CloudWatch filter pattern (default: '')
- `start_time` (int, optional): Start timestamp in milliseconds since epoch
- `end_time` (int, optional): End timestamp in milliseconds since epoch

**Returns**:
- `tuple`: (status_code, message) where status_code is:
  - `200`: Success
  - `404`: No log groups found
  - `500`: Error occurred

#### `retrieve_logs_for_multiple_instances(instance_ids, output_dir, **kwargs)`
Retrieve logs for multiple EC2 instances.

**Parameters**:
- `instance_ids` (list): List of EC2 instance IDs
- `output_dir` (str): Directory where logs should be saved
- `**kwargs`: Additional arguments passed to retrieve_and_save_logs

**Returns**:
- `dict`: Mapping of instance_id to (status_code, message) tuple

## Troubleshooting

### No log groups found

**Error**: `⚠️  No log groups found for EC2 instance 'i-xxx' with prefix '/aws/ec2'`

**Possible causes**:
1. CloudWatch agent not installed on the instance
2. CloudWatch agent not running
3. Agent configured with different log group prefix
4. IAM role on EC2 instance lacks CloudWatch permissions

**Solutions**:
```bash
# Check if CloudWatch agent is running
sudo systemctl status amazon-cloudwatch-agent

# Check agent logs
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log

# Verify IAM role has CloudWatchAgentServerPolicy
aws iam list-attached-role-policies --role-name YourEC2Role
```

### No events found

**Error**: `📭 No log events found for instance 'i-xxx'`

**Possible causes**:
1. Logs exist but outside the time range filter
2. Filter pattern excludes all logs
3. Instance recently started and hasn't generated logs

**Solutions**:
- Remove time range filters to see all logs
- Use an empty filter pattern first: `filter_pattern=''`
- Check CloudWatch console to verify logs exist

### Permission denied

**Error**: `❌ Error retrieving EC2 logs: AccessDeniedException - ...`

**Solution**: Add CloudWatch Logs permissions to your AWS credentials:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ],
    "Resource": "*"
  }]
}
```

## CloudWatch Filter Pattern Syntax

CloudWatch Logs uses a specific filter pattern syntax. Here are some examples:

```python
# Match exact text
filter_pattern='ERROR'

# Match any of multiple terms
filter_pattern='ERROR WARNING CRITICAL'

# Structured logs (space-delimited)
filter_pattern='[time, request_id, event_type = ERROR*, status_code, ...]'

# JSON logs
filter_pattern='{ $.level = "ERROR" }'

# Numeric comparisons (JSON)
filter_pattern='{ $.response_time > 1000 }'

# Multiple conditions (JSON)
filter_pattern='{ $.level = "ERROR" && $.status_code >= 500 }'
```

For more details: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

## Integration with Existing Package

The EC2LogRetriever integrates seamlessly with existing scotton-aws-utils functionality:

```python
from scotton_aws_utils import Aws, EC2LogRetriever

# Use AWS class to list instances
aws = Aws()
aws.list_ec2s()

# Use same client for log retrieval
retriever = EC2LogRetriever(aws_client=aws)
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs'
)

# Access low-level CloudWatch Logs API if needed
log_groups = aws.get_log_groups('/aws/ec2')
events = aws.get_log_events(
    log_group_name='/aws/ec2/i-xxx/var/log/syslog',
    log_stream_name='stream-1',
    limit=100
)
```

## See Also

- [Main README](README.md) - Package overview and installation
- [Examples](examples/ec2_log_retrieval_example.py) - More code examples
- [AWS CloudWatch Logs Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [CloudWatch Agent Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html)
