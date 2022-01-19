import boto3
import os
import io
import glob
from PIL import Image

def crop_square(pil_img):
    img_width, img_height = pil_img.size
    crop_width = crop_height = min(pil_img.size)
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def upload_pfp_to_s3(image_file, bucket, file_name, content_type):
    img_bytes = io.BytesIO()
    image = crop_square(Image.open(image_file)).save(img_bytes, format='PNG')
    byteArr = img_bytes.getvalue()
    s3_client = boto3.client('s3')
    response = s3_client.put_object(Body=byteArr, Bucket=bucket, Key=file_name, ContentType=content_type)
    return response

def upload_doc_to_s3(doc_file, bucket, file_name, content_type):
    s3_client = boto3.client('s3')
    response = s3_client.put_object(Body=doc_file, Bucket=bucket, Key=file_name, ContentType=content_type)
    return response

def generate_url(bucket_name, object_name):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                           Params={'Bucket': bucket_name,
                                                                   'Key': object_name},
                                                           ExpiresIn=60)
    return response