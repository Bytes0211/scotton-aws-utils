# EC2 CloudWatch Log Retrieval Tools

Complete toolkit for retrieving CloudWatch logs from EC2 instances with multiple interfaces and formats.

## Overview

This repository provides **three ways** to retrieve EC2 CloudWatch logs:

1. **Python Script** (`get-ec2-logs.py`) - Quick, interactive Python script
2. **Bash Script** (`get_ec2_logs.sh`) - Full-featured bash script with extensive validation
3. **Python Module** (`EC2LogRetriever`) - Programmatic access via scotton-aws-utils package

## Quick Start

### Python Script (Simplest)

```bash
cd ~/dev/projects/scotton-aws-utils
python get-ec2-logs.py
# Follow the prompts
```

### Bash Script (Most User-Friendly)

```bash
cd ~/dev/projects/scotton-aws-utils
./get_ec2_logs.sh
# Interactive prompts with colored output
```

### Python Module (Most Flexible)

```python
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs',
    format='json'
)
```

## Files in This Repository

### Scripts
- **`get-ec2-logs.py`** - Python script with CLI arguments and interactive mode
- **`get_ec2_logs.sh`** - Bash script with extensive validation and error handling

### Python Module
- **`scotton_aws_utils/ec2_log_retriever.py`** - Core EC2LogRetriever class
- **`scotton_aws_utils/aws.py`** - Base Aws class with CloudWatch Logs methods

### Examples
- **`examples/ec2_log_retrieval_example.py`** - Comprehensive Python examples

### Documentation
- **`GET_EC2_LOGS_README.md`** - Documentation for get-ec2-logs.py
- **`BASH_SCRIPT_USAGE.md`** - Documentation for get_ec2_logs.sh
- **`EC2_LOG_RETRIEVAL.md`** - Documentation for EC2LogRetriever module
- **`EC2_LOGS_README.md`** - This file (overview)

## Comparison: Which Tool Should I Use?

| Feature | get-ec2-logs.py | get_ec2_logs.sh | EC2LogRetriever |
|---------|----------------|-----------------|-----------------|
| **Best For** | Quick scripts | System admin tasks | Custom applications |
| **Language** | Python | Bash | Python (library) |
| **Prerequisites** | Python, package | Bash, AWS CLI, Python | Python, package |
| **Interactive Mode** | ✅ Yes | ✅ Yes | ❌ No (programmatic) |
| **Validation** | Format only | Format + AWS API | Internal |
| **Max Attempts** | Unlimited | 3 attempts | N/A |
| **Error Messages** | Good | Excellent | Programmatic |
| **Config Prompts** | No | Yes | No (code) |
| **Colored Output** | Minimal | Extensive | Console only |
| **Automation** | ✅ Excellent | ✅ Good | ✅ Excellent |
| **Custom Logic** | Limited | Limited | ✅ Full control |

## Use Cases

### Use get-ec2-logs.py when:
- You need a quick log retrieval with minimal setup
- You want command-line arguments for automation
- You prefer Python over bash
- You need interactive prompts for instance ID

**Example:**
```bash
python get-ec2-logs.py -i i-1234567890abcdef0 -f json -n 2000
```

### Use get_ec2_logs.sh when:
- You prefer bash scripting
- You want extensive validation (3 attempts with AWS API checks)
- You want detailed colored output and configuration prompts
- You're doing system administration tasks

**Example:**
```bash
./get_ec2_logs.sh
# Prompts for configuration and instance ID
```

### Use EC2LogRetriever when:
- You're building a Python application
- You need programmatic access
- You want to process logs in memory
- You need to integrate with other Python code
- You're retrieving logs for multiple instances

**Example:**
```python
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()

# Process multiple instances
instances = ['i-xxx', 'i-yyy', 'i-zzz']
results = retriever.retrieve_logs_for_multiple_instances(
    instance_ids=instances,
    output_dir='./logs',
    format='json'
)
```

## Installation

### Prerequisites

All tools require:
1. **AWS credentials** configured
2. **CloudWatch Logs permissions** (logs:DescribeLogGroups, logs:GetLogEvents, etc.)
3. **CloudWatch agent** installed on EC2 instances

### Install scotton-aws-utils Package

```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

### Verify Installation

```bash
# Test Python import
python -c "from scotton_aws_utils import EC2LogRetriever; print('✅ Package installed')"

# Test scripts are executable
ls -l get-ec2-logs.py get_ec2_logs.sh
```

## Common Workflows

### Workflow 1: Quick Interactive Retrieval

```bash
# Use Python script for quick interactive retrieval
python get-ec2-logs.py
# Enter instance ID when prompted
# Logs saved to ./ec2_logs/
```

### Workflow 2: Scheduled Log Collection

```bash
#!/bin/bash
# cron-retrieve-logs.sh

INSTANCES=("i-xxx" "i-yyy" "i-zzz")
OUTPUT_DIR="/var/logs/ec2/$(date +%Y%m%d)"

for instance in "${INSTANCES[@]}"; do
    python get-ec2-logs.py \
        -i "$instance" \
        -o "$OUTPUT_DIR" \
        -f json \
        -n 5000
done
```

Add to crontab:
```bash
# Retrieve logs daily at 2 AM
0 2 * * * /path/to/cron-retrieve-logs.sh
```

### Workflow 3: Log Analysis Pipeline

```python
from scotton_aws_utils import EC2LogRetriever
import json

