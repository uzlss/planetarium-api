from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly

from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    ReservationRetrieveSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "string"},
                description="Filter by the name (ex. ?name=Space)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type={"type": "string"},
                description="Filter by the title(ex. ?title=Astronomy)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "string"},
                description="Filter by the name (ex. ?name=Space)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset

        show_title = self.request.query_params.get("show_title")
        dome_name = self.request.query_params.get("dome_name")
        date = self.request.query_params.get("date")
        if show_title:
            queryset = queryset.filter(
                astronomy_show__title__icontains=show_title
            )
        if dome_name:
            queryset = queryset.filter(
                planetarium_dome__name__icontains=dome_name
            )
        if date:
            queryset = queryset.filter(show_time__date=date)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "astronomy_show",
                "planetarium_dome",
            ).annotate(
                tickets_available=(
                    F("planetarium_dome__rows")
                    * F("planetarium_dome__seats_in_row")
                    - Count("ticket")
                )
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_title",
                type={"type": "string"},
                description="Filter by astronomy show title"
                " (ex. ?show_title=Astronomy)",
            ),
            OpenApiParameter(
                "dome_name",
                type={"type": "string"},
                description="Filter by planetarium dome name"
                " (ex. ?dome_name=Space)",
            ),
            OpenApiParameter(
                "date",
                type={"type": "datetime"},
                description="Filter by show time date (ex. ?date=2020-10-10)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
            return [
                IsAuthenticated(),
            ]
        return [
            IsAdminOrIfAuthenticatedReadOnly(),
        ]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        date = self.request.query_params.get("date")
        show_session = self.request.query_params.get("show_session")
        if date:
            queryset = queryset.filter(created_at__date=date)
        if show_session:
            queryset = queryset.filter(
                tickets__show_session__id=int(show_session)
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("tickets")

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReservationRetrieveSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "show_session",
                type={"type": "number"},
                description="Filter by show session id (ex. ?show_session=2)",
            ),
            OpenApiParameter(
                "date",
                type={"type": "datetime"},
                description="Filter by ticket"
                " reservation date"
                " (ex. ?date=2020-10-10)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
