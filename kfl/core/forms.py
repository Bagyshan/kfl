from django import forms
from django.contrib import admin
from .models import EventsMathes, Players, Matches

class MatchEventAdminForm(forms.ModelForm):
    class Meta:
        model = EventsMathes
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "match" in self.data:  # При создании нового события
            try:
                match_id = int(self.data.get("match"))
                match = Matches.objects.get(id=match_id)
                self.fields["player"].queryset = Players.objects.filter(team__in=[match.home_team, match.away_team])
            except (ValueError, Matches.DoesNotExist):
                self.fields["player"].queryset = Players.objects.none()
        elif self.instance.pk:  # При редактировании существующего события
            match = self.instance.match
            self.fields["player"].queryset = Players.objects.filter(team__in=[match.home_team, match.away_team])

