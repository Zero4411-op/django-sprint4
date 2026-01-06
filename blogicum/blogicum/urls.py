from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pages import views as pages_views

handler404 = "pages.views.page_404"
handler500 = "pages.views.page_500"
handler403 = "pages.views.csrf_failure"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("blog.urls", "blog"), namespace="blog")),
    path("pages/", include(("pages.urls", "pages"), namespace="pages")),
    path("auth/registration/", pages_views.registration, name="registration"),
    path("auth/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
