"""
Lambda function to list .mp4 files uploaded to an S3 bucket on a specific date,
generate a JSON report including file details and total count, and save the report
to S3 under a specified folder.

Script Workflow:
1. Retrieves current date and initializes AWS S3 client.
2. Lists objects in 'media-ingest-temporary' bucket filtered by .mp4 extension and current date.
3. Collects details (Key, LastModified) of filtered objects.
4. Constructs a JSON report including total count and file details.
5. Saves the JSON report to 'report/mp4_objects_<current_date>.json' in the S3 bucket.
6. Returns a JSON response with HTTP status code 200 if successful, including the JSON report.
   Returns a JSON response with HTTP status code 500 in case of errors, including error details.
"""
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

        # Include the total count at the beginning of the JSON data
        output_data = {
            'total_files': len(all_objects),
            'files': all_objects
        }

        # Convert the output data to JSON with pretty-printing and save to S3
        json_data = json.dumps(output_data, indent=4)  # Add indent parameter here
        file_key = f"report/mp4_objects_{current_date}.json"

        s3.put_object(Bucket=bucket_name, Key=file_key, Body=json_data)

        return {
            'statusCode': 200,
            'body': json.dumps(output_data, indent=4)  # Add indent parameter here
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}, indent=4)  # Add indent parameter here
        }
