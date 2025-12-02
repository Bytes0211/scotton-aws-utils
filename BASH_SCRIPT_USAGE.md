# EC2 Log Retrieval Bash Script

A user-friendly bash script for retrieving CloudWatch logs from EC2 instances with validation and error handling.

## Features

- ✅ **Interactive prompts** for EC2 instance ID and configuration
- ✅ **Format validation** - Checks EC2 instance ID format before API calls
- ✅ **AWS validation** - Verifies instance exists using AWS CLI
- ✅ **3-attempt limit** - Allows up to 3 attempts before exiting
- ✅ **Colored output** - Easy-to-read colored terminal output
- ✅ **Error handling** - Comprehensive error messages and troubleshooting tips
- ✅ **Configurable** - Customize output directory, format, and event count

## Prerequisites

1. **AWS CLI** installed and configured
2. **Python 3** installed
3. **scotton-aws-utils** package installed
4. **AWS credentials** configured with appropriate permissions

## Installation

The script is already created at:
```bash
~/dev/projects/scotton-aws-utils/get_ec2_logs.sh
```

Make it executable (already done):
```bash
chmod +x ~/dev/projects/scotton-aws-utils/get_ec2_logs.sh
```

## Usage

### Run the script

```bash
cd ~/dev/projects/scotton-aws-utils
./get_ec2_logs.sh
```

### What the script does

1. **Displays header** with script information
2. **Checks prerequisites** (AWS CLI, Python, package installation)
3. **Prompts for configuration**:
   - Output directory (default: `./ec2_logs`)
   - Output format (txt/json/csv, default: `json`)
   - Number of events (default: `1000`)
4. **Prompts for EC2 instance ID** (up to 3 attempts)
5. **Validates format** - Checks if ID matches pattern `i-xxxxxxxxxxxxxxxx`
6. **Validates with AWS** - Confirms instance exists
7. **Retrieves logs** using the Python module
8. **Reports success/failure** with helpful messages

## Example Session

```bash
$ ./get_ec2_logs.sh

╔════════════════════════════════════════════════════════════╗
║         EC2 CloudWatch Log Retrieval Tool                 ║
╚════════════════════════════════════════════════════════════╝

ℹ Configuration options (press Enter to use defaults):

Output directory [./ec2_logs]: ./my_logs
Output format (txt/json/csv) [json]: txt
Number of events to retrieve [1000]: 2000

ℹ Using configuration:
  Output directory: ./my_logs
  Format: txt
  Max events: 2000

════════════════════════════════════════════════════════════
ℹ Attempt 1 of 3

Enter EC2 instance ID (e.g., i-1234567890abcdef0): i-0a1b2c3d4e5f6g7h8
❌ Invalid EC2 instance ID format
ℹ Format should be: i-xxxxxxxxxxxxxxxx (i- followed by hex characters)

════════════════════════════════════════════════════════════
ℹ Attempt 2 of 3

Enter EC2 instance ID (e.g., i-1234567890abcdef0): i-0a1b2c3d4e5f6789
ℹ Validating EC2 instance: i-0a1b2c3d4e5f6789...
✅ EC2 instance validated successfully

════════════════════════════════════════════════════════════
ℹ Retrieving CloudWatch logs for instance: i-0a1b2c3d4e5f6789

🔍 Retrieving logs for EC2 instance: i-0a1b2c3d4e5f6789
📋 Found 2 log group(s) for instance 'i-0a1b2c3d4e5f6789'
   Retrieving logs from: /aws/ec2/i-0a1b2c3d4e5f6789/var/log/syslog
✅ Retrieved 856 log event(s) from stream 'i-0a1b2c3d4e5f6789'
   Retrieving logs from: /aws/ec2/i-0a1b2c3d4e5f6789/var/log/messages
✅ Retrieved 344 log event(s) from stream 'i-0a1b2c3d4e5f6789'
✅ Retrieved 1200 total log event(s)
✅ Logs saved successfully to: ./my_logs/ec2_logs_i-0a1b2c3d4e5f6789_20251201_024500.txt
   Events: 1200
   Size: 456,789 bytes

✅ Logs retrieved successfully!
ℹ Check output directory: ./my_logs

✅ Operation completed successfully!
```

