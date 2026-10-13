"""
URL configuration for djangoproj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.http import JsonResponse
from django.views.generic import TemplateView


def _home_view(request):
    # Serve React build if present, otherwise return API status
    # instead of raising TemplateDoesNotExist (500) when frontend
    # hasn't been built yet.
    import os
    candidates = [
        os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html'),
        os.path.join(settings.BASE_DIR, 'frontend', 'static', 'index.html'),
    ]
    if any(os.path.exists(p) for p in candidates):
        return TemplateView.as_view(template_name='index.html')(request)
    return JsonResponse({
        'message': 'Car Dealership API is running. Build the React frontend for the full UI.',
        'api_root': '/api/',
        'admin': '/admin/',
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('djangoapp.urls')),
    path('', _home_view, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
