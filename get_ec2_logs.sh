#!/bin/bash

# EC2 Log Retrieval Script
# This script lists EC2 instances, allows user to select one interactively, and retrieves CloudWatch logs

set -e  # Exit on error (except in validation checks)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_ATTEMPTS=3
OUTPUT_DIR="/home/$USER/logs"
LOG_FORMAT="json"
NUM_EVENTS=1000

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✅ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${NC}$1"
}

print_error() {
    echo -e "${RED}❌ ${NC}$1"
}

# Function to fetch and display EC2 instances
fetch_ec2_instances() {
    print_info "Fetching EC2 instances from AWS..." >&2
    
    # Fetch instances using Python
    local temp_file=$(mktemp)
    local error_file=$(mktemp)
    if python3 -c "
import json
from scotton_aws_utils.aws import Aws
try:
    aws = Aws()
    instances = aws.list_ec2s(return_data=True)
    print(json.dumps(instances))
except Exception as e:
    import sys
    print(f'Error: {e}', file=sys.stderr)
    exit(1)
" > "$temp_file" 2>"$error_file"; then
        rm -f "$error_file"
        echo "$temp_file"
        return 0
    else
        cat "$error_file" >&2
        rm -f "$temp_file" "$error_file"
        return 1
    fi
}

# Function to display page of EC2 instances
display_ec2_page() {
    local instances_json=$1
    local page=$2
    local page_size=5
    
    local total_count=$(echo "$instances_json" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    
    if [[ $total_count -eq 0 ]]; then
        return 1
    fi
    
    local total_pages=$(( (total_count + page_size - 1) / page_size ))
    local start_idx=$(( (page - 1) * page_size ))
    
    echo ""
    echo "============================================================"
    echo "EC2 Instances (Page $page of $total_pages)"
    echo "============================================================"
    
    echo "$instances_json" | python3 -c "
import sys, json
instances = json.load(sys.stdin)
page = $page
page_size = $page_size
start_idx = (page - 1) * page_size
end_idx = min(start_idx + page_size, len(instances))

for i in range(start_idx, end_idx):
    instance = instances[i]
    print(f'\\n[{i + 1}] {instance[\"instance_id\"]} ({instance[\"state\"]})')
    if instance['name']:
        print(f'    Name: {instance[\"name\"]}')
    print(f'    Type: {instance[\"type\"]}')
    if instance['public_ip']:
        print(f'    Public IP: {instance[\"public_ip\"]}')
    if instance['private_ip']:
        print(f'    Private IP: {instance[\"private_ip\"]}')
"
    
    echo ""
    echo "============================================================"
    return 0
}

# Function to get instance ID by index
get_instance_by_index() {
    local instances_json=$1
    local index=$2
    
    echo "$instances_json" | python3 -c "
import sys, json
instances = json.load(sys.stdin)
idx = $index - 1
if 0 <= idx < len(instances):
    print(instances[idx]['instance_id'])
"
}

# Function to get total instance count
get_instance_count() {
    local instances_json=$1
    echo "$instances_json" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))"
}

# Function to select EC2 instance interactively
select_ec2_instance() {
    local instances_file
    instances_file=$(fetch_ec2_instances)
    local fetch_status=$?
    
    if [[ $fetch_status -ne 0 ]] || [[ ! -f "$instances_file" ]]; then
        print_error "Failed to fetch EC2 instances" >&2
        rm -f "$instances_file"
        return 1
    fi
    
    local instances_json=$(cat "$instances_file")
    rm -f "$instances_file"
    
    local total_count=$(get_instance_count "$instances_json")
    
    if [[ $total_count -eq 0 ]]; then
        print_warning "No EC2 instances found in your account" >&2
        echo "" >&2
        print_info "Manual entry option:" >&2
        read -p "Enter EC2 instance ID (or press Enter to cancel): " instance_id
        instance_id=$(echo "$instance_id" | xargs)
        if [[ -n "$instance_id" ]]; then
            echo "$instance_id"
            return 0
        else
            return 1
        fi
    fi
    
    local page_size=5
    local current_page=1
    local total_pages=$(( (total_count + page_size - 1) / page_size ))
    
    while true; do
        display_ec2_page "$instances_json" $current_page >&2
        
        echo "" >&2
        print_info "Options:" >&2
        echo "  Enter number (1-${total_count}) to select an instance" >&2
        if [[ $current_page -lt $total_pages ]]; then
            echo "  Enter 'n' for next page" >&2
        fi
        if [[ $current_page -gt 1 ]]; then
            echo "  Enter 'p' for previous page" >&2
        fi
        echo "  Enter 'q' to quit" >&2
        echo "" >&2
        read -p "Your choice: " choice
        choice=$(echo "$choice" | xargs | tr '[:upper:]' '[:lower:]')
        
        if [[ "$choice" == "q" ]]; then
            return 1
        elif [[ "$choice" == "n" ]] && [[ $current_page -lt $total_pages ]]; then
            current_page=$((current_page + 1))
        elif [[ "$choice" == "p" ]] && [[ $current_page -gt 1 ]]; then
            current_page=$((current_page - 1))
        elif [[ "$choice" =~ ^[0-9]+$ ]]; then
            if [[ $choice -ge 1 ]] && [[ $choice -le $total_count ]]; then
                selected_id=$(get_instance_by_index "$instances_json" $choice)
                echo "" >&2
                print_success "Selected: $selected_id" >&2
                echo "$selected_id"
                return 0
            else
                print_error "Invalid selection. Please enter a number between 1 and ${total_count}." >&2
            fi
        else
            print_error "Invalid input. Please try again." >&2
        fi
    done
}

