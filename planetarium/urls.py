from django.urls import path, include
from rest_framework import routers

from planetarium.views import TicketViewSet, ShowThemeViewSet, AstronomyShowViewSet, PlanetariumDomeViewSet, \
    ShowSessionViewSet, ReservationViewSet

app_name = "planetarium"

router = routers.DefaultRouter()
router.register("themes", ShowThemeViewSet)
router.register("shows", AstronomyShowViewSet)
router.register("domes", PlanetariumDomeViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("reservations", ReservationViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [path("", include(router.urls))]