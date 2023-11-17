'''
1. Web Application Deployment:
 - Use `boto3` to:
 - Create an S3 bucket to store your web application's static files.
 - Launch an EC2 instance and configure it as a web server (e.g., Apache, Nginx).
 - Deploy the web application onto the EC2 instance.
'''

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













