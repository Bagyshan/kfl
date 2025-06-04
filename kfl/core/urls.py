from django.urls import path
from django.urls.conf import include
from .views import TeamsModelViewSet, StandingsListView, TeamMatchesView, MatchListView, MatchEventsListView, PlayerDetailView, \
SiteDataListAPIView, NewsListView, NewsDetailView,BestMomentsListView ,MatchLineupListView,MatchDetailView ,\
    PlayerStatisticsViewSet, SeasonAwardsListView, SeasonListView, TournamentListView, RoundListView, CompanyInfoListView, \
    JudgeListView, DocumentListView, ManegementKflListView, StadiumListView
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'teams', TeamsModelViewSet)
router.register(r'stats', PlayerStatisticsViewSet, basename='player_stats')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/standings/', StandingsListView.as_view(), name='standings-list'),
    path('api/matches/', MatchListView.as_view(), name='matches-list'),
    path('api/matches-detail/<int:id>/', MatchDetailView.as_view(), name='match-detail'),
    path('api/matches/team/<int:team_id>/', TeamMatchesView.as_view(), name='matches-by-team'),
    path('api/matches/<int:match_id>/events/', MatchEventsListView.as_view(), name='match-events'),
    path("api/players/<int:pk>/", PlayerDetailView.as_view(), name="player-detail"),
    path("api/site/", SiteDataListAPIView.as_view(), name="site-data"),
    path("api/news/", NewsListView.as_view(), name="news-list"),
    path("api/news/<int:pk>/", NewsDetailView.as_view(), name="news-detail"),
    path("api/matches/<int:match_id>/lineup/", MatchLineupListView.as_view(), name="match-lineup"),
    path('api/season-awards/', SeasonAwardsListView.as_view(), name='season_awards_list'),
    path('api/seasons/', SeasonListView.as_view(), name='season-list'),
    path('api/tournaments/', TournamentListView.as_view(), name='tournament-list'),
    path('api/rounds/', RoundListView.as_view(), name='round-list'),
    path('api/news/', NewsListView.as_view(), name='news-list'),
    path('api/best-moments/', BestMomentsListView.as_view(), name='best-moments-list'),
    path('api/company-info/', CompanyInfoListView.as_view(), name='company-info-list'),
    path('api/judges/', JudgeListView.as_view(), name='judge-list'),
    path('api/documents/', DocumentListView.as_view(), name='document-list'),
    path('api/management/', ManegementKflListView.as_view(), name='management-list'),
    path('api/stadium/', StadiumListView.as_view(), name='stadium-list'),
]
