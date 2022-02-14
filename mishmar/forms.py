from django import forms
from users.models import UserSettings as UserSettings
from .models import Settings as Settings
from .models import Shift1 as Shift
from .models import Organization as Organization
from .models import Week as Week
from .models import ShiftWeek as ShiftWeek
from django.contrib.auth.models import User


class QualityUpdateForm(forms.ModelForm):
    night = forms.IntegerField(min_value=0)
    sat_night = forms.IntegerField(min_value=0)
    sat_morning = forms.IntegerField(min_value=0)
    sat_noon = forms.IntegerField(min_value=0)

    class Meta:
        model = UserSettings
        fields = ['user', 'night', 'sat_night', 'sat_morning', 'sat_noon']


class OrganizationUpdateForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = []

class WeekUpdateForm(forms.ModelForm):

    class Meta:
        fields_temp = []
        for i in range(1, 8):
            fields_temp.append("Day" + str(i) + "_630")
            fields_temp.append("Day" + str(i) + "_700_search")
            fields_temp.append("Day" + str(i) + "_700_manager")
            fields_temp.append("Day" + str(i) + "_720_1")
            fields_temp.append("Day" + str(i) + "_720_pull")
            fields_temp.append("Day" + str(i) + "_720_2")
            fields_temp.append("Day" + str(i) + "_720_3")
            fields_temp.append("Day" + str(i) + "_1400")
            fields_temp.append("Day" + str(i) + "_1500")
            fields_temp.append("Day" + str(i) + "_1500_1900")
            fields_temp.append("Day" + str(i) + "_2300")
            fields_temp.append("Day" + str(i) + "_notes")
        model = Week
        fields = []


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


class ShiftForm(forms.ModelForm):

    class Meta:
        fields_temp = []
        fields_temp.append("seq_night")
        fields_temp.append("seq_noon")
        model = Shift
        fields = fields_temp


class ShiftViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShiftViewForm, self).__init__(*args, **kwargs)
        fields_temp = []
        fields_temp.append("seq_night")
        fields_temp.append("seq_noon")
        for field in fields_temp:
            self.fields[field].disabled = True

    class Meta:
        fields_temp = []
        fields_temp.append("seq_night")
        fields_temp.append("seq_noon")
        model = Shift
        fields = fields_temp


class ShiftWeekForm(forms.ModelForm):

    class Meta:
        fields_temp = []
        for i in range(1, 8):
            fields_temp.append("M" + str(i))
            fields_temp.append("A" + str(i))
            fields_temp.append("N" + str(i))
            fields_temp.append("P" + str(i))
            fields_temp.append("R" + str(i))
            fields_temp.append("notes" + str(i))
        model = ShiftWeek
        fields = fields_temp


class ShiftWeekViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShiftWeekViewForm, self).__init__(*args, **kwargs)
        fields_temp = []
        for i in range(1, 8):
            fields_temp.append("M" + str(i))
            fields_temp.append("A" + str(i))
            fields_temp.append("N" + str(i))
            fields_temp.append("P" + str(i))
            fields_temp.append("R" + str(i))
            fields_temp.append("notes" + str(i))
        for field in fields_temp:
            self.fields[field].disabled = True

    class Meta:
        fields_temp = []
        for i in range(1, 8):
            fields_temp.append("M" + str(i))
            fields_temp.append("A" + str(i))
            fields_temp.append("N" + str(i))
            fields_temp.append("P" + str(i))
            fields_temp.append("R" + str(i))
            fields_temp.append("notes" + str(i))
        model = ShiftWeek
        fields = fields_temp