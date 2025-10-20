from django.urls import path
from . import views
app_name="billing"
urlpatterns=[
    path("subscribe/", views.subscribe_index, name="subscribe_index"),
    path("create-session/", views.create_checkout_session, name="create_session"),
    path("success/", views.subscribe_success, name="success"),
    path("cancel/", views.subscribe_cancel, name="cancel"),
    path("webhook/", views.webhook, name="webhook"),
    path("portal/", views.billing_portal, name="portal"),
    path("manual-mark/", views.manual_mark_premium, name="manual_mark"),
]
