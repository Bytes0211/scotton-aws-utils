"""
Scotton AWS Utilities
=====================

A Python package for AWS service operations including S3, Lambda, EC2, IAM, and DynamoDB.

This package provides a unified interface for common AWS operations with simplified
error handling, automatic retries, and best practices built-in.

Main Classes:
    Aws: Main class for AWS operations
    
Utility Functions:
    util.get_s3_client()
    util.get_lambda_client()
    util.get_dynamodb_client()
    util.get_dynamodb_resource()
    ... and more

Example:
    >>> from scotton_aws_utils import Aws
    >>> aws = Aws()
    >>> aws.list_buckets()
"""

__version__ = '1.0.0'
__author__ = 'Scott On'

from .aws import Aws
from . import util
from . import lambdadeployer

__all__ = ['Aws', 'util', 'lambdadeployer']
