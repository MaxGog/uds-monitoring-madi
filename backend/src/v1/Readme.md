mc admin config set myminio notify_webhook:fastapi \
  endpoint="http://your-backend-api/api/v1/documents/webhook" \
  queue_limit="1000"

mc admin service restart myminio
mc event add myminio/documents arn:minio:sqs::fastapi:webhook --event put