# Retrieve logs
retriever = EC2LogRetriever()
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./temp_logs.json',
    format='json',
    filter_pattern='ERROR'
)

# Analyze logs
if status == 200:
    with open('./temp_logs.json') as f:
        data = json.load(f)
        errors = [e for e in data['events'] if 'ERROR' in e['message']]
        print(f"Found {len(errors)} errors")
        
        # Process errors...
```

### Workflow 4: Multi-Region Retrieval

```bash
#!/bin/bash
# retrieve-all-regions.sh

REGIONS=("us-east-1" "us-west-2" "eu-west-1")
INSTANCE_ID="i-1234567890abcdef0"

for region in "${REGIONS[@]}"; do
    echo "Retrieving logs from $region..."
    AWS_DEFAULT_REGION=$region python get-ec2-logs.py \
        -i "$INSTANCE_ID" \
        -o "./logs/$region" \
        -f json
done
```

## Output Formats

All tools support three output formats:

### TXT (Human-Readable)
```
[2025-12-01T02:30:00] [/aws/ec2/i-xxx/var/log/syslog] [stream-1]
Dec  1 02:30:00 ip-10-0-1-100 systemd[1]: Started Session 123.
```

**Best for:** Manual review, grep searches, text processing

### JSON (Structured)
```json
{
  "metadata": {"total_events": 850, "generated_at": "2025-12-01T02:45:00"},
  "events": [
    {
      "timestamp": 1701394200000,
      "timestamp_iso": "2025-12-01T02:30:00",
      "logGroup": "/aws/ec2/i-xxx/var/log/syslog",
      "message": "Dec  1 02:30:00..."
    }
  ]
}
```

**Best for:** Programmatic processing, APIs, data pipelines

### CSV (Tabular)
```csv
timestamp,timestamp_iso,log_group,log_stream,message
1701394200000,2025-12-01T02:30:00,/aws/ec2/i-xxx/var/log/syslog,stream-1,"Dec  1..."
```

**Best for:** Excel, data analysis, reporting

## Troubleshooting

### Issue: No log groups found

**Cause:** CloudWatch agent not installed or not running on EC2 instance

**Solution:**
```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Check agent status
sudo systemctl status amazon-cloudwatch-agent

# Install if needed
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Issue: Permission denied

**Cause:** Missing AWS permissions

**Solution:** Add these IAM permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:GetLogEvents",
      "logs:FilterLogEvents",
      "ec2:DescribeInstances"
    ],
    "Resource": "*"
  }]
}
```

### Issue: Wrong region

**Cause:** Instance exists in different region

**Solution:**
```bash
# Check current region
aws configure get region

# Set correct region
aws configure set region us-east-1

# Or use environment variable
AWS_DEFAULT_REGION=us-west-2 python get-ec2-logs.py -i i-xxx
```

## Advanced Features

### Filter Patterns

All tools support CloudWatch filter patterns:

```bash
# Simple text match
python get-ec2-logs.py -i i-xxx --filter-pattern "ERROR"

# Structured log matching
python get-ec2-logs.py -i i-xxx --filter-pattern "[time, request_id, level = ERROR*, ...]"

# JSON log matching
python get-ec2-logs.py -i i-xxx --filter-pattern '{ $.level = "ERROR" }'
```

### Time Range Filtering

```python
from datetime import datetime, timedelta
from scotton_aws_utils import EC2LogRetriever

end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

retriever = EC2LogRetriever()
retriever.retrieve_and_save_logs(
    instance_id='i-xxx',
    output_path='./logs',
    start_time=int(start_time.timestamp() * 1000),
    end_time=int(end_time.timestamp() * 1000)
)
```

### Custom Log Group Prefix

```bash
# If your CloudWatch agent uses custom prefix
python get-ec2-logs.py \
    -i i-xxx \
    --log-group-prefix "/custom/application/logs"
```

## Documentation Links

- **[GET_EC2_LOGS_README.md](GET_EC2_LOGS_README.md)** - Python script (get-ec2-logs.py) documentation
- **[BASH_SCRIPT_USAGE.md](BASH_SCRIPT_USAGE.md)** - Bash script (get_ec2_logs.sh) documentation
- **[EC2_LOG_RETRIEVAL.md](EC2_LOG_RETRIEVAL.md)** - EC2LogRetriever module documentation
- **[README.md](README.md)** - Main package documentation

## Examples

See **[examples/ec2_log_retrieval_example.py](examples/ec2_log_retrieval_example.py)** for 9 comprehensive examples covering:
- Basic usage
- Different output formats
- Filtering by pattern
- Time range queries
- Multiple instances
- Custom log groups
- Error handling

## Contributing

This is part of the scotton-aws-utils package. For issues or feature requests related to EC2 log retrieval, please ensure you specify which tool you're using (Python script, bash script, or module).

## License

MIT License - See main package LICENSE file

## Author

Scott On

---

**Quick Reference:**

- Interactive log retrieval: `python get-ec2-logs.py` or `./get_ec2_logs.sh`
- Command-line retrieval: `python get-ec2-logs.py -i i-xxx -f json`
- Programmatic access: `from scotton_aws_utils import EC2LogRetriever`
