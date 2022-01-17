import boto3

def upload_to_s3(image_file, bucket, file_name, content_type):
    s3_client = boto3.client('s3')
    response = s3_client.put_object(Body=image_file, Bucket=bucket, Key=file_name, ContentType=content_type)
    return response

def generate_url(bucket_name, object_name):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                           Params={'Bucket': bucket_name,
                                                                   'Key': object_name},
                                                           ExpiresIn=60)
    return response