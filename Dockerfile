
FROM python:3

ARG TRACKING_STORE="/mnt/mlflow_data"
ENV BACKEND_STORE_URI=$TRACKING_STORE

ARG ARTIFACT_STORE="s3://bucket"
ENV DEFAULT_ARTIFACT_ROOT=$ARTIFACT_STORE

ARG MLFLOW_S3_ENDPOINT_URL="http://localhost:9000"
ENV MLFLOW_S3_ENDPOINT_URL=$MLFLOW_S3_ENDPOINT_URL

RUN pip install -U mlflow==1.5.0
RUN pip install -U psycopg2 boto3
EXPOSE 5000
CMD mlflow server \
    --backend-store-uri $BACKEND_STORE_URI \
    --default-artifact-root $DEFAULT_ARTIFACT_ROOT \
    --host 0.0.0.0 --port 5000
