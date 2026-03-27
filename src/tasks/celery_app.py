import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "public_notice_bot",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.tasks.crawler_tasks"],
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    beat_schedule={
        "crawl-all-daily": {
            "task": "src.tasks.crawler_tasks.crawl_all_task",
            "schedule": 86400,
        },
    },
)
