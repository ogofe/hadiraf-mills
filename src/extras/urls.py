from django.urls import path
from .views import (
    Home_page,
)

app_name = 'core'

urlpatterns = [
    path('', Home_page.as_view(), name="home"),
]
