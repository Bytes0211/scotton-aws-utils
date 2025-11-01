#!/usr/bin/env python3
"""
Complete AWS Lambda Deployment Guide with Python Modules
=========================================================

This script demonstrates the complete process of deploying a Lambda function
with custom Python modules and third-party dependencies.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from zipfile import ZipFile
import json

# Ensure we import boto3 from site-packages, not from a local 'boto3' directory
import importlib
boto3 = importlib.import_module('boto3')

class LambdaDeployer:
    def __init__(self, aws_profile=None):
        """
        Initialize the Lambda deployer.

        Args:
            aws_profile (str): AWS profile name for authentication.
        """
        self.aws_profile = aws_profile
        self.init_aws_session(aws_profile)

    def init_aws_session(self, aws_profile):
        """
        if aws_profile:
            boto3.setup_default_session(profile_name=aws_profile)
        
        self.lambda_client = boto3.client('lambda')
        self.iam_client = boto3.client('iam')
        """
        self.lambda_client = boto3.client('lambda')
        self.iam_client = boto3.client('iam')
    
    def install_lambda_dependencies(self, requirements_file='requirements.txt', target_dir='package'):
        """
        Install Python dependencies to a target directory for Lambda packaging.
        
        Args:
            requirements_file (str): Path to requirements.txt
            target_dir (str): Directory to install packages
        """
        print(f"📦 Installing dependencies from {requirements_file} to {target_dir}/")
        
        # Create package directory if it doesn't exist
        Path(target_dir).mkdir(exist_ok=True)
        
        # Install dependencies
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            '-r', requirements_file,
            '-t', target_dir,
            '--no-deps'  # Don't install sub-dependencies to avoid conflicts
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
            return False
        
        return True
    
    def create_lambda_package(self, source_files, package_name='lambda_function.zip'):
        """
        Create a deployment package for Lambda.
        
        Args:
            source_files (list): List of files/directories to include
            package_name (str): Name of the output zip file
        """
        print(f"📁 Creating Lambda package: {package_name}")
        
        with ZipFile(package_name, 'w') as zipf:
            for item in source_files:
                item_path = Path(item)
                
                if item_path.is_file():
                    # Add individual files
                    zipf.write(item_path, item_path.name)
                    print(f"  ✓ Added file: {item_path.name}")
                
                elif item_path.is_dir():
                    # Add directory contents recursively
                    for file_path in item_path.rglob('*'):
                        if file_path.is_file():
                            # Preserve directory structure relative to the package
                            arcname = file_path.relative_to(item_path.parent)
                            zipf.write(file_path, arcname)
                    print(f"  ✓ Added directory: {item_path.name}/")
        
        # Check package size (Lambda has a 50MB limit for direct upload)
        package_size = Path(package_name).stat().st_size / (1024 * 1024)  # MB
        print(f"📊 Package size: {package_size:.2f} MB")
        
        if package_size > 50:
            print("⚠️  Package exceeds 50MB limit. Consider using S3 for deployment.")
            return False, package_size
        
        return True, package_size
    
    def create_execution_role(self, role_name='lambda-execution-role', additional_policies=None):
        """
        Create an IAM role for Lambda execution if it doesn't exist.
        
        Best Practice: Create separate roles for each Lambda function with 
        only the permissions they need (principle of least privilege).
        
        Args:
            role_name (str): Name of the IAM role (should be function-specific)
            additional_policies (list): List of additional policy ARNs to attach
        """
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Try to get existing role
            response = self.iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"✅ Using existing IAM role: {role_name}")
            return role_arn
        
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create new role
            print(f"🔐 Creating new IAM role: {role_name}")
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Execution role for Lambda functions'
            )
            
            # Attach basic execution policy (required for all Lambda functions)
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach additional policies if specified
            if additional_policies:
                for policy_arn in additional_policies:
                    try:
                        self.iam_client.attach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policy_arn
                        )
                        print(f"  ✓ Attached policy: {policy_arn}")
                    except Exception as e:
                        print(f"  ❌ Failed to attach policy {policy_arn}: {e}")
            
            role_arn = response['Role']['Arn']
            print(f"✅ Created IAM role: {role_name}")
            print(f"⏳ Waiting for IAM role to propagate...")
            self._wait_for_role_propagation(role_name)
            return role_arn
    
    def create_function_specific_role(self, function_name, required_services=None):
        """
        Create a function-specific IAM role with minimal required permissions.
        
        Args:
            function_name (str): Name of the Lambda function
            required_services (list): List of AWS services this function needs access to
                                    Options: ['s3', 'dynamodb', 'sqs', 'sns', 'rds', 'secretsmanager']
        
        Returns:
            str: IAM role ARN
        """
        role_name = f"{function_name}-execution-role"
        
        # Define service-specific policies
        service_policies = {
            's3': 'arn:aws:iam::aws:policy/AmazonS3FullAccess',
            'dynamodb': 'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess', 
            'sqs': 'arn:aws:iam::aws:policy/AmazonSQSFullAccess',
            'sns': 'arn:aws:iam::aws:policy/AmazonSNSFullAccess',
            'rds': 'arn:aws:iam::aws:policy/AmazonRDSDataFullAccess',
            'secretsmanager': 'arn:aws:iam::aws:policy/SecretsManagerReadWrite'
        }
        
        # Build list of additional policies based on required services
        additional_policies = []
        if required_services:
            for service in required_services:
                if service.lower() in service_policies:
                    additional_policies.append(service_policies[service.lower()])
                else:
                    print(f"⚠️ Unknown service: {service}. Available services: {list(service_policies.keys())}")
        
        print(f"🔐 Creating function-specific role for: {function_name}")
        print(f"   Required services: {required_services or 'None (basic execution only)'}")
        
        return self.create_execution_role(role_name, additional_policies)
    
    def _wait_for_role_propagation(self, role_name, max_retries=10, delay=2):
        """
        Wait for IAM role to propagate across AWS infrastructure.
        
        Args:
            role_name (str): Name of the IAM role
            max_retries (int): Maximum number of retries
            delay (int): Delay in seconds between retries
        """
        for i in range(max_retries):
            try:
                # Verify role exists and can be retrieved
                self.iam_client.get_role(RoleName=role_name)
                time.sleep(delay)  # Wait for propagation
                print(f"✓ Role propagation check {i+1}/{max_retries}")
                return True
            except Exception as e:
                if i < max_retries - 1:
                    time.sleep(delay)
                else:
                    raise
        return True
    
    def _wait_for_function_active(self, function_name, max_retries=30, delay=2):
        """
        Wait for Lambda function to transition from Pending to Active state.
        
        Args:
            function_name (str): Name of the Lambda function
            max_retries (int): Maximum number of retries
            delay (int): Delay in seconds between retries
        """
        print(f"⏳ Waiting for function to become active...")
        for i in range(max_retries):
            try:
                response = self.lambda_client.get_function(FunctionName=function_name)
                state = response['Configuration']['State']
                
                if state == 'Active':
                    print(f"✅ Function is now active")
                    return True
                elif state == 'Failed':
                    reason = response['Configuration'].get('StateReason', 'Unknown')
                    raise Exception(f"Function entered Failed state: {reason}")
                else:
                    print(f"  Function state: {state} (check {i+1}/{max_retries})")
                    time.sleep(delay)
            except Exception as e:
                if i < max_retries - 1:
                    time.sleep(delay)
                else:
                    raise
        
        raise TimeoutError(f"Function {function_name} did not become active within {max_retries * delay} seconds")
    
    def deploy_lambda_function(self,
                             function_name,
                             zip_file,
                             handler,
                             role_arn,
                             runtime='python3.13',
                             timeout=300,
                             memory_size=128,
                             environment_vars=None,
                             update_if_exists=True):
        """
        Deploy Lambda function to AWS.
        
        Args:
            function_name (str): Name of the Lambda function
            zip_file (str): Path to the deployment package
            handler (str): Function handler (e.g., 'lambda_function.lambda_handler')
            role_arn (str): IAM role ARN for execution
            runtime (str): Python runtime version
            timeout (int): Function timeout in seconds
            memory_size (int): Memory allocation in MB
            environment_vars (dict): Environment variables
            update_if_exists (bool): Whether to update function if it exists
        """
        print(f"🚀 Deploying Lambda function: {function_name}")
        
        with open(zip_file, 'rb') as f:
            zip_content = f.read()
        
        function_config = {
            'FunctionName': function_name,
            'Runtime': runtime,
            'Role': role_arn,
            'Handler': handler,
            'Code': {'ZipFile': zip_content},
            'Timeout': timeout,
            'MemorySize': memory_size,
            'Publish': True
        }
        
        if environment_vars:
            function_config['Environment'] = {'Variables': environment_vars}
        
        response = None
        
        try:
            # Check if function exists
            self.lambda_client.get_function(FunctionName=function_name)
            
            if update_if_exists:
                # Update existing function code
                response = self.lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
                print(f"✅ Updated existing function code: {function_name}")
                
                # Update configuration if needed
                self.lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Runtime=runtime,
                    Role=role_arn,
                    Handler=handler,
                    Timeout=timeout,
                    MemorySize=memory_size,
                    Environment={'Variables': environment_vars} if environment_vars else {}
                )
                print(f"✅ Updated function configuration: {function_name}")
            else:
                print(f"⚠️ Function {function_name} already exists and update_if_exists=False")
                return None
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function with retry logic for role assumption
            max_retries = 5
            retry_delay = 3
            
            for attempt in range(max_retries):
                try:
                    response = self.lambda_client.create_function(**function_config)
                    print(f"✅ Created new function: {function_name}")
                    break
                except self.lambda_client.exceptions.InvalidParameterValueException as e:
                    if "cannot be assumed" in str(e) and attempt < max_retries - 1:
                        print(f"⏳ Role not ready yet, retrying in {retry_delay}s... (attempt {attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        raise
        
        return response
    
    def test_lambda_function(self, function_name, test_payload=None):
        """
        Test the deployed Lambda function.
        
        Args:
            function_name (str): Name of the Lambda function
            test_payload (dict): Test payload to send to the function
        """
        print(f"🧪 Testing Lambda function: {function_name}")
        
        import json
        
        # Wait for function to become active
        self._wait_for_function_active(function_name)
        
        if test_payload is None:
            test_payload = {}
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(test_payload)
            )
            
            result = response['Payload'].read().decode('utf-8')
            status_code = response['StatusCode']
            
            print(f"✅ Function executed successfully (Status: {status_code})")
            print(f"📤 Response: {result}")
            
            return True, result
            
        except Exception as e:
            print(f"❌ Function execution failed: {str(e)}")
            return False, str(e)
