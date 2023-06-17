from django.shortcuts import render
from django.views.generic.base import TemplateView, View


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'
