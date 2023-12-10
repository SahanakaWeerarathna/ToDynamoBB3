# Date , User , Branches created

import requests
import boto3
from datetime import datetime

# GitHub API endpoint for repository events
repository_owner = "apache"
repository_name = "hadoop"
github_api_url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/events"

# AWS DynamoDB table details
dynamodb_table_name = "MATRIX_3"
aws_region = "eu-north-1"
aws_access_key_id = "AKIAXCWMEHTAR4FWNARJ"
aws_secret_access_key = "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"

def get_repository_events():
    response = requests.get(github_api_url)
    if response.status_code == 200:
        events = response.json()
        return events
    else:
        print(f"Failed to fetch GitHub events. Status Code: {response.status_code}")
        return None

def process_events(events):
    user_branches_created = {}

    for event in events:
        actor_login = event['actor']['login']
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

        if event['type'] == 'CreateEvent' and event['payload']['ref_type'] == 'branch':
            if actor_login in user_branches_created:
                user_branches_created[actor_login]['branches_created'] += 1
            else:
                user_branches_created[actor_login] = {'date': event_date, 'branches_created': 1}

    return user_branches_created

def insert_into_dynamodb(data):
    dynamodb = boto3.resource('dynamodb', region_name=aws_region,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)

    table = dynamodb.Table(dynamodb_table_name)

    for user, user_data in data.items():
        print(user_data['date'],user,user_data['branches_created'])
        table.put_item(Item={
            'primarykey': str(user_data['date'])+"_"+user,
            'Date': user_data['date'],
            'User': user,
            'Branches_Created': user_data['branches_created']
        })

# Main script
def maindefm3():
    # Fetch GitHub events for the Apache Hadoop repository
    repository_events = get_repository_events()

    if repository_events:
        # Process events and count branches created for each user
        user_branches_created = process_events(repository_events)

        # Insert data into DynamoDB
        insert_into_dynamodb(user_branches_created)

