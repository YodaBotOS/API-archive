import boto3

import config


def init_cli(s3: bool = False):
    if s3:
        return boto3.client(
            "s3",
            aws_access_key_id=config.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.S3_AWS_SECRET_ACCESS_KEY,
            region_name=config.S3_BUCKET_REGION,
        )

    return boto3.client(
        "s3",
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        endpoint_url=config.R2_ENDPOINT_URL,
    )
