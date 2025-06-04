from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models

class Teams(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название команды')
    logo = models.ImageField(upload_to='teams/', verbose_name='Логотип команды',null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name='Город',null=True, blank=True)
    stadium = models.CharField(max_length=100, verbose_name='Стадион',null=True, blank=True)
    coach = models.CharField(max_length=100, verbose_name='Тренер',null=True, blank=True)
    founded_year = models.IntegerField(verbose_name='Год основания',null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Management(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name='Команда')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    position = models.CharField(max_length=100, verbose_name='Должность')
    photo = models.ImageField(upload_to='management/', verbose_name='Фото',null=True, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = 'Руководство команды'
        verbose_name_plural = 'Руководство команды'


class Players(models.Model):

    class PositionChoices(models.TextChoices):
        GOALKEEPER = 'Вратарь'
        DEFENDER = 'Защитник'
        MIDFIELDER = 'Полузащитник'
        FORWARD = 'Нападающий'

    team = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name='Команда')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    photo = models.ImageField(upload_to='players/', verbose_name='Фото',null=True, blank=True)
    birth_date = models.DateField(verbose_name='Дата рождения',null=True, blank=True)
    position = models.CharField(max_length=100, choices=PositionChoices.choices, verbose_name='Позиция',null=True, blank=True)
    number = models.IntegerField(verbose_name='Номер',null=True, blank=True)
    height = models.IntegerField(verbose_name='Рост',null=True, blank=True)
    weight = models.IntegerField(verbose_name='Вес',null=True, blank=True)
    nationality = models.CharField(max_length=100, verbose_name='Национальность',null=True, blank=True)
    goals = models.IntegerField(verbose_name='Голы',null=True, blank=True)
    assists = models.IntegerField(verbose_name='Пасы',null=True, blank=True)
    yellow_cards = models.IntegerField(verbose_name='Желтые карточки',null=True, blank=True)
    red_cards = models.IntegerField(verbose_name='Красные карточки',null=True, blank=True)
    games = models.IntegerField(verbose_name='Игры',null=True, blank=True)
    minutes = models.IntegerField(verbose_name='Минуты',null=True, blank=True)

    def __str__(self):
        return f"{self.team.name} - {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class Tournament(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название турнира')
    logo = models.ImageField(upload_to='tournaments/', verbose_name='Логотип турнира', null=True, blank=True)
    country = models.CharField(max_length=100, verbose_name='Страна', null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

class Season(models.Model):
    year = models.IntegerField(unique=True, verbose_name='Сезон')
    is_current = models.BooleanField(default=False, verbose_name='Текущий')
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")

    def save(self, *args, **kwargs):
        if self.is_current:
            # Проверяем, есть ли уже текущий сезон, кроме самого себя (при редактировании)
            current_season = Season.objects.filter(is_current=True).exclude(id=self.id).first()
            if current_season:
                raise ValidationError("Уже есть текущий сезон. Отключите его перед установкой нового.")
        
        super().save(*args, **kwargs)  # Сохраняем, если всё нормально

    def __str__(self):
        return f"{self.year}"

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир", related_name="rounds")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Сезон", related_name="rounds")
    round_number = models.PositiveIntegerField(verbose_name="Номер тура")


    def __str__(self):
        return f"{self.tournament.name} {self.season.year} - Тур {self.round_number}"

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ["round_number"]

class Stadium(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название стадиона')
    city = models.CharField(max_length=100, verbose_name='Город')
    capacity = models.IntegerField(verbose_name='Вместимость')
    adress = models.CharField(null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стадион'
        verbose_name_plural = 'Стадионы'

class Matches(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир", related_name="matches")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Сезон", related_name="matches")
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, verbose_name="Стадион", related_name="matches")
    round = models.ForeignKey(Round, on_delete=models.CASCADE, verbose_name="Тур", related_name="matches", null=True, blank=True)
    home_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='home_matches', verbose_name='Хозяева')
    away_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='away_matches', verbose_name='Гости')
    date_match = models.DateField(verbose_name='Дата матча', null=True, blank=True)
    time_match = models.TimeField(verbose_name='Время матча', null=True, blank=True)
    home_goals = models.IntegerField(verbose_name='Голы хозяев', null=True, blank=True)
    away_goals = models.IntegerField(verbose_name='Голы гостей', null=True, blank=True)
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, verbose_name="Стадион", related_name="matches")
    technical_defeat = models.BooleanField(default=False, verbose_name='Техническое поражение')
    status = models.CharField(
        max_length=100,
        choices=[
            ('Не начался', 'Не начался'),
            ('В процессе', 'В процессе'),
            ('Закончен', 'Закончен')
        ],
        verbose_name='Статус', default='Не начался', null=True, blank=True
    )
    mvp = models.ForeignKey(Players, on_delete=models.CASCADE, verbose_name='Лучший игрок', null=True, blank=True)
    documents = models.FileField(upload_to='documents/', verbose_name='Документы', null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.tournament.name} {self.season.year})"

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'

class MatchLineup(models.Model):
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name="lineups", verbose_name="Матч")
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name="lineups", verbose_name="Команда")
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name="lineups", verbose_name="Игрок")
    
    is_starting = models.BooleanField(default=False, verbose_name="В стартовом составе")
    is_substitute = models.BooleanField(default=False, verbose_name="Запасной")

    def __str__(self):
        return f"{self.team.name}) - {self.match}"

    class Meta:
        verbose_name = "Состав матча"
        verbose_name_plural = "Составы матчей"

