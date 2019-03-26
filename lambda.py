import boto3

def handler(event,context):
    client = boto3.client('ecs')
    response = client.run_task(
        cluster='default',
        launchType = 'FARGATE',
        taskDefinition='postgres-backup-dev',
        count = 1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    "subnet-01479b4d"
                ],
                'assignPublicIp': 'ENABLED'
            }
        }
    )
    return str(response)
