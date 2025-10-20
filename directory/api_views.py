from rest_framework import generics
from .models import Listing, Organisation, Vacancy
from .serializers import ListingSerializer, OrganisationSerializer, VacancySerializer

class ListingListAPI(generics.ListAPIView):
    queryset=Listing.objects.filter(is_approved=True).select_related("organisation").all()
    serializer_class=ListingSerializer

class OrganisationListAPI(generics.ListAPIView):
    queryset=Organisation.objects.all()
    serializer_class=OrganisationSerializer

class VacancyListAPI(generics.ListAPIView):
    queryset=Vacancy.objects.filter(is_open=True).all()
    serializer_class=VacancySerializer
