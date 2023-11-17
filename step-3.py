'''
3. Auto Scaling Group (ASG) Configuration:
 - Using `boto3`, create an ASG with the deployed EC2 instance as a template.
 - Configure scaling policies to scale in/out based on metrics like CPU utilization or network 
traffic
'''

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


# # Check if the CSV file exists
# file_exists = False
# try:
#     with open('credientials.csv', 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if 'LaunchTemplateId' in row:
#                 file_exists = True
#                 break
# except FileNotFoundError:
#     pass

# # Update the 'credientials.csv' file with the Launch Template ID
# with open('credientials.csv', 'a', newline='') as csvfile:
#     fieldnames = ['LaunchTemplateId']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     # If the file doesn't exist or the column 'LaunchTemplateId' is not present, write the header
#     if not file_exists:
#         writer.writeheader()
#     # Write the Launch Template ID
#     writer.writerow({'LaunchTemplateId': launch_template_id})

# print(f"Launch Template ID '{launch_template_id}' added to 'credientials.csv'")
#-----------------------------------------------------


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
