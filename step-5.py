'''
5. S3 Logging & Monitoring: 
 - Configure the ALB to send access logs to the S3 bucket. 
 - Create a Lambda function that triggers when a new log is added to the S3 bucket. This function can analyze the log for suspicious activities (like potential DDoS attacks) or just high traffic. 
 - If any predefined criteria are met during the log analysis, the Lambda function sends a  notification via SNS. 
'''

# import boto3
# import csv
# # Initialize the S3 client
# s3_client = boto3.client('s3')
# region='ap-south-1'
# # Define the bucket name
# bucket_name = 'adarsh-boto3-s3'
# # Create the S3 bucket
# location = {'LocationConstraint': region}
# s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
# # Get the bucket ARN
# response = s3_client.get_bucket_location(Bucket=bucket_name)
# bucket_location = response['LocationConstraint']
# s3_bucket = f'arn:aws:s3:::{bucket_name}'




#----------------------------------------------------------
import boto3

# Initialize AWS client for the Elastic Load Balancing service
elbv2_client = boto3.client('elbv2', region_name='ap-south-1')

# Define the ARN of the ALB
alb_arn = 'arn:aws:elasticloadbalancing:ap-south-1:295397358094:loadbalancer/app/adarsh-boto3-lb/5a90975daf5cef9f'

# Define the S3 bucket name where you want to store the access logs
s3_bucket_name = 'adarsh-boto3-s3'  

# Configure access logs for the ALB
elbv2_client.modify_load_balancer_attributes(
    LoadBalancerArn=alb_arn,
    Attributes=[
        {
            'Key': 'access_logs.s3.enabled',
            'Value': 'true'
        },
        {
            'Key': 'access_logs.s3.bucket',
            'Value': s3_bucket_name
        }
    ]
)

#----------------------------------------------------------

{
  "Id": "Policy1699339671294",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1699339659810",
      "Action": ["s3:*", "autoscaling-plans:*", "ec2:*", "elasticloadbalancing:*"],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::adarsh-boto3-s3",
      "Principal": "*"
    }
  ]
}

























