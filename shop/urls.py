from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.main_page),
    path('map/', views.mapp),
    path('menu/', views.menu),
    path('send/', views.send),
    path('basket/', views.basket),
    path('fruits/', views.fruits),
    path('beverages/', views.beverages),
    path('menu/minus/<str:name>/', views.minus),
    path('menu/plus/<str:name>/', views.plus),
    path('basket/<str:name>/', views.basket_del),
    path('redirect_whatsapp/', views.redirect_whatsapp),
    path('fruits/minus/<str:name>/', views.fruits_minus),
    path('fruits/plus/<str:name>/', views.fruits_plus),
    path('beverages/minus/<str:name>/', views.beverages_minus),
    path('beverages/plus/<str:name>/', views.beverages_plus),
]
