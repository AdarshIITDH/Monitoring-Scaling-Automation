'''
4. Lambda-based Health Checks & Management:
 - Develop a Lambda function to periodically check the health of the web application 
(through the ALB).
 - If the health check fails consistently, the Lambda function should:
 - Capture a snapshot of the failing instance for debugging purposes.
 - Terminate the problematic instance, allowing the ASG to replace it.
 - Send a notification through SNS to the administrators.
'''

#----------------------SNS Topic ------------------------------------
# import boto3
# # Initialize the SNS client
# sns_client = boto3.client('sns', region_name='ap-south-1') 

# # Define the SNS topic name
# topic_name = 'adarsh-boto3-sns'

# # Create the SNS topic
# response = sns_client.create_topic(Name=topic_name)

# # Extract the ARN (Amazon Resource Name) of the created SNS topic
# topic_arn = response['TopicArn']

# print(f'SNS topic created with ARN: {topic_arn}')

# # Specify the protocol and endpoint (email address in this case)
# protocol = 'email'
# endpoint = 'adarsh307kumar@gmail.com'

# # Create the subscription
# sns_client.subscribe(
#     TopicArn=topic_arn,
#     Protocol=protocol,
#     Endpoint=endpoint
# )
#------------------------------------------------------------------------

topic_arn='arn:aws:sns:ap-south-1:295397358094:adarsh-boto3-sns'

#------------------------Lambda Function-------------------------------------------
import boto3

client = boto3.client('lambda' , region_name='ap-south-1')

with open('code.zip', 'rb') as file:
    zip_contents = file.read()
response = client.create_function(
    Code={
        'ZipFile': zip_contents  
    },
    FunctionName='adarsh-boto3-lambda',
    Handler='index.handler',
    MemorySize=256,
    Publish=True,
    Role='arn:aws:iam::295397358094:role/adarsh-role',
    Runtime='python3.11',
    # Tags={
    #     'DEPARTMENT': 'Assets',
    # },
    Timeout=15,
    TracingConfig={
        'Mode': 'Active',
    },
)

yourlambdafunctionarn='arn:aws:lambda:ap-south-1:295397358094:function:adarsh-boto3-lambda'

# Lambda function information
function_name = 'adarsh-boto3-lambda'
sns_topic_arn = 'arn:aws:sns:ap-south-1:295397358094:adarsh-boto3-sns'

# Create or update the function's resource-based policy
policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'Service': 'lambda.amazonaws.com'
            },
            'Action': 'lambda:InvokeFunction',
            'Resource': yourlambdafunctionarn,
            'Condition': {
                'ArnLike': {
                    'AWS:SourceArn': sns_topic_arn
                }
            }
        }
    ]
}

response = client.add_permission(
    FunctionName=function_name,
    StatementId='sns-permission',
    Action='lambda:InvokeFunction',
    Principal='sns.amazonaws.com',
    SourceArn='arn:aws:sns:ap-south-1:295397358094:adarsh-boto3-sns',
    SourceAccount='295397358094'  
)

print(response)
#------------------------------------------------------------------------






















