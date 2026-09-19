"""
URL configuration for bmi_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
# admin  -> Django's built-in administration site (not used by our own pages).
# path   -> creates one URL rule.
# include -> hands a group of URLs over to another urls.py file.
from django.contrib import admin
from django.urls import path, include

# Django checks these rules from top to bottom and uses the first match.
urlpatterns = [
    # Any URL starting with /admin/ goes to Django's built-in admin site.
    path('admin/', admin.site.urls),
    # Send all other URLs to the bmi_calculator app's own urls.py
    # The empty '' prefix means the app's pages live at the site root, so the
    # home page is http://127.0.0.1:8000/ and not http://127.0.0.1:8000/something/.
    path('', include('bmi_calculator.urls')),
]