class EventsMathes(models.Model):

    class EventChoices(models.TextChoices):
        GOAL = 'Гол'
        ASSIST = 'Пас'
        YELLOW_CARD = 'Желтая карточка'
        RED_CARD = 'Красная карточка'
        NO_PENALTY = 'Незабитый пенальти'
        PENALTY = 'Забитый пенальти'
        SUBSTITUTION = 'Замена'
        AUTO_GOAL = 'Автогол'
        INJURY = 'Травма'

    match = models.ForeignKey(Matches, on_delete=models.CASCADE, verbose_name='Матч')
    player = models.ForeignKey(Players, on_delete=models.CASCADE, verbose_name='Игрок')
    event = models.CharField(max_length=100, choices=EventChoices.choices, verbose_name='Событие')
    time = models.PositiveIntegerField(
        verbose_name='Минута матча',
        validators=[MinValueValidator(0), MaxValueValidator(130)]
    )

    def __str__(self):
        return f"{self.time}’ {self.player.first_name} {self.player.last_name} - {self.event}"

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class StaticticsPlayerSeason(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE, verbose_name='Игрок')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир", related_name="player_stats")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Сезон", related_name="player_stats")
    goals = models.IntegerField(verbose_name='Голы',null=True, blank=True)
    assists = models.IntegerField(verbose_name='Пасы',null=True, blank=True)
    yellow_cards = models.IntegerField(verbose_name='Желтые карточки',null=True, blank=True)
    red_cards = models.IntegerField(verbose_name='Красные карточки',null=True, blank=True)
    games = models.IntegerField(verbose_name='Игры',null=True, blank=True)
    minutes = models.IntegerField(verbose_name='Минуты',null=True, blank=True)

    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name} - {self.tournament.name} {self.season.year}"

    class Meta:
        verbose_name = 'Статистика игрока за сезон'
        verbose_name_plural = 'Статистика игроков за сезон'


class SeasonAwards(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Сезон", related_name="awards")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир", related_name="awards")

    best_scorer = models.ForeignKey(
        Players, on_delete=models.SET_NULL, verbose_name="Лучший бомбардир", null=True, blank=True, related_name="best_scorer"
    )
    best_goalkeeper = models.ForeignKey(
        Players, on_delete=models.SET_NULL, verbose_name="Лучший вратарь", null=True, blank=True, related_name="best_goalkeeper"
    )
    best_coach = models.ForeignKey(
        Management, on_delete=models.SET_NULL, verbose_name="Лучший тренер", null=True, blank=True, related_name="best_coach"
    )
    best_team = models.ForeignKey(
        Teams, on_delete=models.SET_NULL, verbose_name="Лучшая команда", null=True, blank=True, related_name="best_team"
    )
    best_player = models.ForeignKey(
        Players, on_delete=models.SET_NULL, verbose_name="Лучший игрок сезона", null=True, blank=True, related_name="best_player"
    )

    def __str__(self):
        return f"Аварды {self.tournament.name} {self.season.year}"

    class Meta:
        verbose_name = "Награды сезона"
        verbose_name_plural = "Награды сезона"



class Standings(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name='Команда')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир", related_name="standings")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="Сезон", related_name="standings")
    games = models.IntegerField(verbose_name='Игры',null=True, blank=True)
    wins = models.IntegerField(verbose_name='Победы')
    draws = models.IntegerField(verbose_name='Ничьи')
    losses = models.IntegerField(verbose_name='Поражения')
    goals_scored = models.IntegerField(verbose_name='Забитые голы')
    goals_conceded = models.IntegerField(verbose_name='Пропущенные голы')
    goals_difference = models.IntegerField(verbose_name='Разница голов', null=True, blank=True)
    points = models.IntegerField(verbose_name='Очки')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name} - {self.season.year}"

    class Meta:
        verbose_name = 'Турнирная таблица'
        verbose_name_plural = 'Турнирные таблицы'



class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site_logo/', verbose_name="Логотип", null=True, blank=True)
    favicon = models.ImageField(upload_to='site_favicon/', verbose_name="Фавикон", null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="Заголовок страницы", null=True, blank=True)
    facebook_link = models.URLField(verbose_name="Facebook", null=True, blank=True)
    instagram_link = models.URLField(verbose_name="Instagram", null=True, blank=True)
    tiktok_link = models.URLField(verbose_name="TikTok", null=True, blank=True)
    youtube_link = models.URLField(verbose_name="YouTube", null=True, blank=True)
    copy_right = models.CharField(max_length=255, verbose_name="Копирайт", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"


class News(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    date = models.DateField(verbose_name='Дата')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news/', verbose_name='Изображение')

    def __str__(self):
        return f"Фото для {self.news.title}"

    class Meta:
        verbose_name = 'Изображение новости'
        verbose_name_plural = 'Изображения новостей'

class BestMoments(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Текст')
    link_moments = models.URLField(verbose_name="Лучшие моменты", null=True, blank=True)
    date = models.DateField(verbose_name='Дата')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Лучшие моменты'
        verbose_name_plural = 'Лучшие моменты'


class Sponsor(models.Model):
    name = models.CharField(max_length=100, verbose_name='Спонсор')
    photo = models.ImageField(upload_to='sponsor_logo/', verbose_name="Фото спонсора", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Спонсор'
        verbose_name_plural = 'Спонсоры'


class CompanyInfo(models.Model):
    about = models.TextField(verbose_name="О нас")

    def __str__(self):
        return "Информация о компании"

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"
    
class Document(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    file = models.FileField(upload_to="documents/", verbose_name="Файл")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
    

class ManegementKfl(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    position = models.CharField(max_length=255, verbose_name="Должность")
    photo = models.ImageField(upload_to="management/", verbose_name="Фото", blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Руководство"
        verbose_name_plural = "Руководство"


class Judge(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    photo = models.ImageField(upload_to="judges/", verbose_name="Фото", blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Судья"
        verbose_name_plural = "Судьи"