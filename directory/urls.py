from django.urls import path
from . import views

app_name="directory"
urlpatterns=[
    path("", views.home, name="home"),
    path("listings/", views.listings, name="listings"),
    path("listings/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("listings/<int:pk>/edit/", views.edit_listing, name="edit_listing"),
    path("listings/<int:pk>/review/", views.submit_review, name="submit_review"),
    path("organisations/", views.organisations, name="organisations"),
    path("organisations/<int:pk>/", views.organisation_detail, name="organisation_detail"),
    path("host-signup/", views.host_signup, name="host_signup"),
    path("host-thanks/", views.host_thanks, name="host_thanks"),
    path("vacancies/", views.vacancies, name="vacancies"),
    path("vacancies/post/", views.post_vacancy, name="post_vacancy"),
    path("vacancies/<int:pk>/", views.vacancy_detail, name="vacancy_detail"),
    path("vacancies/<int:pk>/apply/<int:listing_id>/", views.apply_vacancy, name="apply_vacancy"),
]
