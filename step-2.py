'''
2. Load Balancing with ELB:
 - Deploy an Application Load Balancer (ALB) using `boto3`.
 - Register the EC2 instance(s) with the ALB.
'''

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
# listener_params = {
#     'DefaultActions': [{'Type': 'fixed-response', 'FixedResponseConfig': {'ContentType': 'text/plain', 'StatusCode': '200', 'ContentType': 'text/plain', 'Content': 'OK'}}],  # You can modify this as needed
#     'LoadBalancerArn': alb_arn,
#     'Port': 80,  # Replace with the port you want to use
#     'Protocol': 'HTTP',  # Use 'HTTPS' for HTTPS
#     'DefaultActions': [{'Type': 'fixed-response', 'FixedResponseConfig': {'ContentType': 'text/plain', 'StatusCode': '200', 'ContentType': 'text/plain', 'Content': 'OK'}}],  # Modify this action as needed
# }
listener_params = {
    'LoadBalancerArn': alb_arn,
    'Port': 80,  # Replace with the port you want to use
    'Protocol': 'HTTP',  # Use 'HTTPS' for HTTPS
    'DefaultActions': [
        # {
        #     'Type': 'fixed-response',
        #     'FixedResponseConfig': {
        #         'ContentType': 'text/plain',
        #         'StatusCode': '200',
        #         'ContentType': 'text/plain',
        #         # 'Content': 'OK'
                
        #     }
            
        # },
        {
            'Type': 'forward',
            'TargetGroupArn': target_group_arn  # Point the listener to the target group
        }
    ]
}

client.create_listener(**listener_params)


#------------------------------------------------------------------------------------

















