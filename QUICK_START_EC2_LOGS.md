# Quick Start: EC2 Log Retrieval

Choose your preferred method and get started in seconds!

## 🚀 Choose Your Tool

### 1. Python Script (Fastest)
```bash
cd ~/dev/projects/scotton-aws-utils
python get-ec2-logs.py
```
**When to use:** Quick one-off log retrieval

### 2. Bash Script (Most Interactive)
```bash
cd ~/dev/projects/scotton-aws-utils
./get_ec2_logs.sh
```
**When to use:** System administration with extensive validation

### 3. Python Library (Most Flexible)
```python
from scotton_aws_utils import EC2LogRetriever

retriever = EC2LogRetriever()
status, message = retriever.retrieve_and_save_logs(
    instance_id='i-1234567890abcdef0',
    output_path='./logs',
    format='json'
)
```
**When to use:** Building applications or automation

## 📚 Full Documentation

- **Python Script:** [GET_EC2_LOGS_README.md](GET_EC2_LOGS_README.md)
- **Bash Script:** [BASH_SCRIPT_USAGE.md](BASH_SCRIPT_USAGE.md)
- **Python Module:** [EC2_LOG_RETRIEVAL.md](EC2_LOG_RETRIEVAL.md)
- **Overview:** [EC2_LOGS_README.md](EC2_LOGS_README.md)

## ⚡ Common Commands

```bash
# Interactive mode
python get-ec2-logs.py

# Specify everything on command line
python get-ec2-logs.py -i i-xxx -o ./logs -f json -n 2000

# Filter error logs only
python get-ec2-logs.py -i i-xxx --filter-pattern "ERROR"

# Bash script with full validation
./get_ec2_logs.sh
```

## 🔧 Installation

```bash
cd ~/dev/projects/scotton-aws-utils
pip install -e .
```

That's it! You're ready to retrieve EC2 logs.
