from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from planetarium.models import (
    ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Reservation,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly

from planetarium.serializers import (
    ShowThemeSerializer, AstronomyShowSerializer, PlanetariumDomeSerializer, ShowSessionSerializer,
    ReservationSerializer, ShowSessionListSerializer, ShowSessionRetrieveSerializer,
    ReservationRetrieveSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show",
        "planetarium_dome",
    )
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer

        return self.serializer_class


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAuthenticated(), ]
        return [IsAdminOrIfAuthenticatedReadOnly(), ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReservationRetrieveSerializer
        return self.serializer_class