## Error Scenarios

### Scenario 1: Invalid Format

```bash
Enter EC2 instance ID (e.g., i-1234567890abcdef0): 12345
❌ Invalid EC2 instance ID format
ℹ Format should be: i-xxxxxxxxxxxxxxxx (i- followed by hex characters)
```

### Scenario 2: Instance Not Found

```bash
Enter EC2 instance ID (e.g., i-1234567890abcdef0): i-1234567890abcdef0
ℹ Validating EC2 instance: i-1234567890abcdef0...
❌ EC2 instance 'i-1234567890abcdef0' not found or access denied
ℹ Possible reasons:
  - Instance ID is incorrect
  - Instance is in a different region
  - You don't have permission to access this instance
```

### Scenario 3: Maximum Attempts Reached

After 3 failed attempts:
```bash
════════════════════════════════════════════════════════════
❌ Maximum attempts reached (3)
❌ Failed to validate EC2 instance ID

ℹ Please verify:
  1. The instance ID is correct
  2. The instance exists in your current AWS region
  3. Your AWS credentials are configured
  4. You have permissions to describe EC2 instances

ℹ Check your AWS region with: aws configure get region
ℹ List instances with: aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,Tags[?Key==`Name`].Value|[0]]' --output table
```

## Configuration Variables

You can modify these variables at the top of the script:

```bash
MAX_ATTEMPTS=3          # Number of validation attempts
OUTPUT_DIR="./ec2_logs" # Default output directory
LOG_FORMAT="json"       # Default format (txt/json/csv)
NUM_EVENTS=1000         # Default number of events
```

## Troubleshooting

### AWS CLI not found

**Error**: `❌ AWS CLI is not installed or not in PATH`

**Solution**:
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Python package not installed

**Error**: `❌ scotton-aws-utils package is not installed`

**Solution**:
```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

### AWS credentials not configured

**Error**: `Unable to locate credentials`

**Solution**:
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### Check current AWS region

```bash
aws configure get region
```

### List all your EC2 instances

```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

### CloudWatch agent not installed

If logs are not found, the CloudWatch agent might not be installed on the EC2 instance:

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

## Script Structure

```
get_ec2_logs.sh
├── Configuration variables
├── Helper functions
│   ├── print_info()
│   ├── print_success()
│   ├── print_warning()
│   ├── print_error()
│   ├── validate_instance_id_format()
│   ├── validate_instance_exists()
│   ├── show_header()
│   ├── prompt_config()
│   └── retrieve_logs()
└── main()
    ├── Check prerequisites
    ├── Prompt for configuration
    ├── Validation loop (3 attempts)
    └── Retrieve logs
```

## Integration with Other Scripts

You can also call this script from other scripts:

```bash
#!/bin/bash

# Auto-retrieve logs for multiple instances
instances=("i-1234567890abcdef0" "i-0987654321fedcba0")

for instance in "${instances[@]}"; do
    echo "$instance" | ~/dev/projects/scotton-aws-utils/get_ec2_logs.sh
done
```

Or use it with environment variables:

```bash
export OUTPUT_DIR="./production_logs"
export LOG_FORMAT="json"
export NUM_EVENTS="5000"

./get_ec2_logs.sh
```

## Advanced Usage

### Create a symlink for easy access

```bash
sudo ln -s ~/dev/projects/scotton-aws-utils/get_ec2_logs.sh /usr/local/bin/get-ec2-logs
```

Now you can run from anywhere:
```bash
get-ec2-logs
```

### Add to PATH

Add to your `~/.bashrc` or `~/.bash_profile`:
```bash
export PATH="$PATH:~/dev/projects/scotton-aws-utils"
```

Then run:
```bash
get_ec2_logs.sh
```

## See Also

- [EC2 Log Retrieval Documentation](EC2_LOG_RETRIEVAL.md)
- [Main README](README.md)
- [Python Examples](examples/ec2_log_retrieval_example.py)
