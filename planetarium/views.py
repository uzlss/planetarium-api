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

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    @staticmethod
    def _params_to_int(str_ids):
        return [int(str_id) for str_id in str_ids.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        show_title = self.request.query_params.get("show_title")
        dome_name = self.request.query_params.get("dome_name")
        date = self.request.query_params.get("date")
        if show_title:
            queryset = queryset.filter(astronomy_show__title__icontains=show_title)
        if dome_name:
            queryset = queryset.filter(planetarium_dome__name__icontains=dome_name)
        if date:
            queryset = queryset.filter(show_time__date=date)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "astronomy_show",
                "planetarium_dome",
            )

        return queryset.distinct()


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
        queryset = self.queryset.filter(user=self.request.user)

        date = self.request.query_params.get("date")
        show_session = self.request.query_params.get("show_session")
        if date:
            queryset = queryset.filter(created_at__date=date)
        if show_session:
            queryset = queryset.filter(tickets__show_session__id=int(show_session))

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("tickets")

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReservationRetrieveSerializer
        return self.serializer_class