# Function to display script header
show_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         EC2 CloudWatch Log Retrieval Tool                 ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Function to prompt for configuration
prompt_config() {
    echo ""
    print_info "Configuration options (press Enter to use defaults):"
    echo ""
    
    # Log format
    read -p "Output format (txt/json/csv) [${LOG_FORMAT}]: " user_format
    if [[ -n "$user_format" ]]; then
        case "$user_format" in
            txt|json|csv)
                LOG_FORMAT="$user_format"
                ;;
            *)
                print_warning "Invalid format. Using default: ${LOG_FORMAT}"
                ;;
        esac
    fi
    
    # Number of events
    read -p "Number of events to retrieve [${NUM_EVENTS}]: " user_events
    if [[ -n "$user_events" ]] && [[ "$user_events" =~ ^[0-9]+$ ]]; then
        NUM_EVENTS="$user_events"
    fi
    
    echo ""
    print_info "Using configuration:"
    echo "  Output directory: ${OUTPUT_DIR}"
    echo "  Format: ${LOG_FORMAT}"
    echo "  Max events: ${NUM_EVENTS}"
    echo ""
}

# Function to retrieve logs
retrieve_logs() {
    local instance_id=$1
    
    print_info "Retrieving CloudWatch logs for instance: ${instance_id}"
    echo ""
    
    # Create output directory if it doesn't exist
    mkdir -p "$OUTPUT_DIR"
    
    # Execute Python module to retrieve logs
    if python3 -m scotton_aws_utils.ec2_log_retriever "$instance_id" \
        --output "$OUTPUT_DIR" \
        --format "$LOG_FORMAT" \
        --num-events "$NUM_EVENTS"; then
        
        echo ""
        print_success "Logs retrieved successfully!"
        print_info "Check output directory: ${OUTPUT_DIR}"
        return 0
    else
        echo ""
        print_error "Failed to retrieve logs"
        return 1
    fi
}

# Main script execution
main() {
    show_header
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        print_info "Install AWS CLI: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if scotton-aws-utils is installed
    if ! python3 -c "import scotton_aws_utils" 2>/dev/null; then
        print_error "scotton-aws-utils package is not installed"
        print_info "Install with: pip install -e ~/dev/projects/scotton-aws-utils"
        exit 1
    fi
    
    # Prompt for configuration
    prompt_config
    
    # Select EC2 instance
    echo ""
    echo "════════════════════════════════════════════════════════════"
    print_info "Select EC2 instance for log retrieval"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    # Option to manually enter instance ID first
    print_info "Enter EC2 instance ID directly or press Enter to list instances:"
    read -p "EC2 Instance ID: " manual_instance_id
    manual_instance_id=$(echo "$manual_instance_id" | xargs)
    
    if [[ -n "$manual_instance_id" ]]; then
        # Validate instance ID format (i-xxxxxxxxxxxxxxxxx)
        if [[ "$manual_instance_id" =~ ^i-[0-9a-f]{8,17}$ ]]; then
            instance_id="$manual_instance_id"
            print_success "Using instance: $instance_id"
        else
            print_warning "Invalid instance ID format. Expected format: i-xxxxxxxxxxxxxxxxx"
            print_info "Proceeding to list instances..."
            echo ""
            instance_id=$(select_ec2_instance) || instance_id=""
        fi
    else
        # User pressed Enter - list instances
        echo ""
        instance_id=$(select_ec2_instance) || instance_id=""
    fi
    
    if [[ -z "$instance_id" ]]; then
        echo ""
        print_error "No instance selected. Exiting."
        exit 1
    fi
    
    # Retrieve logs
    echo ""
    echo "════════════════════════════════════════════════════════════"
    if retrieve_logs "$instance_id"; then
        echo ""
        print_success "Operation completed successfully!"
        exit 0
    else
        echo ""
        print_error "Operation failed"
        print_info "Common issues:"
        echo "  - CloudWatch agent not installed on EC2 instance"
        echo "  - No logs available for this instance"
        echo "  - Missing CloudWatch Logs permissions"
        echo ""
        exit 1
    fi
}

# Run main function
main
