
from minio import Minio
from minio.error import ResponseError
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

import boto3
from botocore.client import Config

import mlflow
import os
import urllib

MINIO_URI = "localhost:9000"
MINIO_HTTP_URI = "http://"+MINIO_URI
os.environ['MLFLOW_S3_ENDPOINT_URL'] = MINIO_HTTP_URI
os.environ['AWS_ACCESS_KEY_ID'] = "your-key-id"
os.environ['AWS_SECRET_ACCESS_KEY'] = "your-secret"

MINIO_ACCESS_KEY="your-key-id"
MINIO_SECRET_KEY="your-secret"

MLFLOW_URI="http://localhost:5000"

def parse_uri_from_mlflow(uri):
    # uri from mlflow will be in format s3://artifacts/14/acdf9557954345f4b2156d438b39d868/artifacts
    parsed_uri = urllib.parse.urlparse(uri)
    if parsed_uri.scheme != 's3':
        raise Exception("expected s3 path")
    return parsed_uri.netloc, parsed_uri.path[1:]


def load_file_on_minio(client, bucket, filename, path):
    try:
       client.make_bucket(bucket, location="us-east-1")
    except BucketAlreadyOwnedByYou as err:
       pass
    except BucketAlreadyExists as err:
       pass
    except ResponseError as err:
       raise
    try:
        client.fput_object(bucket, filename, path)
    except ResponseError as err:
        print(err)


# with some version of python upload_file method from boto3
# which is used underneath with mlflow.log_artifact
# wait indefinitely even if upload succeded
def log_using_boto3_hang():
    EXP_NAME="BOTO"
    with open("boto_hang.txt", "w") as f:
        f.write("Hello boto!")
    
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXP_NAME)

    with mlflow.start_run():
        mlflow.log_param("boto3", 1)
        mlflow.log_artifact("boto_hang.txt")

# with some version of python boto3 wiht minio
# wait indefinitely even if upload succeded
def log_using_boto3():
    EXP_NAME="BOTOOK"
    s3 = boto3.resource('s3',
                    endpoint_url=MINIO_HTTP_URI,
                    aws_access_key_id=MINIO_ACCESS_KEY,
                    aws_secret_access_key=MINIO_SECRET_KEY,
                    config=Config(signature_version='s3v4'),
                    region_name='us-east-1')

    with open("boto.txt", "w") as f:
        f.write("Hello boto!")
    
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXP_NAME)

    with mlflow.start_run():
        mlflow.log_param("boto3", 1)
        artifact_path = mlflow.get_artifact_uri()
        print(artifact_path)
        bucket, bucket_path = parse_uri_from_mlflow(artifact_path)
        s3.Bucket(bucket).upload_file('boto.txt',bucket_path+'/'+'boto.txt')
        
    

def log_using_minio():
    EXP_NAME="MINIO"
    with open("minio.txt", "w") as f:
        f.write("Hello minio!")
    
    minioClient = Minio(MINIO_URI,
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET_KEY,
                  secure=False)

    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXP_NAME)

    with mlflow.start_run():
        mlflow.log_param("minio", 1)
        artifact_path = mlflow.get_artifact_uri()
        bucket, bucket_path = parse_uri_from_mlflow(artifact_path)
        load_file_on_minio(minioClient, bucket, bucket_path+'/'+"minio.txt", "./minio.txt")
    

if __name__ == '__main__':
    log_using_minio()
    # log_using_boto3() # hang on windows 10 with python(conda) 3.7
    # log_using_boto3_hang() # hang on windows 10 with python(conda) 3.7
    
