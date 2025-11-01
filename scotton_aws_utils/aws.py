import uuid
import json
import boto3 as boto
import requests 
import io 
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from . import util, lambdadeployer

class Aws:
    """AWS service wrapper class for S3, IAM, Lambda, EC2, and DynamoDB operations."""

    def __init__(self, use_local_dynamodb: bool = False) -> None:
        """Initialize AWS service clients lazily.
        
        Args:
            use_local_dynamodb: If True, connects to DynamoDB at localhost:8000
        """
        self._s3_client = None 
        self._s3_resource = None
        self._iam_client = None
        self._lambda_client = None
        self._lambda_deployer = None
        self._ec2_client = None
        self._ec2_resource = None
        self._dynamodb_client = None
        self._dynamodb_resource = None
        self._use_local_dynamodb = use_local_dynamodb
        
    # Properties for lazy initialization of AWS clients
    # lazy initialization Creational Design Pattern that delays the creation of a resource until it’s actually needed
    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = util.get_s3_client()
        return self._s3_client
    
    # @s3_client.setter allows you to define a method that will be called when you assign a value to the s3_client property.
    # syntactically useful for dependency injection during testing or when you want to override the default client behavior.
    # warning: setter methods should be used judiciously to avoid unintended side effects. Especially with multi-threaded applications, changing the client unexpectedly could lead to inconsistent behavior.
    # and methods that are resource-intensive or have side effects should be designed carefully to ensure that they behave predictably when their dependencies are changed.
    @s3_client.setter
    def s3_client(self, value):
        self._s3_client = value
    
    @property
    def s3_resource(self):
        if self._s3_resource is None:
            self._s3_resource = util.get_s3_resource()
        return self._s3_resource
    
    @s3_resource.setter
    def s3_resource(self, value):
        self._s3_resource = value

    @property
    def iam_client(self):
        if self._iam_client is None:
            self._iam_client = util.get_iam_client()
        return self._iam_client
    
    @iam_client.setter
    def iam_client(self, value):
        self._iam_client = value
    
    @property
    def lambda_client(self):
        if self._lambda_client is None:
            self._lambda_client = util.get_lambda_client()
        return self._lambda_client
    
    @lambda_client.setter
    def lambda_client(self, value):
        self._lambda_client = value

    @property
    def lambda_deployer(self):
        if self._lambda_deployer is None:
            self._lambda_deployer = lambdadeployer.LambdaDeployer()
        return self._lambda_deployer

    @lambda_deployer.setter
    def lambda_deployer(self, value):
        self._lambda_deployer = value

    @property
    def ec2_client(self):
        if self._ec2_client is None:
            self._ec2_client = util.get_ec2_client()
        return self._ec2_client
    
    @ec2_client.setter
    def ec2_client(self, value):
        self._ec2_client = value
    
    @property
    def ec2_resource(self):
        if self._ec2_resource is None:
            self._ec2_resource = util.get_ec2_resource()
        return self._ec2_resource
    
    @ec2_resource.setter
    def ec2_resource(self, value):
        self._ec2_resource = value

    @property
    def dynamodb_client(self):
        if self._dynamodb_client is None:
            self._dynamodb_client = util.get_dynamodb_client(local=self._use_local_dynamodb)
        return self._dynamodb_client
    
    @dynamodb_client.setter
    def dynamodb_client(self, value):
        self._dynamodb_client = value
    
    @property
    def dynamodb_resource(self):
        if self._dynamodb_resource is None:
            self._dynamodb_resource = util.get_dynamodb_resource(local=self._use_local_dynamodb)
        return self._dynamodb_resource
    
    @dynamodb_resource.setter
    def dynamodb_resource(self, value):
        self._dynamodb_resource = value

    def create_bucket_name(self, prefix: str = 'scotton') -> str:
        """Create unique bucket name with UUID suffix."""
        return f"{prefix}-{str(uuid.uuid4())[:8]}"

    def create_bucket(self, bucket_prefix: str) -> tuple:
        """Create S3 bucket with proper region configuration."""
        session = boto.session.Session() # type: ignore
        current_region = session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)
        
        if current_region == 'us-east-1':
            bucket_resp = self.s3_resource.create_bucket(Bucket=bucket_name) # type: ignore
        else:
            bucket_resp = self.s3_resource.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': current_region}) # type: ignore
        
        return bucket_name, bucket_resp

    def list_buckets(self) -> None:
        """List all S3 buckets in account."""
        response = self.s3_client.list_buckets()
        print(f"📋 S3 Buckets in account:\n")
        for bucket in response.get('Buckets', []):
            print(f" - {bucket['Name']}")

    def list_bucket_objects(self, bucket_name: str) -> None:
        """List objects in S3 bucket."""
        response = self.s3_client.list_objects_v2(Bucket=bucket_name)
        print(f"📋 S3 Objects in bucket {bucket_name}:\n")
        for obj in response.get('Contents', []):
            print(f" - {obj['Key']} (Size: {obj['Size']}, StorageClass: {obj['StorageClass']})")


    def add_file_to_bucket(self, bucket_name: str, file_name: str, object_name: str, url: str = None) -> tuple: # type: ignore
        """Upload file to S3 bucket from local path or URL."""
        if url:
            response = requests.get(f'{url}/{file_name}')
            response.raise_for_status()
            self.s3_client.upload_fileobj(io.BytesIO(response.content), bucket_name, object_name)
        else:
            with open(file_name, 'rb') as file:
                self.s3_client.upload_fileobj(file, bucket_name, object_name)
        return 200, f'✅ FILE {object_name} UPLOADED TO {bucket_name} SUCCESSFULLY!'

    def copy_to_bucket(self, from_bucket: str, to_bucket: str, file_name: str) -> str:
        """Copy S3 object between buckets."""
        copy_source = {'Bucket': from_bucket, 'Key': file_name}
        self.s3_resource.Object(to_bucket, file_name).copy(copy_source) # type: ignore
        return f'✅ FILE {file_name} COPIED FROM {from_bucket} TO {to_bucket}'

    def delete_files_from_bucket(self, bucket_name: str, file_list: list) -> tuple:
        """Delete multiple files from S3 bucket efficiently."""
        if not isinstance(file_list, list):
            return 400, f'❌ {file_list} IS NOT A LIST'
        
        # Use batch delete for efficiency
        delete_objects = [{'Key': key} for key in file_list]
        response = self.s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': delete_objects}
        )
        return 200, f'✅ {len(file_list)} FILES DELETED FROM {bucket_name}'

    def enable_bucket_versioning(self, bucket_name: str) -> str:
        """Enable versioning for S3 bucket."""
        versioning = self.s3_resource.BucketVersioning(bucket_name) # type: ignore
        versioning.enable()
        return f'✅ VERSIONING ENABLED FOR BUCKET {bucket_name} - STATUS: {versioning.status}'

    def list_iam_roles(self) -> dict:
        """List all IAM roles in account."""
        response = self.iam_client.list_roles()
        return {
            role['RoleName']: (role['RoleName'], role['Arn']) 
            for role in response['Roles']
        }

    def validate_iam_role(self, role: str) -> tuple:
        """Validate IAM role exists in account."""
        role_list = self.list_iam_roles()
        if role in role_list:
            return 1, role_list[role]
        return 0, f'❌ ROLE {role} NOT FOUND!'
    
    def invoke_function(self, function_name: str, function_params: dict, get_log: bool = False) -> dict:
        """Invokes a Lambda function."""
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params),
                LogType="Tail" if get_log else "None",
            )
            print(f"✅ Function {function_name} invoked successfully")
            return response
        except ClientError as err:
            print(f"❌ Error invoking function {function_name}: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def update_function_code(self, function_name: str, deployment_package: bytes) -> None:
        """Updates Lambda function code with .zip archive."""
        try:
            print(f"✅ Function {function_name} code updated successfully")
            self.lambda_client.update_function_code(
                FunctionName=function_name, ZipFile=deployment_package
            )
        except ClientError as err:
            print(f"❌ Error updating function {function_name}: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def update_function_configuration(self, function_name: str, env_vars: dict) -> None:
        """Updates Lambda function environment variables."""
        try:
            response = self.lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": env_vars}
            )
            print(f'✅ Function {function_name} configuration updated successfully')
            return response
        except ClientError as err:
            print(f"❌ Error updating function config {function_name}: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def list_functions(self) -> None:
        """
        Lists the Lambda functions for the current account.
        Returns list of function details.
        """
        try:
            func_paginator = self.lambda_client.get_paginator("list_functions")
            for page in func_paginator.paginate():
                print(f"📋 Functions in account:\n")
                for func in page['Functions']:
                    print(f"Function Name: {func['FunctionName']}\n"
                          f"\tDescription: {func.get('Description', '')}\n"
                          f"\tRuntime: {func['Runtime']}\n"
                          f"\tHandler: {func['Handler']}\n")
        except ClientError as err:
            print(f"❌ Error listing functions: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
    
    def create_ec2(self, image_id: str, instance_type: str = 't2.micro', min_count: int = 1, max_count: int = 1, key_name: str = None, security_group_ids: list = None, subnet_id: str = None, tags: list = None) -> tuple: # type: ignore
        """Create EC2 instance(s) with specified configuration."""
        try:
            params = {
                'ImageId': image_id,
                'InstanceType': instance_type,
                'MinCount': min_count,
                'MaxCount': max_count
            }
            
            if key_name:
                params['KeyName'] = key_name
            if security_group_ids:
                params['SecurityGroupIds'] = security_group_ids
            if subnet_id:
                params['SubnetId'] = subnet_id
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'instance',
                    'Tags': tags
                }]
            
            instances = self.ec2_resource.create_instances(**params) # type: ignore
            instance_ids = [instance.id for instance in instances]
            print(f"✅ EC2 instance(s) created successfully: {', '.join(instance_ids)}")
            return 200, instance_ids
        except ClientError as err:
            print(f"❌ Error creating EC2 instance: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def start_ec2(self, instance_ids: list) -> tuple:
        """Start one or more EC2 instances."""
        if not isinstance(instance_ids, list):
            return 400, f'❌ {instance_ids} IS NOT A LIST'
        
        try:
            response = self.ec2_client.start_instances(InstanceIds=instance_ids)
            print(f"✅ Started EC2 instance(s): {', '.join(instance_ids)}")
            return 200, response
        except ClientError as err:
            print(f"❌ Error starting EC2 instance(s): {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def stop_ec2(self, instance_ids: list) -> tuple:
        """Stop one or more EC2 instances."""
        if not isinstance(instance_ids, list):
            return 400, f'❌ {instance_ids} IS NOT A LIST'
        
        try:
            response = self.ec2_client.stop_instances(InstanceIds=instance_ids)
            print(f"✅ Stopped EC2 instance(s): {', '.join(instance_ids)}")
            return 200, response
        except ClientError as err:
            print(f"❌ Error stopping EC2 instance(s): {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def list_ec2s(self) -> None:
        """List all EC2 instances in account."""
        try:
            response = self.ec2_client.describe_instances()
            if len(response['Reservations']) > 0:
                print(f"📋 EC2 Instances in account [{len(response['Reservations'])}]:\n")
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        instance_name = ''
                        if 'Tags' in instance:
                            for tag in instance['Tags']:
                                if tag['Key'] == 'Name':
                                    instance_name = tag['Value']
                                    break
                        
                        print(f" - {instance['InstanceId']} ({instance['State']['Name']})")
                        if instance_name:
                            print(f"   Name: {instance_name}")
                        print(f"   Type: {instance['InstanceType']}")
                        print(f"   Image: {instance['ImageId']}")
                        if 'PublicIpAddress' in instance:
                            print(f"   Public IP: {instance['PublicIpAddress']}")
                        if 'PrivateIpAddress' in instance:
                            print(f"   Private IP: {instance['PrivateIpAddress']}")
                        print()
            else:
                print("📋 No EC2 instances found in account.")
        except ClientError as err:
            print(f"❌ Error listing EC2 instances: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def remove_ec2s(self, instance_ids: list) -> tuple:
        """Terminate one or more EC2 instances."""
        if not isinstance(instance_ids, list):
            return 400, f'❌ {instance_ids} IS NOT A LIST'
        
        try:
            response = self.ec2_client.terminate_instances(InstanceIds=instance_ids)
            print(f"✅ Terminated EC2 instance(s): {', '.join(instance_ids)}")
            return 200, response
        except ClientError as err:
            print(f"❌ Error terminating EC2 instance(s): {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise

    def create_dynamodb_table(self, table_name: str, key_schema: list, attribute_definitions: list, 
                              provisioned_throughput: dict = None, billing_mode: str = 'PAY_PER_REQUEST', # type: ignore
                              global_secondary_indexes: list = None, local_secondary_indexes: list = None, # type: ignore
                              tags: list = None, stream_specification: dict = None) -> tuple: # type: ignore
        """Create DynamoDB table with specified configuration.
        
        Args:
            table_name: Name of the table
            key_schema: List of key schema elements
            attribute_definitions: List of attribute definitions
            provisioned_throughput: Throughput settings (only for PROVISIONED mode)
            billing_mode: 'PAY_PER_REQUEST' or 'PROVISIONED'
            global_secondary_indexes: List of GSI definitions
            local_secondary_indexes: List of LSI definitions
            tags: List of tags
            stream_specification: Stream settings e.g. {'StreamEnabled': True, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}
        """
        try:
            params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'BillingMode': billing_mode
            }
            
            # Only add ProvisionedThroughput if billing mode is PROVISIONED
            if billing_mode == 'PROVISIONED':
                if provisioned_throughput:
                    params['ProvisionedThroughput'] = provisioned_throughput
                else:
                    params['ProvisionedThroughput'] = {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
            
            if global_secondary_indexes:
                params['GlobalSecondaryIndexes'] = global_secondary_indexes
            if local_secondary_indexes:
                params['LocalSecondaryIndexes'] = local_secondary_indexes
            if tags:
                params['Tags'] = tags
            if stream_specification:
                params['StreamSpecification'] = stream_specification
            
            table = self.dynamodb_resource.create_table(**params) # type: ignore
            table.wait_until_exists()
            print(f"✅ DynamoDB table '{table_name}' created successfully")
            return 200, table
        except ClientError as err:
            print(f"❌ Error creating DynamoDB table: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def put_item_dynamodb(self, table_name: str, item: dict) -> tuple:
        """Insert or update item in DynamoDB table."""
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            response = table.put_item(Item=item)
            print(f"✅ Item added to table '{table_name}' successfully")
            return 200, response
        except ClientError as err:
            print(f"❌ Error putting item in DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def get_item_dynamodb(self, table_name: str, key: dict) -> dict:
        """Retrieve item from DynamoDB table by key."""
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            response = table.get_item(Key=key)
            
            if 'Item' in response:
                print(f"✅ Item retrieved from table '{table_name}' successfully")
                return response['Item']
            else:
                print(f"⚠️  Item not found in table '{table_name}'")
                return {}
        except ClientError as err:
            print(f"❌ Error getting item from DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def update_item_dynamodb(self, table_name: str, key: dict, update_expression: str, 
                            expression_attribute_values: dict = None, # type: ignore
                            expression_attribute_names: dict = None, # type: ignore
                            condition_expression: str = None, # type: ignore
                            return_values: str = 'ALL_NEW') -> tuple:
        """Update item in DynamoDB table with optional conditional expression.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item
            update_expression: Update expression
            expression_attribute_values: Values for the expression
            expression_attribute_names: Name substitutions for reserved words
            condition_expression: Optional condition that must be met for update
            return_values: What to return after update
        """
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            params = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ReturnValues': return_values
            }
            
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = expression_attribute_values
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            response = table.update_item(**params)
            print(f"✅ Item updated in table '{table_name}' successfully")
            return 200, response
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"⚠️  Conditional check failed for update in table '{table_name}'")
            else:
                print(f"❌ Error updating item in DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def delete_item_dynamodb(self, table_name: str, key: dict) -> tuple:
        """Delete item from DynamoDB table."""
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            response = table.delete_item(Key=key)
            print(f"✅ Item deleted from table '{table_name}' successfully")
            return 200, response
        except ClientError as err:
            print(f"❌ Error deleting item from DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def query_dynamodb(self, table_name: str, key_condition_expression, # type: ignore
                       expression_attribute_values: dict = None, # type: ignore
                       expression_attribute_names: dict = None, # type: ignore
                       filter_expression = None, # type: ignore
                       index_name: str = None, # type: ignore
                       limit: int = None, # type: ignore
                       scan_index_forward: bool = True) -> list:
        """Query DynamoDB table with key condition.
        
        Args:
            table_name: Name of the table
            key_condition_expression: Key condition (can be string or boto3.dynamodb.conditions.Key)
            expression_attribute_values: Values for the expression (when using string expressions)
            expression_attribute_names: Name substitutions
            filter_expression: Filter expression (can be string or boto3.dynamodb.conditions.Attr)
            index_name: Name of the index to query
            limit: Maximum number of items to return
            scan_index_forward: Sort order (True for ascending, False for descending)
        
        Returns:
            List of items (automatically handles pagination)
        """
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            params = {
                'KeyConditionExpression': key_condition_expression,
                'ScanIndexForward': scan_index_forward
            }
            
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = expression_attribute_values
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            if filter_expression:
                params['FilterExpression'] = filter_expression
            if index_name:
                params['IndexName'] = index_name
            if limit:
                params['Limit'] = limit
            
            response = table.query(**params)
            items = response.get('Items', [])
            
            # Handle pagination automatically
            while 'LastEvaluatedKey' in response:
                params['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = table.query(**params)
                items.extend(response.get('Items', []))
            
            print(f"✅ Query returned {len(items)} item(s) from table '{table_name}'")
            return items
        except ClientError as err:
            print(f"❌ Error querying DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def scan_dynamodb(self, table_name: str, filter_expression = None, # type: ignore
                     expression_attribute_values: dict = None, # type: ignore
                     expression_attribute_names: dict = None, # type: ignore
                     limit: int = None) -> list: # type: ignore
        """Scan DynamoDB table (reads all items).
        
        Args:
            table_name: Name of the table
            filter_expression: Filter expression (can be string or boto3.dynamodb.conditions.Attr)
            expression_attribute_values: Values for the expression (when using string expressions)
            expression_attribute_names: Name substitutions
            limit: Maximum number of items to return
        """
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            params = {}
            
            if filter_expression:
                params['FilterExpression'] = filter_expression
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = expression_attribute_values
            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names
            if limit:
                params['Limit'] = limit
            
            response = table.scan(**params)
            items = response.get('Items', [])
            
            # Handle pagination for large tables
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                params['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = table.scan(**params)
                items.extend(response.get('Items', []))
            
            print(f"✅ Scan returned {len(items)} item(s) from table '{table_name}'")
            return items
        except ClientError as err:
            print(f"❌ Error scanning DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def batch_write_dynamodb(self, table_name: str, items: list) -> tuple:
        """Batch write items to DynamoDB table (up to 25 items per batch)."""
        if not isinstance(items, list):
            return 400, f'❌ {items} IS NOT A LIST'
        
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            
            # DynamoDB batch_write supports max 25 items per batch
            batch_size = 25
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                with table.batch_writer() as writer:
                    for item in batch:
                        writer.put_item(Item=item)
            
            print(f"✅ Batch write completed: {len(items)} item(s) added to table '{table_name}'")
            return 200, f'✅ {len(items)} ITEMS ADDED TO {table_name}'
        except ClientError as err:
            print(f"❌ Error batch writing to DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def list_dynamodb_tables(self) -> None:
        """List all DynamoDB tables in account."""
        try:
            response = self.dynamodb_client.list_tables()
            table_names = response.get('TableNames', [])
            
            if table_names:
                print(f"📋 DynamoDB Tables in account [{len(table_names)}]:\n")
                for table_name in table_names:
                    # Get additional table details
                    table_info = self.dynamodb_client.describe_table(TableName=table_name)
                    table = table_info['Table']
                    print(f" - {table_name}")
                    print(f"   Status: {table['TableStatus']}")
                    print(f"   Item Count: {table.get('ItemCount', 0)}")
                    print(f"   Size: {table.get('TableSizeBytes', 0)} bytes")
                    print(f"   Billing Mode: {table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')}")
                    print()
            else:
                print("📋 No DynamoDB tables found in account.")
        except ClientError as err:
            print(f"❌ Error listing DynamoDB tables: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def batch_get_dynamodb(self, table_name: str, keys: list) -> list:
        """Batch get items from DynamoDB table (up to 100 items).
        
        Args:
            table_name: Name of the table
            keys: List of key dictionaries
        
        Returns:
            List of items
        """
        if not isinstance(keys, list):
            raise ValueError(f'❌ keys must be a list')
        
        try:
            response = self.dynamodb_resource.batch_get_item( # type: ignore
                RequestItems={
                    table_name: {
                        'Keys': keys
                    }
                }
            )
            
            items = response.get('Responses', {}).get(table_name, [])
            print(f"✅ Batch get returned {len(items)} item(s) from table '{table_name}'")
            return items
        except ClientError as err:
            print(f"❌ Error batch getting from DynamoDB: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def transact_write_dynamodb(self, transact_items: list) -> tuple:
        """Execute a DynamoDB transaction with up to 25 items.
        
        Ensures all operations succeed or fail together atomically.
        
        Args:
            transact_items: List of transaction items (Put, Update, Delete, ConditionCheck)
                          Each item should be a dict with one of these keys:
                          - Put: {TableName, Item, [ConditionExpression]}
                          - Update: {TableName, Key, UpdateExpression, [ConditionExpression]}
                          - Delete: {TableName, Key, [ConditionExpression]}
                          - ConditionCheck: {TableName, Key, ConditionExpression}
        
        Returns:
            Tuple of (status_code, response)
        """
        if not isinstance(transact_items, list):
            return 400, f'❌ transact_items must be a list'
        
        if len(transact_items) > 25:
            return 400, f'❌ Transaction can contain max 25 items, got {len(transact_items)}'
        
        try:
            response = self.dynamodb_client.transact_write_items(
                TransactItems=transact_items
            )
            print(f"✅ Transaction completed successfully with {len(transact_items)} item(s)")
            return 200, response
        except ClientError as err:
            if err.response['Error']['Code'] == 'TransactionCanceledException':
                print(f"⚠️  Transaction cancelled - check conditions and item conflicts")
                # The cancellation reasons are in err.response['CancellationReasons']
            else:
                print(f"❌ Error in transaction: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def delete_dynamodb_table(self, table_name: str) -> tuple:
        """Delete DynamoDB table."""
        try:
            table = self.dynamodb_resource.Table(table_name) # type: ignore
            table.delete()
            table.wait_until_not_exists()
            print(f"✅ DynamoDB table '{table_name}' deleted successfully")
            return 200, f'✅ TABLE {table_name} DELETED'
        except ClientError as err:
            print(f"❌ Error deleting DynamoDB table: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def get_table_schema(self, table_name: str) -> dict:
        """Get table schema information (key schema and attribute definitions)."""
        try:
            response = self.dynamodb_client.describe_table(TableName=table_name)
            table = response['Table']
            
            schema = {
                'table_name': table_name,
                'key_schema': table['KeySchema'],
                'attribute_definitions': table['AttributeDefinitions'],
                'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
            }
            
            # Include provisioned throughput if applicable
            if 'ProvisionedThroughput' in table:
                schema['provisioned_throughput'] = {
                    'ReadCapacityUnits': table['ProvisionedThroughput']['ReadCapacityUnits'],
                    'WriteCapacityUnits': table['ProvisionedThroughput']['WriteCapacityUnits']
                }
            
            # Include GSI if present
            if 'GlobalSecondaryIndexes' in table:
                schema['global_secondary_indexes'] = table['GlobalSecondaryIndexes']
            
            # Include LSI if present
            if 'LocalSecondaryIndexes' in table:
                schema['local_secondary_indexes'] = table['LocalSecondaryIndexes']
            
            print(f"✅ Retrieved schema for table '{table_name}'")
            return schema
        except ClientError as err:
            print(f"❌ Error getting table schema: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
    
    def copy_table_to_aws(self, source_table_name: str, destination_table_name: str = None) -> tuple: # type: ignore
        """Copy a table from local DynamoDB to AWS DynamoDB.
        
        Args:
            source_table_name: Name of the source table (from local DynamoDB)
            destination_table_name: Name for the destination table (defaults to source name)
        
        Returns:
            Tuple of (status_code, message)
        """
        if destination_table_name is None:
            destination_table_name = source_table_name
        
        try:
            # Get source table schema from local DynamoDB
            local_aws = Aws(use_local_dynamodb=True)
            schema = local_aws.get_table_schema(source_table_name)
            
            print(f"🔄 Starting migration of '{source_table_name}' to AWS as '{destination_table_name}'...")
            
            # Create table on AWS
            print(f"🛠️  Creating table '{destination_table_name}' on AWS...")
            create_params = {
                'table_name': destination_table_name,
                'key_schema': schema['key_schema'],
                'attribute_definitions': schema['attribute_definitions'],
                'billing_mode': 'PAY_PER_REQUEST'  # Use on-demand for migration
            }
            
            self.create_dynamodb_table(**create_params)
            
            # Scan all items from local table
            print(f"📊 Scanning items from local table '{source_table_name}'...")
            items = local_aws.scan_dynamodb(source_table_name)
            
            if not items:
                print(f"⚠️  No items to migrate from '{source_table_name}'")
                return 200, f'✅ TABLE {destination_table_name} CREATED (0 items migrated)'
            
            # Batch write items to AWS table
            print(f"🚀 Migrating {len(items)} item(s) to AWS...")
            self.batch_write_dynamodb(destination_table_name, items)
            
            print(f"✅ Migration complete: {len(items)} item(s) copied to '{destination_table_name}' on AWS")
            return 200, f'✅ TABLE {destination_table_name} CREATED AND {len(items)} ITEMS MIGRATED'
            
        except ClientError as err:
            print(f"❌ Error copying table to AWS: {err.response['Error']['Code']} - {err.response['Error']['Message']}")
            raise
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            raise
