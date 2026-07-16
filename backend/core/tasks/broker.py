import taskiq_redis
from dishka.integrations.taskiq import setup_dishka
from backend.core.ioc.container import create_task_container
from backend.config.config import settings

# broker = taskiq_redis.ListQueueBroker(
#     settings.redis.REDIS_URL,
#     protocol = 2,
#     socket_timeout=10,
#     socket_connect_timeout=10,
#     retry_on_timeout=True,
#     )

result_backend = taskiq_redis.RedisAsyncResultBackend(
    redis_url=settings.redis.REDIS_URL,
)

broker = taskiq_redis.RedisStreamBroker(
    url=settings.redis.REDIS_URL,
).with_result_backend(result_backend)


container = create_task_container()
from backend.src.v1.filesystem.infrastructure.parser_service.task import process_excel_import_task
setup_dishka(container, broker)

print(f"Зарегистрированные задачи: {list(broker.get_all_tasks())}")
# taskiq worker backend.core.tasks.broker:broker