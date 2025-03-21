from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
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
            f"Show session"
            f"(id: {self.id}, "
            f"astronomy show: {self.astronomy_show} "
            f"planetarium dome: {self.planetarium_dome})"
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
