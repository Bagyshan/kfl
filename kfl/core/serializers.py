from rest_framework import serializers
from .models import Teams,Management ,Players, \
SeasonAwards,Standings, Matches, EventsMathes, \
StaticticsPlayerSeason, SiteSettings, News, \
BestMoments, MatchLineup, Season, Tournament, Round, Sponsor\
,CompanyInfo, Judge, NewsImage, Document, ManegementKfl, Stadium


class TeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ['id','name', 'logo', 'city']


class TeamsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ['id','name', 'logo', 'city', 'stadium', 'coach', 'founded_year', ]


class ManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Management
        fields = ['id', 'team', 'first_name', 'last_name', 'position', 'photo']


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'logo', 'country',]


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'year', 'is_current', 'start_date', 'end_date']
        

class RoundSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    season_year = serializers.CharField(source='season.year', read_only=True)
    class Meta:
        model = Round
        fields = ['id', 'tournament_name', 'season_year', 'round_number']

class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = ['id', 'name', 'city', 'capacity', 'adress']

class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ['id','photo', 'first_name', 'last_name', 'position', 'number', 'nationality', 'goals', 'assists']

class PlayerDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    team_name = serializers.CharField(source="team.name")
    team_id = serializers.IntegerField(source="team.id")
    team_logo = serializers.CharField(source="team.logo")

    class Meta:
        model = Players
        fields = [
            "id", "full_name", "team_name", "team_id", "team_logo","photo", "birth_date", "position", "number",
            "height", "weight", "nationality", "goals", "assists", "yellow_cards",
            "red_cards", "games", "minutes"
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class StandingsSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField(source='team.id', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_logo = serializers.CharField(source='team.logo', read_only=True)
    season = serializers.CharField(source='season.year', read_only=True)
    tournament = serializers.CharField(source='tournament.name', read_only=True)
    calculated_goals_difference = serializers.IntegerField(read_only=True)

    class Meta:
        model = Standings
        fields = ['id', 'tournament', 'season','team_id', 'team_name', 'team_logo', 'season', 'games', 'wins', 'draws', 'losses', 'goals_scored', 'goals_conceded', 'calculated_goals_difference','points', 'goals_difference']


class MatchesSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    home_team_logo = serializers.CharField(source='home_team.logo', read_only=True)
    away_team_logo = serializers.CharField(source='away_team.logo', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    season_year = serializers.CharField(source='season.year', read_only=True)
    round_number = serializers.CharField(source='round.round_number',read_only=True)
    stadium = serializers.CharField(source='stadium.name')

    class Meta:
        model = Matches
        fields = ['id','tournament_name', 'season_year', 'round_number', 'home_team_logo', 'away_team_logo', 'home_team_name', 'away_team_name', 'date_match','time_match','home_goals', 'away_goals', 'stadium', 'status', 'mvp', 'documents','technical_defeat']

class MatchLineupSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = MatchLineup
        fields = ["id", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.player.first_name} {obj.player.last_name}"

    

class EventsMathesSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    player_team_id = serializers.SerializerMethodField()
    player_team_name = serializers.CharField(source='player.team.name', read_only=True)
    match_info = serializers.SerializerMethodField()

    class Meta:
        model = EventsMathes
        fields = ['id', 'match_info', 'player_name', 'player_team_id','player_team_name','event', 'time',]

    def get_player_name(self, obj):
        return f"{obj.player.first_name} {obj.player.last_name}"
    
    def get_player_team_id(self, obj):
        return obj.player.team.id

    def get_match_info(self, obj):
        return f"{obj.match.home_team.name} vs {obj.match.away_team.name} - {obj.match.date_match}"

class MatchDetailSerializer(serializers.ModelSerializer):
    """ Основной сериализатор для матча с событиями """
    home_team = serializers.CharField(source='home_team.name')
    away_team = serializers.CharField(source='away_team.name')
    home_team_logo = serializers.CharField(source='home_team.logo', read_only=True)
    away_team_logo = serializers.CharField(source='away_team.logo', read_only=True)
    stadium = serializers.CharField(source='stadium.name')
    events = serializers.SerializerMethodField()

    class Meta:
        model = Matches
        fields = ['id', 'home_team_logo', 'away_team_logo', 'home_team', 'away_team', 'home_goals','away_goals' ,'date_match', 'time_match','events', 'stadium','documents','technical_defeat']


    def get_events(self, obj):
        events = EventsMathes.objects.filter(match=obj).order_by('time')
        return EventsMathesSerializer(events, many=True).data

class StaticticsPlayerSeasonSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(source="player.id")
    player_name = serializers.SerializerMethodField()
    player_photo = serializers.CharField(source="player.photo")
    team = serializers.CharField(source='player.team.name', read_only=True)
    team_logo = serializers.CharField(source='player.team.logo', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    season_year = serializers.CharField(source='season.year', read_only=True)

    class Meta:
        model = StaticticsPlayerSeason
        fields = [
            'id',
            'player_id',
            'player_name',
            'player_photo',
            'team',
            'team_logo',
            'tournament_name',
            'season_year',
            'goals',
            'assists',
            'yellow_cards',
            'red_cards',
            'games',
            'minutes'
        ]
    
    def get_player_name(self, obj):
        return f"{obj.player.first_name} {obj.player.last_name}"

class SeasonAwardsSerializer(serializers.ModelSerializer):
    best_scorer = PlayersSerializer(read_only=True)
    best_goalkeeper = PlayersSerializer(read_only=True)
    best_coach = ManagementSerializer(read_only=True)  # Допустим, тренер имеет строковое представление
    best_team = TeamsSerializer(read_only=True)
    best_player = PlayersSerializer(read_only=True)
    season_year = serializers.CharField(source='season.year', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)

    class Meta:
        model = SeasonAwards
        fields = [
            'season_year', 'tournament_name', 'best_scorer', 'best_goalkeeper', 'best_coach', 'best_team', 'best_player'
        ]

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['logo', 'title', 'facebook_link', 'instagram_link', 'tiktok_link', 'youtube_link', 'copy_right']


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image']



class NewsDetailSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'date', 'images']

class NewsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'date', 'images']

    def get_images(self, obj):
        first_image = obj.images.first()
        return first_image.image.url if first_image else None


class BestMomentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestMoments
        fields = ['id', 'title', 'description', 'link_moments', 'date']


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = ['id', 'name', 'photo']


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = ['id', 'about']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id','name', 'file']

class ManegementKflSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManegementKfl
        fields = ['id', 'name', 'photo', 'position']


class JudgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Judge
        fields = ['id','name', 'photo']