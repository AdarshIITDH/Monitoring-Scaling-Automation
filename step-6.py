'''
6. SNS Notifications: 
 - Set up different SNS topics for different alerts (e.g., health issues, scaling events, high traffic). 
 - Integrate SNS with Lambda so that administrators receive SMS or email notifications. 
'''

#-----------------------SNS Topics for different alerts---------------------------
import boto3

# Initialize SNS client
sns_client = boto3.client('sns', region_name='ap-south-1')
# Specify the email address for subscription
email_address = 'adarsh307kumar@gmail.com'

# Create an SNS topic for health issues
health_topic = sns_client.create_topic(Name='adarsh-boto3-HealthIssuesTopic')
health_topic_arn = health_topic['TopicArn']

# Create an SNS topic for scaling events
scaling_topic = sns_client.create_topic(Name='adarsh-boto3-ScalingEventsTopic')
scaling_topic_arn = scaling_topic['TopicArn']

# Create an SNS topic for high traffic alerts
high_traffic_topic = sns_client.create_topic(Name='adarsh-boto3-HighTrafficTopic')
high_traffic_topic_arn = high_traffic_topic['TopicArn']

# Print the ARNs of the created topics
print(f"Health Issues Topic ARN: {health_topic_arn}")
print(f"Scaling Events Topic ARN: {scaling_topic_arn}")
print(f"High Traffic Topic ARN: {high_traffic_topic_arn}")

# Subscribe the email address to the health issues topic
sns_client.subscribe(
    TopicArn=health_topic_arn,
    Protocol='email',
    Endpoint=email_address
)

# Subscribe the email address to the scaling events topic
sns_client.subscribe(
    TopicArn=scaling_topic_arn,
    Protocol='email',
    Endpoint=email_address
)

# Subscribe the email address to the high traffic topic
sns_client.subscribe(
    TopicArn=high_traffic_topic_arn,
    Protocol='email',
    Endpoint=email_address
)

#--------------------------------------------------

#--------------------------------------------------










#--------------------------------------------------

















