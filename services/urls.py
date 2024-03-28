from django.urls import path, include
from rest_framework import routers

from .views import (
    ShowThemeViewSet,
    AstronomyShowViewSet,
    PlanetariumDomeViewSet,
    ShowSessionViewSet, ReservationViewSet
)

router = routers.DefaultRouter()
router.register("show_themes", ShowThemeViewSet)
router.register("shows", AstronomyShowViewSet)
router.register("domes", PlanetariumDomeViewSet)
router.register("sessions", ShowSessionViewSet)
router.register("reservations", ReservationViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "service"
