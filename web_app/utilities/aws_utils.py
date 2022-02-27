import io

import boto3
from botocore.client import Config
from PIL import Image


def crop_square(pil_img):
    img_width, img_height = pil_img.size
    crop_width = crop_height = min(pil_img.size)
    return pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )


def upload_pfp_to_s3(image_file, bucket, file_name, content_type):
    img_bytes = io.BytesIO()
    crop_square(Image.open(image_file)).save(img_bytes, format="PNG")
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
    response = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": object_name}, ExpiresIn=86400
    )
    return response

