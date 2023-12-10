# Date , User , Total responsible events

import requests
import boto3
from datetime import datetime

# GitHub API endpoint for repository events
repository_owner = "apache"
repository_name = "hadoop"
github_api_url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/events"

# AWS DynamoDB table details
dynamodb_table_name = "MATRIX_1"
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

def count_events_for_users(events):
    user_events_count = {}

    for event in events:
        actor_login = event['actor']['login']
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

        if actor_login in user_events_count:
            user_events_count[actor_login]['event_count'] += 1
        else:
            user_events_count[actor_login] = {'date': event_date, 'event_count': 1}

    return user_events_count

def insert_into_dynamodb(data):
    dynamodb = boto3.resource('dynamodb', region_name=aws_region,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)

    table = dynamodb.Table(dynamodb_table_name)

    for user, user_data in data.items():
        print(str(user_data['date'])+"_"+user,user_data['date'],user,user_data['event_count'])

        table.put_item(Item={
            'primarykey': str(user_data['date'])+"_"+user
            'Date': user_data['date'],
            'User': user,
            'Event_Count': user_data['event_count']
        })



repository_events = get_repository_events()

if repository_events:
    # Count events for each user
    user_events_count = count_events_for_users(repository_events)

    # Insert data into DynamoDB
    insert_into_dynamodb(user_events_count)
    print("Data inserted into DynamoDB successfully.")
