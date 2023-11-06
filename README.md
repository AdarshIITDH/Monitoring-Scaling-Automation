# Monitoring-Scaling-Automation

### Overview

Develop a system that automatically manages the lifecycle of a web application hosted on  EC2 instances, monitors its health, and reacts to changes in traffic by scaling resources.  Furthermore, administrators receive notifications regarding the infrastructure's health and scaling events. 

Detailed Breakdown

1. Web Application Deployment
   - Use `boto3` to 
   - Create an S3 bucket to store your web application's static files. 
   - Launch an EC2 instance and configure it as a web server (e.g., Apache, Nginx).
   - Deploy the web application onto the EC2 instance.
  
```
#---------------------Creating a S3 bucket-----------------------------------------
import boto3
import csv
# Initialize the S3 client
s3_client = boto3.client('s3')
region='ap-south-1'
# Define the bucket name
bucket_name = 'adarsh-s3'
# Create the S3 bucket
location = {'LocationConstraint': region}
# s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
# # Get the bucket ARN
# response = s3_client.get_bucket_location(Bucket=bucket_name)
# bucket_location = response['LocationConstraint']
# s3_bucket = f'arn:aws:s3:::{bucket_name}'
#----------------------------------------------------------------------------------
```

```
#----------------------Launch the EC2---------------------------------------
ec2_client = boto3.client('ec2')
#configuring the webserver nginx
user_data_script = """#!/bin/bash
cd /home/ubuntu/
sudo apt update -y
sudo apt -y install git 
sudo apt install -y nginx
sudo git clone https://github.com/UnpredictablePrashant/TravelMemory.git
curl -s https://deb.nodesource.com/setup_18.x | sudo bash
sudo apt install nodejs -y
sudo apt-get update -y
"""
#Define the parameters for your EC2 instance
instance_params = {
    'ImageId': 'ami-08e5424edfe926b43',
    # 'groupId': 'sg-0103a917e74448c29',
    'InstanceType': 't2.micro',
    'KeyName': 'adarsh_key',
    # 'SecurityGroupIds': ['sg-0103a917e74448c29'],
    'MaxCount': 1,
    'MinCount': 1,
    'UserData': user_data_script,
}
#Launch the EC2 instance
instance = ec2_client.run_instances(**instance_params)
# Get the instance ID
instance_id = instance['Instances'][0]['InstanceId']
#storing the instance id in csv for future reference

# Check if the CSV file exists
file_exists = False
try:
    with open('credientials.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'Instance ID' in row:
                file_exists = True
                break
except FileNotFoundError:
    pass

# Create a list of dictionaries to hold the data
data = []
s3_bucket = 'your_s3_bucket'
# If the file doesn't exist or the column 'Instance ID' is not present, write the header
if not file_exists:
    data.append({'S3 Bucket': 'S3 Bucket', 'Instance ID': 'Instance ID'})

# Add the data to the list
data.append({'S3 Bucket': s3_bucket, 'Instance ID': instance_id})

# Write the data to the 'credientials.csv' file
with open('credientials.csv', 'w', newline='') as csvfile:
    fieldnames = ['S3 Bucket', 'Instance ID']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write the data
    for row in data:
        writer.writerow(row)

# Wait for the instance to be running (optional)
ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
# You can also add tags to the instance for better management
ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': 'adarsh-boto3'}])

#----------------------------------------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/6d551c70-911c-4a2e-bb1c-acd1c37fde4d)

Web-server is up and running
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/6a3819c3-1b0d-4a61-9f2c-af4cf877fe60)



2. Load Balancing with ELB:
    - Deploy an Application Load Balancer (ALB) using `boto3`.
    - Register the EC2 instance(s) with the ALB.

```
#---------------------target group-----------------------------
import boto3
import csv
client = boto3.client('elbv2', region_name='ap-south-1')
# Define the target group parameters
target_group_params = {
    'Name': 'adarsh-boto3-tg',  # Replace with your desired target group name
    'Protocol': 'HTTP',  # Use 'HTTPS' for HTTPS
    'Port': 80,  # Replace with your desired port
    'VpcId': 'vpc-0c5a8881cff1146d8',  # Replace with your VPC ID
}
# Create the target group
target_group_response = client.create_target_group(**target_group_params)
response1 = client.describe_target_groups(Names=['adarsh-boto3-tg'])
target_group_arn = response1['TargetGroups'][0]['TargetGroupArn']
# Get the target group ARN from the response
target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']


