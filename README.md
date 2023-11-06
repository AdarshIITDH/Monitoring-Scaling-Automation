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
# Initialize the S3 client
s3_client = boto3.client('s3')
region='ap-south-1'
# Define the bucket name
bucket_name = 'adarsh-s3'
# Create the S3 bucket
location = {'LocationConstraint': region}
s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
```

```
#----------------------Launch the EC2---------------------------------------
import boto3
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

# Wait for the instance to be running (optional)
ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
# You can also add tags to the instance for better management
ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': 'adarsh-boto3'}])

```
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/6d551c70-911c-4a2e-bb1c-acd1c37fde4d)
Web-server is up and running
![image](https://github.com/AdarshIITDH/Monitoring-Scaling-Automation/assets/60352729/6a3819c3-1b0d-4a61-9f2c-af4cf877fe60)

