from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.astronomy_show} {self.show_time}"
        )


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE
    )

    @staticmethod
    def validate_ticket(
            row,
            seat,
            planetarium_dome,
            error_to_raise
    ):
        for (
                ticket_attr_value,
                ticket_attr_name,
                planetarium_dome_attr_name
        ) in [
            (row, "row", "rows"),
            (seat, "seat", "seats"),
        ]:
            count_attrs = getattr(
                planetarium_dome,
                planetarium_dome_attr_name
            )
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: (
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {planetarium_dome_attr_name}): "
                            f"(1, {count_attrs})"
                        )
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.show_session} (row: {self.row}, seat: {self.seat})"
