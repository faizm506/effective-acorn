from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tours/', views.tour_list, name='tour_list'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),

    path('my-secret-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]