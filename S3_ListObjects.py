import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'media-ingest-temporary'
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        all_objects = []
        continuation_token = None

        while True:
            if continuation_token:
                response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=continuation_token
                )
            else:
                response = s3.list_objects_v2(Bucket=bucket_name)

            # Filter objects by .mp4 extension and current date
            filtered_objects = [
                {'Key': obj['Key'], 'LastModified': obj['LastModified'].isoformat()}
                for obj in response.get('Contents', [])
                if obj['Key'].endswith('.mp4') and obj['LastModified'].strftime('%Y-%m-%d') == current_date
            ]

            # Append filtered objects to the list
            all_objects.extend(filtered_objects)

            # Check if there are more objects to fetch
            if 'NextContinuationToken' in response:
                continuation_token = response['NextContinuationToken']
            else:
                break

        return {
            'statusCode': 200,
            'body': json.dumps(all_objects)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
