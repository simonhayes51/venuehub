from django import forms
from .models import Review, Vacancy, VacancyApplication, ContactRequest, Listing, ListingImage

class HostSignupForm(forms.Form):
    org_name=forms.CharField(max_length=200,label="Organisation / Act name")
    city=forms.CharField(max_length=100,required=False)
    region=forms.CharField(max_length=100,required=False)
    website=forms.URLField(required=False)
    contact_email=forms.EmailField(required=True,label="Public booking email")
    title=forms.CharField(max_length=200)
    category=forms.ChoiceField(choices=[("quiz","Quiz Host"),("dj","DJ"),("band","Band"),("comedian","Comedian"),("karaoke","Karaoke Host"),("other","Other")])
    description=forms.CharField(widget=forms.Textarea,required=False)
    location=forms.CharField(max_length=120,required=False)
    price_from=forms.DecimalField(max_digits=8,decimal_places=2,required=False)
    owner_email=forms.EmailField(required=True,label="Admin contact email")
    photo=forms.ImageField(required=False,label="Profile photo")
    wants_premium=forms.BooleanField(required=False,label="I'm interested in Premium placement")

class ListingEditForm(forms.ModelForm):
    class Meta:
        model=Listing
        fields=["title","category","description","location","price_from","website","contact_email","photo"]
        widgets={"description": forms.Textarea(attrs={"rows":5})}

class ListingImageForm(forms.ModelForm):
    class Meta:
        model=ListingImage
        fields=["image","caption"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=["rating","comment","venue_name","venue_email"]
        widgets={"comment": forms.Textarea(attrs={"rows":4})}

class VacancyForm(forms.ModelForm):
    class Meta:
        model=Vacancy
        fields=["title","description","event_date","budget","location","contact_email"]
        widgets={"description": forms.Textarea(attrs={"rows":5})}

class VacancyApplicationForm(forms.ModelForm):
    class Meta:
        model=VacancyApplication
        fields=["message"]
        widgets={"message": forms.Textarea(attrs={"rows":4})}

class ContactRequestForm(forms.ModelForm):
    class Meta:
        model=ContactRequest
        fields=["venue_name","venue_email","message"]
        widgets={"message": forms.Textarea(attrs={"rows":4})}
