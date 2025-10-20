from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns=[
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("directory.api_urls")),
    path("billing/", include("billing.urls")),
    path("", include("directory.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
