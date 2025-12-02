# get-ec2-logs.py

A Python script for retrieving CloudWatch logs from EC2 instances with interactive prompts and command-line options.

## Overview

`get-ec2-logs.py` provides a user-friendly interface to retrieve EC2 CloudWatch logs and save them to disk. It supports both interactive mode (prompts for input) and command-line mode (all options via arguments).

## Features

- ✅ **Interactive Mode**: Prompts for EC2 instance ID if not provided
- ✅ **Command-Line Mode**: Full argument support for automation
- ✅ **Format Validation**: Validates EC2 instance ID format before API calls
- ✅ **Multiple Formats**: Save logs as TXT, JSON, or CSV
- ✅ **Flexible Filtering**: Apply CloudWatch filter patterns
- ✅ **Error Handling**: Comprehensive error messages with troubleshooting tips
- ✅ **User-Friendly Output**: Clear status messages and configuration display

## Prerequisites

1. **Python 3.x** installed
2. **scotton-aws-utils** package installed:
   ```bash
   pip install -e ~/dev/projects/scotton-aws-utils
   ```
3. **AWS credentials** configured with CloudWatch Logs permissions
4. **CloudWatch agent** installed on EC2 instances (for logs to be available)

## Installation

The script is standalone and uses the `scotton-aws-utils` package. No additional installation needed beyond the package.

## Usage

### Interactive Mode

Run without arguments and follow the prompts:

```bash
python get-ec2-logs.py
```

**Example Session:**
```
============================================================
EC2 CloudWatch Log Retrieval
============================================================

Enter EC2 instance ID (e.g., i-1234567890abcdef0): i-0a1b2c3d4e5f6789

============================================================
Configuration:
============================================================
  Instance ID:      i-0a1b2c3d4e5f6789
  Output Path:      ./ec2_logs
  Format:           json
  Max Events:       1000
  Log Group Prefix: /aws/ec2
============================================================

Initializing EC2 log retriever...

🔍 Retrieving logs for EC2 instance: i-0a1b2c3d4e5f6789
📋 Found 2 log group(s) for instance 'i-0a1b2c3d4e5f6789'
✅ Retrieved 850 total log event(s)
✅ Logs saved successfully to: ./ec2_logs/ec2_logs_i-0a1b2c3d4e5f6789_20251201_024500.json
   Events: 850
   Size: 234,567 bytes

============================================================
✅ SUCCESS
============================================================
Logs saved successfully to: ./ec2_logs/ec2_logs_i-0a1b2c3d4e5f6789_20251201_024500.json
   Events: 850
   Size: 234,567 bytes
```

### Command-Line Mode

#### Basic Usage

```bash
python get-ec2-logs.py --instance-id i-1234567890abcdef0
```

#### Specify Output Directory and Format

```bash
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --output ./my_logs \
    --format txt
```

#### Retrieve More Events

```bash
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --num-events 5000
```

#### Filter Logs by Pattern

```bash
# Get only ERROR logs
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --filter-pattern "ERROR"

# Complex filter
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --filter-pattern "[time, request_id, event_type = ERROR*, ...]"
```

#### Custom Log Group Prefix

```bash
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --log-group-prefix "/custom/logs"
```

#### Save to Specific File

```bash
python get-ec2-logs.py \
    --instance-id i-1234567890abcdef0 \
    --output ./logs/production_ec2.json \
    --format json
```

## Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--instance-id` | `-i` | EC2 instance ID | (interactive prompt) |
| `--output` | `-o` | Output directory or file path | `./ec2_logs` |
| `--format` | `-f` | Output format: txt, json, csv | `json` |
| `--num-events` | `-n` | Maximum number of events to retrieve | `1000` |
| `--log-group-prefix` | `-p` | CloudWatch log group prefix | `/aws/ec2` |
| `--filter-pattern` | | CloudWatch filter pattern | (none) |

## Exit Codes

- `0`: Success
- `1`: Error (validation failed, logs not found, etc.)
- `130`: Cancelled by user (Ctrl+C)

## Examples

### Example 1: Quick Retrieval

```bash
python get-ec2-logs.py -i i-1234567890abcdef0
```

### Example 2: Large Log Retrieval in CSV Format

```bash
python get-ec2-logs.py \
    -i i-1234567890abcdef0 \
    -o ./logs/large_export.csv \
    -f csv \
    -n 10000
```

### Example 3: Filter Application Errors

```bash
python get-ec2-logs.py \
    -i i-1234567890abcdef0 \
    -o ./logs/app_errors.txt \
    -f txt \
    --filter-pattern "[ERROR]"
```

### Example 4: Multiple Instance Automation

```bash
#!/bin/bash
# retrieve_all_instances.sh

INSTANCES=(
    "i-1234567890abcdef0"
    "i-0987654321fedcba0"
    "i-abcdef1234567890"
)

for instance in "${INSTANCES[@]}"; do
    echo "Retrieving logs for $instance..."
    python get-ec2-logs.py \
        --instance-id "$instance" \
        --output "./logs/$instance" \
        --format json
done
```

