#!/usr/bin/env python3
"""
EC2 Log Retriever - Retrieves CloudWatch logs for EC2 instances and saves to disk.

This module provides functionality to:
- Retrieve EC2 CloudWatch logs
- Save logs to local disk in various formats (txt, json, csv)
- Filter logs by time range and patterns
- Support multiple log groups per instance
"""

import os
import json
import csv
from datetime import datetime
from typing import Optional, List
from botocore.exceptions import ClientError
from .aws import Aws


class EC2LogRetriever:
    """Retrieve and save EC2 CloudWatch logs to disk."""
    
    def __init__(self, aws_client: Optional[Aws] = None):
        """Initialize EC2 log retriever.
        
        Args:
            aws_client: Optional Aws client instance (creates new one if not provided)
        """
        self.aws = aws_client or Aws()
    
    def retrieve_and_save_logs(
        self, 
        instance_id: str,
        output_path: str,
        log_group_prefix: str = '/aws/ec2',
        num_events: int = 1000,
        format: str = 'txt',
        filter_pattern: str = '',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> tuple:
        """Retrieve EC2 logs and save to disk.
        
        Args:
            instance_id: EC2 instance ID (e.g., 'i-1234567890abcdef0')
            output_path: Path where logs should be saved (directory or file)
            log_group_prefix: CloudWatch log group prefix (default: '/aws/ec2')
            num_events: Maximum number of log events to retrieve (default: 1000)
            format: Output format - 'txt', 'json', or 'csv' (default: 'txt')
            filter_pattern: Optional CloudWatch filter pattern
            start_time: Optional start timestamp in milliseconds since epoch
            end_time: Optional end timestamp in milliseconds since epoch
        
        Returns:
            Tuple of (status_code, message)
        """
        try:
            print(f"🔍 Retrieving logs for EC2 instance: {instance_id}")
            
            # Find all log groups for this instance using the get_ec2_logs method
            # which properly handles EC2 log discovery
            all_events = self.aws.get_ec2_logs(
                instance_id=instance_id,
                log_group_prefix=log_group_prefix,
                num_events=num_events
            )
            
            if not all_events:
                message = f"⚠️  No log events found for EC2 instance '{instance_id}' with prefix '{log_group_prefix}'\n" \
                          f"   Ensure CloudWatch agent is installed and configured on the instance."
                print(message)
                return 404, message
            
            # Sort events by timestamp
            all_events.sort(key=lambda x: x.get('timestamp', 0))
            
            print(f"✅ Retrieved {len(all_events)} total log event(s)")
            
            # Save logs to disk
            return self._save_logs_to_disk(
                events=all_events,
                output_path=output_path,
                instance_id=instance_id,
                format=format
            )
            
        except ClientError as err:
            error_msg = f"❌ Error retrieving EC2 logs: {err.response['Error']['Code']} - {err.response['Error']['Message']}"
            print(error_msg)
            return 500, error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(error_msg)
            return 500, error_msg
    
    def _save_logs_to_disk(
        self,
        events: List[dict],
        output_path: str,
        instance_id: str,
        format: str
    ) -> tuple:
        """Save log events to disk in specified format.
        
        Args:
            events: List of log events
            output_path: Output path (file or directory)
            instance_id: EC2 instance ID
            format: Output format ('txt', 'json', or 'csv')
        
        Returns:
            Tuple of (status_code, message)
        """
        try:
            # Determine output file path
            if os.path.isdir(output_path):
                # If path is a directory, create filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"ec2_logs_{instance_id}_{timestamp}.{format}"
                file_path = os.path.join(output_path, filename)
            else:
                # Use provided path as filename
                file_path = output_path
                # Ensure directory exists
                dir_path = os.path.dirname(file_path)
                if dir_path:  # Only create if there's a directory component
                    os.makedirs(dir_path, exist_ok=True)
            
            # Save based on format
            if format == 'json':
                self._save_as_json(events, file_path)
            elif format == 'csv':
                self._save_as_csv(events, file_path)
            else:  # default to txt
                self._save_as_txt(events, file_path)
            
            file_size = os.path.getsize(file_path)
            message = f"✅ Logs saved successfully to: {file_path}\n" \
                     f"   Events: {len(events)}\n" \
                     f"   Size: {file_size:,} bytes"
            print(message)
            return 200, message
            
        except Exception as e:
            error_msg = f"❌ Error saving logs to disk: {str(e)}"
            print(error_msg)
            return 500, error_msg
    
    def _save_as_txt(self, events: List[dict], file_path: str) -> None:
        """Save logs as plain text file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"EC2 CloudWatch Logs\n")
            f.write(f"{'='*80}\n")
            f.write(f"Total Events: {len(events)}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n\n")
            
            for event in events:
                timestamp = event.get('timestamp', 0)
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                message = event.get('message', '').strip()
                log_group = event.get('logGroup', 'N/A')
                log_stream = event.get('logStreamName', 'N/A')
                
                f.write(f"[{dt.isoformat()}] [{log_group}] [{log_stream}]\n")
                f.write(f"{message}\n\n")
    
    def _save_as_json(self, events: List[dict], file_path: str) -> None:
        """Save logs as JSON file."""
        # Convert timestamp to ISO format for readability
        formatted_events = []
        for event in events:
            formatted_event = event.copy()
            if 'timestamp' in formatted_event:
                dt = datetime.fromtimestamp(formatted_event['timestamp'] / 1000.0)
                formatted_event['timestamp_iso'] = dt.isoformat()
            formatted_events.append(formatted_event)
        
        output_data = {
            'metadata': {
                'total_events': len(events),
                'generated_at': datetime.now().isoformat()
            },
            'events': formatted_events
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)
    
    def _save_as_csv(self, events: List[dict], file_path: str) -> None:
        """Save logs as CSV file."""
        if not events:
            return
        
        # Define CSV columns
        fieldnames = ['timestamp', 'timestamp_iso', 'log_group', 'log_stream', 'message']
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                timestamp = event.get('timestamp', 0)
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                
                row = {
                    'timestamp': timestamp,
                    'timestamp_iso': dt.isoformat(),
                    'log_group': event.get('logGroup', 'N/A'),
                    'log_stream': event.get('logStreamName', 'N/A'),
                    'message': event.get('message', '').strip()
                }
                writer.writerow(row)
    
    def retrieve_logs_for_multiple_instances(
        self,
        instance_ids: List[str],
        output_dir: str,
        **kwargs
    ) -> dict:
        """Retrieve logs for multiple EC2 instances.
        
        Args:
            instance_ids: List of EC2 instance IDs
            output_dir: Directory where logs should be saved
            **kwargs: Additional arguments passed to retrieve_and_save_logs
        
        Returns:
            Dictionary mapping instance_id to (status_code, message) tuple
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        for instance_id in instance_ids:
            print(f"\n{'='*80}")
            print(f"Processing instance: {instance_id}")
            print(f"{'='*80}")
            
            status, message = self.retrieve_and_save_logs(
                instance_id=instance_id,
                output_path=output_dir,
                **kwargs
            )
            results[instance_id] = (status, message)
        
        return results


def main():
    """Example usage of EC2LogRetriever."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Retrieve EC2 CloudWatch logs and save to disk'
    )
    parser.add_argument(
        'instance_id',
        help='EC2 instance ID (e.g., i-1234567890abcdef0)'
    )
    parser.add_argument(
        '-o', '--output',
        default='./ec2_logs',
        help='Output path (file or directory) (default: ./ec2_logs)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['txt', 'json', 'csv'],
        default='txt',
        help='Output format (default: txt)'
    )
    parser.add_argument(
        '-n', '--num-events',
        type=int,
        default=1000,
        help='Maximum number of events to retrieve (default: 1000)'
    )
    parser.add_argument(
        '-p', '--log-group-prefix',
        default='/aws/ec2',
        help='CloudWatch log group prefix (default: /aws/ec2)'
    )
    parser.add_argument(
        '--filter-pattern',
        default='',
        help='CloudWatch filter pattern'
    )
    
    args = parser.parse_args()
    
    # Create retriever and get logs
    retriever = EC2LogRetriever()
    status, message = retriever.retrieve_and_save_logs(
        instance_id=args.instance_id,
        output_path=args.output,
        format=args.format,
        num_events=args.num_events,
        log_group_prefix=args.log_group_prefix,
        filter_pattern=args.filter_pattern
    )
    
    # Exit with appropriate code
    exit(0 if status == 200 else 1)


if __name__ == '__main__':
    main()
