from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, IntegerField
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.filters import OrderingFilter
from rest_framework import filters, generics, status, viewsets, mixins
from .models import Teams, Season,Players, Management ,StaticticsPlayerSeason , \
SeasonAwards,Standings, Matches, EventsMathes, SiteSettings, News, BestMoments, MatchLineup, Season, Tournament, Round, Sponsor, CompanyInfo, Judge, \
NewsImage, Document, ManegementKfl, Stadium
from django.db.models import Q, Case, When, Value, IntegerField
from .serializers import TeamsSerializer, ManagementSerializer,StaticticsPlayerSeasonSerializer ,TeamsDetailSerializer, PlayersSerializer, StandingsSerializer, PlayerDetailSerializer, MatchesSerializer, EventsMathesSerializer, SiteSettingsSerializer, NewsSerializer, \
    BestMomentsSerializer, MatchDetailSerializer,MatchLineupSerializer, SeasonAwardsSerializer, \
        SeasonSerializer, TournamentSerializer, RoundSerializer, SponsorSerializer, CompanyInfoSerializer, JudgeSerializer, \
        NewsImageSerializer, DocumentSerializer, ManegementKflSerializer, NewsDetailSerializer, StadiumSerializer
from django.utils.timezone import now
from .pagination import StandardResultsSetPagination


class TeamsModelViewSet(viewsets.ModelViewSet):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'city']
    search_fields = ['name', 'city']
    ordering_fields = ['name', 'city']
    ordering = ['name']

    
    @action(detail=True, methods=['get'], url_path='team_detail', url_name='team_detail')
    def team_detail(self, request, pk=None):
        team = self.get_object()
        print(team, "-----")
        serializer = TeamsDetailSerializer(team)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='players', url_name='players')
    def players(self, request, pk=None):
        team = self.get_object()
        players = Players.objects.filter(team=team)


        forwards = []
        midfielders = []
        defenders = []
        goalkeepers = []

        added_player_ids = set()  

        for player in players:
            pos = player.position.lower()
            if "нападающий" in pos and player.id not in added_player_ids:
                forwards.append(player)
            elif "полузащитник" in pos and player.id not in added_player_ids:
                midfielders.append(player)
            elif "защитник" in pos and player.id not in added_player_ids:
                defenders.append(player)
            elif "вратарь" in pos and player.id not in added_player_ids:
                goalkeepers.append(player)
            
            added_player_ids.add(player.id)

        grouped_players = {
            "forwards": PlayersSerializer(forwards, many=True).data,
            "midfielders": PlayersSerializer(midfielders, many=True).data,
            "defenders": PlayersSerializer(defenders, many=True).data,
            "goalkeepers": PlayersSerializer(goalkeepers, many=True).data,
            "management": ManagementSerializer(Management.objects.filter(team=team), many=True).data
        }

        response_data = {
            "team": TeamsSerializer(team).data,
            "players": grouped_players
        }

        return Response(response_data)

    
    @action(detail=True, methods=['get'], url_path='matches')
    def matches(self, request, pk=None):
        """
        Возвращает список матчей, в которых участвовала команда.
        Поддерживаются фильтры по сезону, турниру и туру.
        """
        team = self.get_object()
        filters = self._build_filters(request)

        matches = Matches.objects.filter(Q(home_team=team) | Q(away_team=team)).filter(**filters)
        serializer = MatchesSerializer(matches, many=True)
        
        return Response(serializer.data)

    def _build_filters(self, request):
        """
        Собирает фильтры для запроса на основе query-параметров.
        """
        filter_map = {
            'season': ('season__year', int),
            'tournament': ('tournament__id', int),
            'round': ('round', int)
        }
        
        return {
            filter_field: cast_func(request.query_params[param])
            for param, (filter_field, cast_func) in filter_map.items()
            if request.query_params.get(param)
        }

