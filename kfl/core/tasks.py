# tasks.py
from celery import shared_task
from datetime import datetime
from .models import Matches

@shared_task
def update_match_status():
    now = datetime.now()
    # Найдем матчи, которые еще не начались и у которых время уже пришло
    matches = Matches.objects.filter(
        status='Не начался',
        date_match__lte=now.date(),
        time_match__lte=now.time()
    )
    # Обновим статус матчей
    matches.update(status='В процессе')
