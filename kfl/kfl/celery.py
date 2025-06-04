from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем конфигурацию Celery из Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfl.settings')

app = Celery('kfl')

# Используем строковую запись для загрузки конфигурации
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем задачи в приложениях
app.autodiscover_tasks()