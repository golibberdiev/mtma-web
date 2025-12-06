from django import forms
from .models import OrganizationStat


class OrganizationStatForm(forms.ModelForm):
    class Meta:
        model = OrganizationStat
        fields = [
            "name",
            "classroom_count",
            "lectures",
            "labs",
            "practicals",
            "survey_count",
        ]
        labels = {
            "name": "Tashkilot (OTM / maktab) nomi",
            "classroom_count": "Sinf / laboratoriya xonalari soni",
            "lectures": "Ma'ruza darslari soni",
            "labs": "Laboratoriya mashg'ulotlari soni",
            "practicals": "Amaliy mashg'ulotlar soni",
            "survey_count": "Talaba so'rovnomalari soni",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "classroom_count": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "lectures": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "labs": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "practicals": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "survey_count": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }
