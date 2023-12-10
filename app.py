import requests
import boto3
from datetime import datetime

# GitHub API endpoint for Apache Hadoop repository
github_api_url = "https://api.github.com/repos/apache/hadoop/stats/contributors"

aws_access_key_id = 'AKIAXCWMEHTAR4FWNARJ'
aws_secret_access_key = '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'
aws_region = 'eu-north-1'
dynamodb_table_name = 'Matrix_1'

# Function to retrieve data from GitHub API
def get_github_data():
    response = requests.get(github_api_url)
    return response.json()

# Function to format data and create a table
def create_table_data(github_data):
    table_data = []
    for contributor in github_data:
        for week_data in contributor["weeks"]:
            date = datetime.utcfromtimestamp(week_data["w"]).strftime('%Y-%m-%d')
            user = contributor["author"]["login"]
            commits = week_data["c"]
            table_data.append({"Date": date, "User": user, "Commits": commits})
    return table_data

# Function to deploy data to AWS DynamoDB
def deploy_to_dynamodb(table_data):
    dynamodb = boto3.resource("dynamodb", region_name=aws_region,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table(dynamodb_table_name)
    for item in table_data[:10]:
        table.put_item(Item=item)
        print(item)

def main():
    github_data = get_github_data()
    table_data = create_table_data(github_data)
    deploy_to_dynamodb(table_data)

if __name__ == "__main__":
    main()