"""
URL configuration for hirevision_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from logging_config import get_logger

# Initialize logger for project URLs
logger = get_logger('project_urls')

# Log URL pattern registration
logger.info("Registering HireVision Django project URL patterns")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hirevision.urls")),
]

logger.info(f"Registered {len(urlpatterns)} main URL patterns for Django project")
logger.debug("URL patterns include: admin interface and HireVision app")

# Serve media files during development
if settings.DEBUG:
    logger.info("Development mode detected - adding media file serving")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    logger.debug(f"Media URL: {settings.MEDIA_URL}, Media Root: {settings.MEDIA_ROOT}")
else:
    logger.info("Production mode detected - media files should be served by web server")

logger.info("URL configuration completed successfully")
