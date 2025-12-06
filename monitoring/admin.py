from django import forms
from .models import OrganizationStat


class OrganizationStatForm(forms.ModelForm):
    class Meta:
        model = OrganizationStat
        fields = ["name", "lectures", "labs", "practicals"]
        labels = {
            "name": "Tashkilot (OTM / maktab) nomi",
            "lectures": "Ma'ruza darslari soni",
            "labs": "Laboratoriya mashg'ulotlari soni",
            "practicals": "Amaliy mashg'ulotlar soni",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "lectures": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "labs": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "practicals": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
