from django.views.generic import TemplateView
from django.shortcuts import render


class Home_page(TemplateView):
    template_name = 'core/pages/homepage.html'