## Output Formats

### Text Format (`.txt`)
Human-readable format with timestamps:
```
EC2 CloudWatch Logs
================================================================================
Total Events: 850
Generated: 2025-12-01T02:45:00
================================================================================

[2025-12-01T02:30:00] [/aws/ec2/i-xxx/var/log/syslog] [stream-1]
Dec  1 02:30:00 ip-10-0-1-100 systemd[1]: Started Session 123.
```

### JSON Format (`.json`)
Structured data with metadata:
```json
{
  "metadata": {
    "total_events": 850,
    "generated_at": "2025-12-01T02:45:00"
  },
  "events": [
    {
      "timestamp": 1701394200000,
      "timestamp_iso": "2025-12-01T02:30:00",
      "logGroup": "/aws/ec2/i-xxx/var/log/syslog",
      "logStreamName": "stream-1",
      "message": "Dec  1 02:30:00 ip-10-0-1-100..."
    }
  ]
}
```

### CSV Format (`.csv`)
Spreadsheet-compatible:
```csv
timestamp,timestamp_iso,log_group,log_stream,message
1701394200000,2025-12-01T02:30:00,/aws/ec2/i-xxx/var/log/syslog,stream-1,"Dec  1..."
```

## Error Handling

### Invalid Instance ID Format

```
❌ Invalid format. Instance ID should be like: i-1234567890abcdef0
Try again? (y/n):
```

### Instance Not Found

```
============================================================
⚠️  NOT FOUND
============================================================
⚠️  No log groups found for EC2 instance 'i-xxx' with prefix '/aws/ec2'
   Ensure CloudWatch agent is installed and configured on the instance.

Troubleshooting:
  • Ensure CloudWatch agent is installed on the EC2 instance
  • Verify the instance ID is correct
  • Check that logs are being sent to CloudWatch
```

### Permission Issues

```
❌ Unexpected error: An error occurred (AccessDeniedException)...

Please check:
  • AWS credentials are configured
  • You have necessary permissions
  • scotton-aws-utils is properly installed
```

## Troubleshooting

### No logs found

**Problem**: Script reports no log groups found

**Solutions**:
1. Verify CloudWatch agent is installed on EC2 instance:
   ```bash
   # SSH into instance
   sudo systemctl status amazon-cloudwatch-agent
   ```

2. Check if logs exist in CloudWatch console

3. Verify log group prefix matches your configuration:
   ```bash
   aws logs describe-log-groups --query 'logGroups[*].logGroupName'
   ```

### AWS credentials not configured

**Problem**: `Unable to locate credentials`

**Solution**:
```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

### Package not installed

**Problem**: `ModuleNotFoundError: No module named 'scotton_aws_utils'`

**Solution**:
```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

### Wrong AWS region

**Problem**: Instance not found but you know it exists

**Solution**: Check and set your AWS region:
```bash
# Check current region
aws configure get region

# Set correct region
aws configure set region us-east-1
```

## Integration

### Use in Python Scripts

```python
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs',
    format='json',
    num_events=1000
)

if status == 200:
    print("Success!")
else:
    print(f"Failed: {message}")
```

### Call from Bash Scripts

```bash
#!/bin/bash

# Retrieve logs with error handling
if python get-ec2-logs.py -i i-1234567890abcdef0 -o ./logs; then
    echo "Logs retrieved successfully"
    # Process logs
    cat ./logs/*.json | jq '.events[].message'
else
    echo "Failed to retrieve logs"
    exit 1
fi
```

### Scheduled Retrieval (Cron)

```bash
# Add to crontab (crontab -e)
# Retrieve logs every hour
0 * * * * cd /home/user && python get-ec2-logs.py -i i-1234567890abcdef0 -o /var/logs/ec2/$(date +\%Y\%m\%d_\%H\%M).json
```

## Comparison with Bash Script

This Python script is an alternative to `get_ec2_logs.sh`:

| Feature | get-ec2-logs.py | get_ec2_logs.sh |
|---------|----------------|----------------|
| Language | Python | Bash |
| Interactive Mode | ✅ Yes | ✅ Yes |
| Validation Attempts | Unlimited | 3 attempts max |
| AWS Validation | Via Python SDK | Via AWS CLI |
| Prerequisites | Python, scotton-aws-utils | Bash, AWS CLI, Python |
| Error Messages | Detailed | Very detailed |
| Use Case | Quick scripts, automation | System administration |

## See Also

- [EC2LogRetriever Module Documentation](EC2_LOG_RETRIEVAL.md)
- [Bash Script Alternative](BASH_SCRIPT_USAGE.md) - `get_ec2_logs.sh`
- [Python Examples](examples/ec2_log_retrieval_example.py)
- [Main Package README](README.md)

## License

Part of scotton-aws-utils package. See main package LICENSE.
