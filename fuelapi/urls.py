from django.urls import path
from .views import route_view, route_form_page

urlpatterns = [
    path("route/", route_view, name="route_view"),
    path("", route_form_page, name="route_form"),
]
