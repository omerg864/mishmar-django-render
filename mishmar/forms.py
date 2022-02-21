from django import forms
from users.models import UserSettings as UserSettings
from .models import Settings as Settings
from django.contrib.auth.models import User


class QualityUpdateForm(forms.ModelForm):
    night = forms.IntegerField(min_value=0)
    sat_night = forms.IntegerField(min_value=0)
    sat_morning = forms.IntegerField(min_value=0)
    sat_noon = forms.IntegerField(min_value=0)

    class Meta:
        model = UserSettings
        fields = ['user', 'night', 'sat_night', 'sat_morning', 'sat_noon']



class SettingsForm(forms.ModelForm):
    pin_code = forms.IntegerField(required=True)
    officer = forms.CharField(max_length=20)
    city = forms.CharField(max_length=30)
    max_seq0 = forms.IntegerField(required=True)
    max_seq1 = forms.IntegerField(required=True)
    friday_morning = forms.BooleanField(required=False)
    friday_noon = forms.BooleanField(required=False)
    num_mags = forms.IntegerField(required=True)
    hand_cuffs = forms.IntegerField(required=True)
    num_mag_cases = forms.IntegerField(required=True)
    num_gun_cases = forms.IntegerField(required=True)


    class Meta:
        model = Settings
        fields = ["pin_code", "officer", "city", "max_seq0", "max_seq1", "friday_morning", "friday_noon", "num_mags", "hand_cuffs", "num_mag_cases", "num_gun_cases"]


