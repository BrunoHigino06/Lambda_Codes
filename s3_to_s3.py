import json
import boto3
s3 = boto3.client('s3')
def lambda_handler(event, context):
    destination = 'bucketdestnation202111'

    #Colect the name of source bucket (that trigged the lambdafunction)
    source = event['Records'][0]['s3']['bucket']['name']

    #Colect the name of file that is put in the bucket
    file_name = event['Records'][0]['s3']['object']['key']

    #Copy object to a destination bucket
    copy_source_object = {'Bucket': source, 'Key': file_name}
    s3.copy_object(CopySource=copy_source_object, Bucket=destination, Key=file_name)