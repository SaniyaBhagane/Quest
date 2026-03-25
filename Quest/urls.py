from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),

    path("users/", include("users.urls")),
    path("communities/", include("communities.urls")),
    path("posts/", include("posts.urls", namespace="posts")),  
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)