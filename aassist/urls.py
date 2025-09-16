from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("info/", views.info, name="info"),
    path("tracker/", views.tracker, name="tracker"),
    path("api/search-drinks/", views.search_drinks, name="search_drinks"),
    path("api/add-consumption/", views.add_consumption, name="add_consumption"),
    path("api/delete-consumption/<int:consumption_id>/", views.delete_consumption, name="delete_consumption"),
]