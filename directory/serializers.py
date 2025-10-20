from rest_framework import serializers
from .models import Listing, Organisation, Vacancy

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Organisation
        fields=["id","name","city","region","website","contact_email"]

class ListingSerializer(serializers.ModelSerializer):
    organisation=OrganisationSerializer()
    class Meta:
        model=Listing
        fields=["id","title","category","description","location","price_from","is_premium","featured_until","is_approved","website","contact_email","organisation"]

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model=Vacancy
        fields=["id","title","description","event_date","budget","location","contact_email","is_open"]
