# your_project/__init__.py
from __future__ import absolute_import, unicode_literals

# Это необходимо для того, чтобы запустился Celery при старте проекта
from .celery import app as celery_app

__all__ = ('celery_app',)
