from django.urls import path
from . import views

urlpatterns = [
    path('<coor1>/<coor2>/', views.ApiViewGet.as_view()),
    path('', views.ApiView.as_view())
]