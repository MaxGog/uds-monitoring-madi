import json
import uuid
from celery import Celery
from redis import Redis


celery_app = Celery('sync_tasks', broker='redis://localhost:6379/0')
redis_client = Redis(host='localhost', port=6379, db=0)


# Набросок ИИ кода, нужно внимательно всё будет отрефакторить для синхронизации БД
@celery_app.task(name="tasks.minio_event_listener")
def listen_minio_events():
    """
    Долгоживущая задача Celery. Рекомендуется запускать в отдельном пуле 
    или через Celery Beat один раз при старте воркера.
    """
    print("Старт прослушивания событий MinIO...")
    while True:
        # Блокирующее чтение из ключа, куда MinIO отправляет уведомления (например, 'minio_events')
        # timeout=5 позволяет периодически разрывать блок для проверки сигналов завершения
        packed_event = redis_client.blpop("minio_events", timeout=5)
        if not packed_event:
            continue
            
        _, raw_json = packed_event
        event_data = json.loads(raw_json)
        
        # S3 Event Notification формат всегда содержит массив "Records"
        for record in event_data.get("Records", []):
            event_name = record.get("eventName", "")

            if "ObjectCreated" in event_name:
                s3_metadata = record.get("s3", {})
                object_key = s3_metadata.get("object", {}).get("key")
                file_size = s3_metadata.get("object", {}).get("size")
                
                try:
                    file_uuid = uuid.UUID(object_key)
                except ValueError:
                    continue
                
                # Синхронизируем состояние с PostgreSQL
                with SessionLocal() as session:
                    with session.begin():
                        db_file = session.query(DBFile).filter(DBFile.id == file_uuid).first()
                        
                        # Обновление только если запись существовала и была в статусе pending
                        if db_file and db_file.status == FileStatus.PENDING:
                            db_file.status = FileStatus.SUCCESS
                            db_file.size = file_size
                            # Если необходимо, здесь же можно запустить цепочку тяжелых задач (например, парсинг)
                            # run_file_parsing.delay(str(db_file.id))