from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tours/', views.tour_list, name='tour_list'),
    path('tour/<int:pk>/', views.tour_detail, name='tour_detail'),

    path('control-room-secure-77/', views.admin_dashboard, name='admin_dashboard'),

    path('about/', views.about, name='about'),
    path('dashboard/download-report/', views.download_monthly_report, name='download_report'),
    path('destinations/', views.destination_list, name='destination_list'),

    path('gallery/', views.gallery, name='gallery'),

]