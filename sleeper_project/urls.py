"""
URL configuration for sleeper_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from sleeper_project.views.home import home, find_leagues
from sleeper_project.views.manager import manager_page, get_avatar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('find_leagues/', find_leagues, name='find_leagues'),
    path('manager/<str:username>/', manager_page, name='manager'),
    path('get_avatar/<str:username>/', get_avatar, name='get_avatar')
]
