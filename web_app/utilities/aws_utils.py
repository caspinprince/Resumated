import io

import boto3
from botocore.client import Config
from PIL import Image
from web_app import celery, cache
import time

def crop_square(pil_img):
    img_width, img_height = pil_img.size
    crop_width = crop_height = min(pil_img.size)
    pil_img = pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )
    pil_img = pil_img.resize((300, 300))
    return pil_img

@celery.task(name='upload_pfp_to_s3')
def upload_pfp_to_s3(pfp_cache, bucket, file_name, content_type):
    image_file = cache.get(pfp_cache)
    cache.delete(pfp_cache)
    img_bytes = io.BytesIO()

    # compressing images and saving in a bytes object so no unecessary I/O is done
    crop_square(image_file).convert('RGB').save(img_bytes, format="JPEG", optimize=True, quality=20)
    byteArr = img_bytes.getvalue()
    session = boto3.session.Session()
    s3_client = session.client('s3', aws_access_key_id='AKIA4QN2U3BRYSBGFH53',
                        aws_secret_access_key='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', region_name='us-east-2', config=Config(signature_version='s3v4'))

    response = s3_client.put_object(
        Body=byteArr, Bucket=bucket, Key=file_name, ContentType=content_type
    )
    return response


def upload_doc_to_s3(doc_file, bucket, file_name, content_type):
    s3_client = boto3.client("s3")
    response = s3_client.put_object(
        Body=doc_file, Bucket=bucket, Key=file_name, ContentType=content_type
    )
    return response


def delete_object_s3(bucket, file_name):
    s3_client = boto3.client("s3")
    s3_client.delete_object(Bucket=bucket, Key=file_name)


def generate_url(bucket_name, object_name):
    session = boto3.session.Session()
    s3_client = session.client('s3', aws_access_key_id='AKIA4QN2U3BRYSBGFH53',
                        aws_secret_access_key='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', region_name='us-east-2', config=Config(signature_version='s3v4'))

    # presigned urls expire every day while cache expires every hour so urls are always fresh
    response = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": object_name}, ExpiresIn=86400
    )
    return response

