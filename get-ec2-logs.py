#!/usr/bin/env python3
"""
get-ec2-logs.py
Created: 2025-11-30
Last Modified: 2025-12-01

Description: 
    This script retrieves CloudWatch logs from EC2 instances and saves them to disk.
    It lists all EC2 instances in paginated format (5 at a time) and allows interactive
    selection, or accepts instance ID via command-line argument.

Usage:
    python get-ec2-logs.py
    python get-ec2-logs.py --instance-id i-1234567890abcdef0
    python get-ec2-logs.py --instance-id i-1234567890abcdef0 --format json --output ./logs
"""

import sys
import os
import argparse
from scotton_aws_utils import EC2LogRetriever
from scotton_aws_utils.aws import Aws


def display_ec2_page(instances, page_num, page_size=5):
    """Display a page of EC2 instances with numbered list."""
    start_idx = (page_num - 1) * page_size
    end_idx = min(start_idx + page_size, len(instances))
    
    print(f"\n{'='*60}")
    print(f"EC2 Instances (Page {page_num} of {(len(instances) + page_size - 1) // page_size})")
    print(f"{'='*60}")
    
    for i in range(start_idx, end_idx):
        instance = instances[i]
        print(f"\n[{i + 1}] {instance['instance_id']} ({instance['state']})")
        if instance['name']:
            print(f"    Name: {instance['name']}")
        print(f"    Type: {instance['type']}")
        if instance['public_ip']:
            print(f"    Public IP: {instance['public_ip']}")
        if instance['private_ip']:
            print(f"    Private IP: {instance['private_ip']}")
    
    print(f"\n{'='*60}")


def get_instance_id_interactive():
    """List EC2 instances and prompt user to select one."""
    print("\n" + "="*60)
    print("EC2 CloudWatch Log Retrieval")
    print("="*60)
    
    try:
        print("\n⏳ Fetching EC2 instances...")
        aws = Aws()
        instances = aws.list_ec2s(return_data=True)
        
        if not instances:
            print("❌ No EC2 instances found in your account.")
            print("\nManual entry option:")
            instance_id = input("Enter EC2 instance ID (or press Enter to cancel): ").strip()
            return instance_id if instance_id else None
        
        page_size = 5
        current_page = 1
        total_pages = (len(instances) + page_size - 1) // page_size
        
        while True:
            display_ec2_page(instances, current_page, page_size)
            
            print("\nOptions:")
            print("  Enter number (1-{}) to select an instance".format(len(instances)))
            if current_page < total_pages:
                print("  Enter 'n' for next page")
            if current_page > 1:
                print("  Enter 'p' for previous page")
            print("  Enter 'q' to quit")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 'q':
                return None
            elif choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(instances):
                    selected = instances[idx]
                    print(f"\n✅ Selected: {selected['instance_id']}")
                    if selected['name']:
                        print(f"   Name: {selected['name']}")
                    return selected['instance_id']
                else:
                    print(f"❌ Invalid selection. Please enter a number between 1 and {len(instances)}.")
            else:
                print("❌ Invalid input. Please try again.")
    
    except Exception as e:
        print(f"❌ Error fetching EC2 instances: {str(e)}")
        print("\nFalling back to manual entry...")
        instance_id = input("Enter EC2 instance ID (or press Enter to cancel): ").strip()
        return instance_id if instance_id else None


def main():
    """Main function to retrieve EC2 logs."""
    parser = argparse.ArgumentParser(
        description='Retrieve CloudWatch logs from EC2 instances and save to disk',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for instance ID)
  python get-ec2-logs.py
  
  # Specify instance ID directly
  python get-ec2-logs.py --instance-id i-1234567890abcdef0
  
  # Custom format and number of events
  python get-ec2-logs.py --instance-id i-1234567890abcdef0 \
      --format txt --num-events 2000
  
  # Filter error logs only
  python get-ec2-logs.py --instance-id i-1234567890abcdef0 \
      --filter-pattern "ERROR"
        """
    )
    
    parser.add_argument(
        '--instance-id', '-i',
        help='EC2 instance ID (e.g., i-1234567890abcdef0)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['txt', 'json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--num-events', '-n',
        type=int,
        default=1000,
        help='Maximum number of events to retrieve (default: 1000)'
    )
    parser.add_argument(
        '--log-group-prefix', '-p',
        default='/aws/ec2',
        help='CloudWatch log group prefix (default: /aws/ec2)'
    )
    parser.add_argument(
        '--filter-pattern',
        default='',
        help='CloudWatch filter pattern to apply'
    )
    
    args = parser.parse_args()
    
    # Get instance ID (either from args or interactive prompt)
    instance_id = args.instance_id
    if not instance_id:
        instance_id = get_instance_id_interactive()
        if not instance_id:
            print("\n❌ Operation cancelled by user.")
            return 1
    
    # Hardcoded output path: /home/$USER/logs/ec2
    output_path = os.path.expanduser("~/logs/ec2")
    
    # Display configuration
    print("\n" + "="*60)
    print("Configuration:")
    print("="*60)
    print(f"  Instance ID:      {instance_id}")
    print(f"  Output Path:      {output_path}")
    print(f"  Format:           {args.format}")
    print(f"  Max Events:       {args.num_events}")
    print(f"  Log Group Prefix: {args.log_group_prefix}")
    if args.filter_pattern:
        print(f"  Filter Pattern:   {args.filter_pattern}")
    print("="*60 + "\n")
    
    # Create retriever and get logs
    try:
        print("Initializing EC2 log retriever...\n")
        retriever = EC2LogRetriever()
        
        status, message = retriever.retrieve_and_save_logs(
            instance_id=instance_id,
            output_path=output_path,
            format=args.format,
            num_events=args.num_events,
            log_group_prefix=args.log_group_prefix,
            filter_pattern=args.filter_pattern
        )
        
        # Display result
        print("\n" + "="*60)
        if status == 200:
            print("✅ SUCCESS")
            print("="*60)
            print(message)
            return 0
        elif status == 404:
            print("⚠️  NOT FOUND")
            print("="*60)
            print(message)
            print("\nTroubleshooting:")
            print("  • Ensure CloudWatch agent is installed on the EC2 instance")
            print("  • Verify the instance ID is correct")
            print("  • Check that logs are being sent to CloudWatch")
            return 1
        else:
            print("❌ ERROR")
            print("="*60)
            print(message)
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nPlease check:")
        print("  • AWS credentials are configured")
        print("  • You have necessary permissions")
        print("  • scotton-aws-utils is properly installed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