class PlayerDetailView(RetrieveAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayerDetailSerializer


class StandingsListView(ListAPIView):
    serializer_class = StandingsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season__year', 'tournament']

    # Укажи вручную нужный турнир
    DEFAULT_TOURNAMENT_NAME = "Премьер-лига"

    def get_queryset(self):
        standings = Standings.objects.select_related('team', 'tournament')

        # Вычисляем разницу мячей
        for standing in standings:
            standing.goals_difference = standing.goals_scored - standing.goals_conceded
            standing.save()

        # Сортировка по очкам, разнице мячей, забитым голам и победам
        return standings.order_by(
            '-points', 
            '-goals_difference', 
            '-goals_scored', 
            '-wins'
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Получаем текущий сезон
        current_season = Season.objects.filter(is_current=True).first()

        # Получаем ID турнира по названию
        default_tournament = Tournament.objects.filter(name=self.DEFAULT_TOURNAMENT_NAME).first()

        # Проверяем, переданы ли параметры в запросе
        season_year = request.query_params.get("season__year")
        tournament_id = request.query_params.get("tournament")

        # Если параметры не переданы, устанавливаем значения по умолчанию
        if not season_year and current_season:
            season_year = current_season.year

        if not tournament_id and default_tournament:
            tournament_id = default_tournament.id

        # Фильтруем бомбардиров по указанным или дефолтным данным
        top_scorers = StaticticsPlayerSeason.objects.filter(
            season__year=season_year, 
            tournament=tournament_id
        ).select_related('player').order_by('-goals')[:3]

        # Формируем ответ с топ-голеадорами
        response.data = {
            "standings": response.data,
            "top_scorers": [
                {   
                    "id": scorer.player.id,
                    "player_photo": scorer.player.photo.url if scorer.player.photo else None,
                    "player": f"{scorer.player.first_name} {scorer.player.last_name}",
                    "number": scorer.player.number,
                    "goals": scorer.goals,
                    "team": scorer.player.team.name if scorer.player.team else None,
                    "team_logo": scorer.player.team.logo.url if scorer.player.team.logo else None,
                }
                for scorer in top_scorers
            ]
        }
        
        return Response(response.data)


class TeamMatchesView(ListAPIView):
    serializer_class = MatchesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tournament']
    ordering_fields = ['date_match']
    ordering = ['date_match']

    def get_queryset(self):

        team_id = self.kwargs.get('team_id')

        # Определяем текущий сезон
        current_season = Season.objects.filter(is_current=True).first()

        if not current_season:
            return Matches.objects.none()  # Если сезона нет, возвращаем пустой список

        # Фильтруем матчи текущего сезона
        queryset = Matches.objects.filter(season=current_season, home_team_id=team_id) | Matches.objects.filter(
            season=current_season, away_team_id=team_id
        )

        return queryset

class MatchDetailView(RetrieveAPIView):
    """ Возвращает детали матча с событиями """
    queryset = Matches.objects.all()
    serializer_class = MatchDetailSerializer
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        match = get_object_or_404(Matches, id=self.kwargs["id"])
        serializer = self.get_serializer(match)
        return Response(serializer.data)

class MatchListView(ListAPIView):
    serializer_class = MatchesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season__year', 'tournament', 'round']
    ordering_fields = ['date_match']
    ordering = ['date_match']
    queryset = Matches.objects.all()

class MatchLineupListView(ListAPIView):
    serializer_class = MatchLineupSerializer

    def get_queryset(self):
        match_id = self.kwargs["match_id"]
        match = get_object_or_404(Matches, id=match_id)
        return MatchLineup.objects.filter(match=match)

    def list(self, request, *args, **kwargs):
        match_id = self.kwargs["match_id"]
        match = get_object_or_404(Matches, id=match_id)

        def get_team_lineup(team):
            starting = self.get_queryset().filter(team=team, is_starting=True)
            substitutes = self.get_queryset().filter(team=team, is_substitute=True)
            return {
                "starting": MatchLineupSerializer(starting, many=True).data,
                "substitutes": MatchLineupSerializer(substitutes, many=True).data
            }

        return Response({
            "match": f"{match.home_team.name} vs {match.away_team.name}",
            "date": match.date_match,
            "stadium": match.stadium.name,
            "status": match.status,
            "home_goals": match.home_goals,
            "away_goals": match.away_goals,
            "home_team": {
                "logo": match.home_team.logo.url,
                "team_name": match.home_team.name,
                "lineup": get_team_lineup(match.home_team)
            },
            "away_team": {
                "logo": match.away_team.logo.url,
                "team_name": match.away_team.name,
                "lineup": get_team_lineup(match.away_team)
            }
        })

class MatchEventsListView(ListAPIView):
    serializer_class = EventsMathesSerializer

    def get_queryset(self):
        match_id = self.kwargs.get('match_id')
        return EventsMathes.objects.filter(match_id=match_id).order_by('time')

class PlayerStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticticsPlayerSeason.objects.all()
    serializer_class = StaticticsPlayerSeasonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season__year', 'tournament']
    ordering_fields = ['goals', 'assists', 'yellow_cards', 'red_cards']
    ordering = ['-goals']  # По умолчанию сортировка по голам

    @action(detail=False, methods=['get'], url_path='top-scorers', url_name='top_scorers')
    def top_scorers(self, request):
        """Возвращает лучших бомбардиров"""
        season = request.query_params.get('season')
        tournament = request.query_params.get('tournament')

        filters = Q(goals__gt=0)  # Только игроки, забившие хотя бы 1 гол
        if season:
            filters &= Q(season=season)
        if tournament:
            filters &= Q(tournament=tournament)

        top_scorers = StaticticsPlayerSeason.objects.filter(filters).order_by('-goals')[:10]
        serializer = self.get_serializer(top_scorers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top-assistants', url_name='top_assistants')
    def top_assistants(self, request):
        """Возвращает лучших ассистентов"""
        season = request.query_params.get('season')
        tournament = request.query_params.get('tournament')

        filters = Q(assists__gt=0)
        if season:
            filters &= Q(season=season)
        if tournament:
            filters &= Q(tournament=tournament)

        top_assistants = StaticticsPlayerSeason.objects.filter(filters).order_by('-assists')[:10]
        serializer = self.get_serializer(top_assistants, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='most-yellow-cards', url_name='most_yellow_cards')
    def most_yellow_cards(self, request):
        """Возвращает игроков с наибольшим числом желтых карточек"""
        season = request.query_params.get('season')
        tournament = request.query_params.get('tournament')

        filters = Q(yellow_cards__gt=0)
        if season:
            filters &= Q(season=season)
        if tournament:
            filters &= Q(tournament=tournament)

        most_yellow = StaticticsPlayerSeason.objects.filter(filters).order_by('-yellow_cards')[:10]
        serializer = self.get_serializer(most_yellow, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='most-red-cards', url_name='most_red_cards')
    def most_red_cards(self, request):
        """Возвращает игроков с наибольшим числом красных карточек"""
        season = request.query_params.get('season')
        tournament = request.query_params.get('tournament')

        filters = Q(red_cards__gt=0)
        if season:
            filters &= Q(season=season)
        if tournament:
            filters &= Q(tournament=tournament)

        most_red = StaticticsPlayerSeason.objects.filter(filters).order_by('-red_cards')[:10]
        serializer = self.get_serializer(most_red, many=True)
        return Response(serializer.data)


class SiteDataListAPIView(ListAPIView):
    def list(self, request, *args, **kwargs):
        # Получаем настройки сайта (должна быть 1 запись)
        site_settings = SiteSettings.objects.first()
        site_data = SiteSettingsSerializer(site_settings, context={'request': request}).data if site_settings else {}

        # Последние 20 новостей
        latest_news = News.objects.order_by('-date')[:20]
        news_data = NewsSerializer(latest_news, many=True, context={'request': request}).data

        # Последние 5 лучших моментов
        latest_moments = BestMoments.objects.order_by('-date')[:5]
        moments_data = BestMomentsSerializer(latest_moments, many=True, context={'request': request}).data

        # 10 ближайших матчей (которые ещё не начались)
        upcoming_matches = Matches.objects.filter(date_match__gte=timezone.now().date()).order_by('date_match')[:10]
        matches_data = MatchesSerializer(upcoming_matches, many=True, context={'request': request}).data

        clubs = Teams.objects.all().order_by('name')
        clubs_data = TeamsSerializer(clubs, many=True, context={'request': request}).data

        # Все спонсоры
        sponsors = Sponsor.objects.all()
        sponsors_data = SponsorSerializer(sponsors, many=True, context={'request': request}).data

        # Формируем общий JSON
        response_data = {
            "logo": site_data.get("logo", ""),
            "title": site_data.get("title", ""),
            "facebook": site_data.get("facebook_link", ""),
            "instagram": site_data.get("instagram_link", ""),
            "tiktok": site_data.get("tiktok_link", ""),
            "youtube": site_data.get("youtube_link", ""),
            "copyright": site_data.get("copy_right", ""),
            "clubs": clubs_data,
            "upcoming_matches": matches_data,
            "news": news_data,
            "best_moments": moments_data,
            "sponsors": sponsors_data
        }

        return Response(response_data)


class SeasonAwardsListView(ListAPIView):
    serializer_class = SeasonAwardsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season__year', 'season__is_current','tournament']
    queryset = SeasonAwards.objects.all()


class SeasonListView(ListAPIView):
    serializer_class = SeasonSerializer

    def get_queryset(self):
        # Возвращаем все сезоны
        return Season.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TournamentListView(ListAPIView):
    serializer_class = TournamentSerializer

    def get_queryset(self):
        # Возвращаем все турниры
        return Tournament.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class RoundListView(ListAPIView):
    serializer_class = RoundSerializer

    def get_queryset(self):
        # Получаем текущий сезон
        current_season = Season.objects.filter(is_current=True).first()

        if not current_season:
            return Round.objects.none()  # Если сезона нет, возвращаем пустой queryset

        # Извлекаем параметры фильтрации из query-параметров
        season_id = self.request.query_params.get('season')
        tournament_id = self.request.query_params.get('tournament')

        # Начальная фильтрация: туры текущего сезона
        queryset = Round.objects.filter(season=current_season)

        # Фильтрация по сезону, если передан параметр season
        if season_id:
            queryset = queryset.filter(season_id=season_id)

        # Фильтрация по турниру, если передан параметр tournament
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        return queryset

    def list(self, request, *args, **kwargs):
        # Получаем фильтрованный queryset
        queryset = self.get_queryset()
        # Сериализуем queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




        
class NewsListView(ListAPIView):
    queryset = News.objects.all().order_by('-date')  # Сортировка по дате (от новых к старым)
    serializer_class = NewsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'text']  # Поиск по заголовку и тексту

class NewsDetailView(RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsDetailSerializer

class BestMomentsListView(ListAPIView):
    queryset = BestMoments.objects.all().order_by('-date')
    serializer_class = BestMomentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

class CompanyInfoListView(ListAPIView):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer

class DocumentListView(ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class ManegementKflListView(ListAPIView):
    queryset = ManegementKfl.objects.all()
    serializer_class = ManegementKflSerializer

class JudgeListView(ListAPIView):
    queryset = Judge.objects.all()
    serializer_class = JudgeSerializer

class StadiumListView(ListAPIView):
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer