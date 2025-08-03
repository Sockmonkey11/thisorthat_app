from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("poll/<int:poll_id>/", views.poll_detail, name="poll_detail"),
    path("create_poll/", views.create_poll, name="create_poll"),
    path("delete_poll/<int:poll_id>/", views.delete_poll, name="delete_poll"),
    path("register/", views.register, name="register"),
]


