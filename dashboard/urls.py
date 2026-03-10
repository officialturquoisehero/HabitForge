from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('schedule/', views.schedule_view, name='schedule'),
]