# Check if the CSV file exists
file_exists = False
#register instance with the target group
instances_to_register = []
# Read the CSV file
with open('credientials.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for column in reader:
        instance_id = column['Instance ID']
        instances_to_register.append(instance_id)

target_group_found = False  # To track if the "Target-Group" column is found

# Read the existing CSV file to check for the "Target-Group" column
with open('credientials.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames  # Get the existing field names
    if 'Target-Group' in fieldnames:
        target_group_found = True

# If the "Target-Group" column is not found, add it to the existing field names
if not target_group_found:
    fieldnames.append('Target-Group')

# Update the 'credientials.csv' file with the target group ARN
with open('credientials.csv', 'a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # If the "Target-Group" column was added, write the header
    if not target_group_found:
        writer.writeheader()

    # Prepare a dictionary with empty values for existing columns
    row_data = {column: '' for column in fieldnames}

    # Set the "Target-Group" value
    row_data['Target-Group'] = target_group_arn

    # Write the row to the CSV file
    writer.writerow(row_data)

# Now, the instances_to_register list contains the instance IDs

for instance_id in instances_to_register:
    client.register_targets(TargetGroupArn=target_group_arn, Targets=[{'Id': instance_id}])
#-----------------------------------------------------------------
```
```
#---------------------------Load Balancer------------------------
import boto3

client = boto3.client('elbv2', region_name='ap-south-1')

alb_params = {
    'Name':'adarsh-boto3-lb',
    'SecurityGroups': ['sg-0103a917e74448c29'],
    'Subnets':['subnet-0ea24e054cba9cad2','subnet-054d138c719f3f355','subnet-0ea185273ead71a27'],
    'Type':'application',
    # 'Scheme': 'internet-facing', 
}

response = client.create_load_balancer(**alb_params)
alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']

# Check if the CSV file exists
file_exists = False
alb_arn_found = False  # To track if the "ALB-ARN" column is found

# Read the existing CSV file to check for the "ALB-ARN" column
with open('credientials.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames  # Get the existing field names
    if 'ALB-ARN' in fieldnames:
        alb_arn_found = True

# If the "ALB-ARN" column is not found, add it to the existing field names
if not alb_arn_found:
    fieldnames.append('ALB-ARN')

# Update the 'credientials.csv' file with the ALB ARN
with open('credientials.csv', 'a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # If the "ALB-ARN" column was added, write the header
    if not alb_arn_found:
        writer.writeheader()

    # Prepare a dictionary with empty values for existing columns
    row_data = {column: '' for column in fieldnames}

    # Set the "ALB-ARN" value
    row_data['ALB-ARN'] = alb_arn

    # Write the row to the CSV file
    writer.writerow(row_data)

# Check the CSV file after writing the ALB ARN
with open('credientials.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row)

# Create a listener for the ALB to route traffic to the target group
listener_params = {
    'LoadBalancerArn': alb_arn,
    'Port': 80,  # Replace with the port you want to use
    'Protocol': 'HTTP',  # Use 'HTTPS' for HTTPS
    'DefaultActions': [
        {
            'Type': 'forward',
            'TargetGroupArn': target_group_arn  # Point the listener to the target group
        }
    ]
}
client.create_listener(**listener_params)
#------------------------------------------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/c4d6aedd-c3fc-48e4-a747-77171cfe57a3)

![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/56b6b0c1-5b6f-4a4d-b320-a54982a35dd2)
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/708a9c1e-0921-4d05-868b-a4438dbffbe0)

3. Auto Scaling Group (ASG) Configuration:
 - Using `boto3`, create an ASG with the deployed EC2 instance as a template.
 - Configure scaling policies to scale in/out based on metrics like CPU utilization or network traffic

```
#----------------------EC2 Template configuration-------------------------------------------------------
import boto3
import csv
region='ap-south-1'
# Create the EC2 template 

# Initialize the EC2 client
ec2_client = boto3.client('ec2', region_name= region)

# EC2 instance ID to use as a template
instance_id = 'i-0f33853ceec6bac22'

# Describe the instance to get its configuration details
response = ec2_client.describe_instances(InstanceIds=[instance_id])

# Extract the instance details
instance = response['Reservations'][0]['Instances'][0]
instance_type = instance['InstanceType']
ami_id = instance['ImageId']
key_name = instance.get('adarsh_key')  # Key pair name
security_group_ids = [sg['GroupId'] for sg in instance['SecurityGroups']]
subnet_id = instance['SubnetId']

# Create a launch template using the instance's configuration
launch_template_name = 'adarsh-boto3-template'
launch_template = ec2_client.create_launch_template(
    LaunchTemplateName=launch_template_name,
    VersionDescription='Initial version',
    LaunchTemplateData={
        'InstanceType': instance_type,
        'ImageId': ami_id,
        'KeyName': 'adarsh_key',
        'SecurityGroupIds': security_group_ids,
    }
)

# Extract the launch template ID
launch_template_id = launch_template['LaunchTemplate']['LaunchTemplateId']
#------------------------------------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/8b8f3c97-8143-49d0-a136-896f1f462bb7)

```
#--------------------ASG Configuration-------------------------------------

region='ap-south-1'
# Initialize the Auto Scaling client
autoscaling_client = boto3.client('autoscaling', region_name= region)

# Define the Auto Scaling Group configuration
asg_params = {
    'AutoScalingGroupName': 'adarsh-boto3-asg',
    'LaunchTemplate': {
        'LaunchTemplateName': launch_template_name,
    },
    'MinSize': 1,  # Minimum number of instances
    'MaxSize': 3,  # Maximum number of instances
    'DesiredCapacity': 1,  # Desired number of instances
    'AvailabilityZones': ['ap-south-1a','ap-south-1b','ap-south-1c'],  # Define your availability zones
    # Other parameters as needed
}

# Create the Auto Scaling Group
response = autoscaling_client.create_auto_scaling_group(**asg_params)
print(f"Auto Scaling Group '{asg_params['AutoScalingGroupName']}' created with Launch Template ID '{launch_template_id}'")
#-----------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/2aebd522-2f38-45df-888f-205e278a9611)

```
#---------------------Scaling Policy--------------------------------
# Define the scaling policy parameters
scaling_policy_params = {
    'AutoScalingGroupName': 'adarsh-boto3-asg',  
    'PolicyName': 'adarsh-boto3-asgp',  
    'PolicyType': 'TargetTrackingScaling', 
    # 'AdjustmentType': 'ChangeInCapacity',
    # 'ScalingAdjustment': 1,  # Adjust by 1 instance
    # 'Cooldown': 60,  # Cooldown period in seconds
    'TargetTrackingConfiguration': {
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization',
            # 'ResourceLabel': 'app/adarsh-neeraj-lb/b75d821e7370c5cd/targetgroup/adarsh-neeraj-tg/640d9f378acdbef4',
        },
        'TargetValue': 70,
    },
}
#-----------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/b77f7f60-eb33-47d9-8521-564820218618)

4. Lambda-based Health Checks & Management:
    - Develop a Lambda function to periodically check the health of the web application(through the ALB).
    - If the health check fails consistently, the Lambda function should:
    - Capture a snapshot of the failing instance for debugging purposes.
    - Terminate the problematic instance, allowing the ASG to replace it.
    - Send a notification through SNS to the administrators.

```
#----------------------SNS Topic ------------------------------------
import boto3
# Initialize the SNS client
sns_client = boto3.client('sns', region_name='ap-south-1') 

# Define the SNS topic name
topic_name = 'adarsh-boto3-sns'

# Create the SNS topic
response = sns_client.create_topic(Name=topic_name)

# Extract the ARN (Amazon Resource Name) of the created SNS topic
topic_arn = response['TopicArn']

print(f'SNS topic created with ARN: {topic_arn}')

# Specify the protocol and endpoint (email address in this case)
protocol = 'email'
endpoint = 'adarsh307kumar@gmail.com'

# Create the subscription
sns_client.subscribe(
    TopicArn=topic_arn,
    Protocol=protocol,
    Endpoint=endpoint
)
#------------------------------------------------------------------------
```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/ce0411a9-ba33-484f-bb2b-cf266430c18f)


