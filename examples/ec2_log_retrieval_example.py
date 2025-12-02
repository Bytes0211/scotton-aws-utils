#!/usr/bin/env python3
"""
EC2 Log Retrieval Examples

This file demonstrates various ways to use the EC2LogRetriever class
to retrieve and save EC2 CloudWatch logs.
"""

from scotton_aws_utils import Aws, EC2LogRetriever


def example_basic_usage():
    """Basic example: Retrieve logs and save as text file."""
    print("="*80)
    print("Example 1: Basic Usage - Save logs as text file")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs',
        format='txt',
        num_events=500
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_json_format():
    """Example: Save logs as JSON for programmatic processing."""
    print("\n" + "="*80)
    print("Example 2: Save logs as JSON")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs/ec2_logs.json',
        format='json',
        num_events=1000
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_csv_format():
    """Example: Save logs as CSV for spreadsheet analysis."""
    print("\n" + "="*80)
    print("Example 3: Save logs as CSV")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs/ec2_logs.csv',
        format='csv',
        num_events=1000
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_with_filter():
    """Example: Retrieve only ERROR logs."""
    print("\n" + "="*80)
    print("Example 4: Filter logs by pattern (ERROR only)")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs/error_logs.txt',
        format='txt',
        filter_pattern='ERROR',
        num_events=500
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_with_time_range():
    """Example: Retrieve logs for a specific time range."""
    print("\n" + "="*80)
    print("Example 5: Retrieve logs for specific time range")
    print("="*80)
    
    from datetime import datetime, timedelta
    
    # Get logs from last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Convert to milliseconds since epoch
    start_ms = int(start_time.timestamp() * 1000)
    end_ms = int(end_time.timestamp() * 1000)
    
    retriever = EC2LogRetriever()
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs/last_24h.json',
        format='json',
        start_time=start_ms,
        end_time=end_ms,
        num_events=2000
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_custom_log_group():
    """Example: Use custom log group prefix."""
    print("\n" + "="*80)
    print("Example 6: Custom log group prefix")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    # If your CloudWatch agent uses a custom prefix
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs/custom_logs.txt',
        log_group_prefix='/custom/path/logs',
        num_events=500
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_multiple_instances():
    """Example: Retrieve logs for multiple instances."""
    print("\n" + "="*80)
    print("Example 7: Retrieve logs for multiple EC2 instances")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    instance_ids = [
        'i-1234567890abcdef0',
        'i-0987654321fedcba0',
        'i-abcdef1234567890'
    ]
    
    results = retriever.retrieve_logs_for_multiple_instances(
        instance_ids=instance_ids,
        output_dir='./logs/multi_instance',
        format='json',
        num_events=500
    )
    
    print("\nResults Summary:")
    for instance_id, (status, message) in results.items():
        print(f"\n{instance_id}:")
        print(f"  Status: {status}")
        print(f"  {message}")


def example_with_existing_aws_client():
    """Example: Use existing Aws client instance."""
    print("\n" + "="*80)
    print("Example 8: Use existing Aws client")
    print("="*80)
    
    # Reuse existing AWS client
    aws = Aws()
    retriever = EC2LogRetriever(aws_client=aws)
    
    status, message = retriever.retrieve_and_save_logs(
        instance_id='i-1234567890abcdef0',
        output_path='./logs',
        format='txt',
        num_events=500
    )
    
    print(f"\nStatus: {status}")
    print(f"Result: {message}")


def example_error_handling():
    """Example: Proper error handling."""
    print("\n" + "="*80)
    print("Example 9: Error handling")
    print("="*80)
    
    retriever = EC2LogRetriever()
    
    try:
        status, message = retriever.retrieve_and_save_logs(
            instance_id='i-nonexistent',
            output_path='./logs/error_test.txt',
            num_events=100
        )
        
        if status == 200:
            print(f"✅ Success: {message}")
        elif status == 404:
            print(f"⚠️  Not found: {message}")
        else:
            print(f"❌ Error (status {status}): {message}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")


def main():
    """Run all examples (modify as needed)."""
    print("EC2 Log Retrieval Examples")
    print("="*80)
    print("\nNOTE: Modify the instance IDs before running these examples!")
    print("="*80)
    
    # Uncomment the examples you want to run:
    
    # example_basic_usage()
    # example_json_format()
    # example_csv_format()
    # example_with_filter()
    # example_with_time_range()
    # example_custom_log_group()
    # example_multiple_instances()
    # example_with_existing_aws_client()
    # example_error_handling()
    
    print("\n✅ Examples completed!")


if __name__ == '__main__':
    main()
