from django.db.models.signals import post_save, post_delete,pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import EventsMathes, Matches, Standings, StaticticsPlayerSeason, EventsMathes

# Обновление статистики игроков при добавлении события матча (голы, карточки и т.д.)
@receiver(post_save, sender=EventsMathes)
def update_player_statistics(sender, instance, created, **kwargs):
    if not created:  
        return  # Если событие не новое, выходим

    # Получаем или создаем запись статистики игрока
    player_stats, created = StaticticsPlayerSeason.objects.get_or_create(
        player=instance.player,
        tournament=instance.match.tournament,
        season=instance.match.season,
        defaults={'goals': 0, 'assists': 0, 'yellow_cards': 0, 'red_cards': 0, 'games': 0}
    )

    # Обновляем соответствующее поле в зависимости от типа события
    event_mapping = {
        EventsMathes.EventChoices.GOAL: "goals",
        EventsMathes.EventChoices.ASSIST: "assists",
        EventsMathes.EventChoices.YELLOW_CARD: "yellow_cards",
        EventsMathes.EventChoices.RED_CARD: "red_cards",
    }

    if instance.event in event_mapping:
        field_name = event_mapping[instance.event]
        setattr(player_stats, field_name, getattr(player_stats, field_name) + 1)
        player_stats.save()


# Автоматическое обновление турнирной таблицы после завершения матча
@receiver(post_save, sender=Matches)
def update_standings_after_match(sender, instance, **kwargs):
    if instance.status == "Закончен":
        home_team, _ = Standings.objects.get_or_create(
            team=instance.home_team, 
            tournament=instance.tournament, 
            season=instance.season
        )
        away_team, _ = Standings.objects.get_or_create(
            team=instance.away_team, 
            tournament=instance.tournament, 
            season=instance.season
        )

        home_team.games += 1
        away_team.games += 1

        home_goals = instance.home_goals or 0  # Если None, то 0
        away_goals = instance.away_goals or 0  # Если None, то 0

        home_team.goals_scored += home_goals
        home_team.goals_conceded += away_goals

        away_team.goals_scored += away_goals
        away_team.goals_conceded += home_goals

        if home_goals > away_goals:
            home_team.wins += 1
            home_team.points += 3
            away_team.losses += 1
        elif home_goals < away_goals:
            away_team.wins += 1
            away_team.points += 3
            home_team.losses += 1
        else:
            home_team.draws += 1
            away_team.draws += 1
            home_team.points += 1
            away_team.points += 1

        home_team.goals_difference = home_team.goals_scored - home_team.goals_conceded
        away_team.goals_difference = away_team.goals_scored - away_team.goals_conceded

        home_team.save()
        away_team.save()


@receiver(post_save, sender=EventsMathes)
def update_match_score(sender, instance, created, **kwargs):
    if created and instance.match.status == "В процессе" and instance.event == "Гол":
        match = instance.match  # Получаем матч

        # Проверяем, что значения не None, иначе присваиваем 0
        match.home_goals = match.home_goals if match.home_goals is not None else 0
        match.away_goals = match.away_goals if match.away_goals is not None else 0

        # Увеличиваем счет в зависимости от команды игрока
        if instance.player.team == match.home_team:
            match.home_goals += 1
        elif instance.player.team == match.away_team:
            match.away_goals += 1

        match.save()  # Сохраняем обновленный счет

@receiver(post_save, sender=Matches)
def update_match_status(sender, instance, **kwargs):
    now = timezone.localtime(timezone.now())  # Учитываем локальное время
    match_datetime = timezone.make_aware(
        timezone.datetime.combine(instance.date_match, instance.time_match)
    )  # Создаем объект даты-времени матча

    print(f"Проверка матча {instance.id} | Дата: {instance.date_match}, Время: {instance.time_match} | Сейчас: {now}")

    # Проверяем, если матч должен был начаться, но статус не изменился
    if instance.status == 'Не начался' and now >= match_datetime:
        instance.status = 'В процессе'
        instance.save(update_fields=['status'])  # Обновляем только статус
        print(f"✅ Статус матча {instance.id} изменен на 'В процессе'")


@receiver(post_save, sender=EventsMathes)
def handle_yellow_cards(sender, instance, created, **kwargs):
    # Проверяем, что событие - желтая карточка
    if instance.event == EventsMathes.EventChoices.YELLOW_CARD:
        # Получаем все события для этого игрока в текущем матче
        events = EventsMathes.objects.filter(player=instance.player, match=instance.match)

        # Считаем количество желтых карточек
        yellow_count = events.filter(event=EventsMathes.EventChoices.YELLOW_CARD).count()

        if yellow_count == 2:  # Если 2 желтые карточки
            # Создаем красную карточку
            EventsMathes.objects.create(
                match=instance.match,
                player=instance.player,
                event=EventsMathes.EventChoices.RED_CARD,
                time=instance.time  # или другое время, как нужно
            )