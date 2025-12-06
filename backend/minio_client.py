# backend/minio_client.py

import boto3

MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

# Create ONLY ONE bucket: models
def ensure_bucket(name):
    try:
        s3_client.create_bucket(Bucket=name)
    except:
        pass

ensure_bucket("models")
