from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=63,)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255,)
    description = models.TextField()
    theme = models.ManyToManyField(
        ShowTheme, related_name="astronomy_shows"
    )

    def __str__(self):
        return f"Show: {self.title}, theme: {self.theme}"


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=63, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return f"Dome: {self.name} (rows: {self.rows}, seats_in_row: {self})"

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )

    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])
        reservation = Reservation.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation

    class Meta:
        ordering = ["-created_at"]


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow, on_delete=models.CASCADE, related_name="sessions")
    planetarium_dome = models.ForeignKey(
        PlanetariumDome, on_delete=models.CASCADE, related_name="sessions"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return (f"Show: {self.astronomy_show},"
                f"{self.planetarium_dome},"
                f"at time: {self.show_time}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome, error_to_raise):
        for (ticket_attr_value,
             ticket_attr_name, 
             planetarium_dome_attr_name) in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(planetarium_dome,
                                  planetarium_dome_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {planetarium_dome_attr_name}): "
                        f"(1, {count_attrs})"
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
        return (f"Ticket: {self.id},"
                f"(row: {self.row}, seat: {self.seat})."
                f"Session info: {self.show_session}\n")

    class Meta:
        unique_together = (
            "show_session", "reservation", "row", "seat"
        )
        ordering = ("row", "seat")
