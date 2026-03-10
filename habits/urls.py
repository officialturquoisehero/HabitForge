from django.urls import path
from . import views

urlpatterns = [
    path('', views.habit_list, name='habit_list'),
    path('add/', views.add_habit, name='add_habit'),
    path('<int:habit_id>/edit/', views.edit_habit, name='edit_habit'),
    path('<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
    path('<int:habit_id>/complete/', views.complete_habit, name='complete_habit'),
]