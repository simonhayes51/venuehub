from django.urls import path
from . import api_views
urlpatterns=[
    path("listings/", api_views.ListingListAPI.as_view()),
    path("organisations/", api_views.OrganisationListAPI.as_view()),
    path("vacancies/", api_views.VacancyListAPI.as_view()),
]
