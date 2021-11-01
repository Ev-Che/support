from django.contrib import admin
from django.urls import path, include

import tickets

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('tickets/', include('tickets.urls')),
]
