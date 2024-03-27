from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    Ticket,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = '__all__'


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = '__all__'


class AstronomyShowListSerializer(serializers.ModelSerializer):
    theme = ShowThemeSerializer(many=True, read_only=True)

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "theme")


class AstronomyShowDetailSerializer(serializers.ModelSerializer):
    theme = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "theme")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity"
        )


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
        )


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show_title = serializers.CharField(
        source="astronomy_show.title", read_only=True, slug_field="title"
    )
    planetarium_dome_name = serializers.CharField(
       source="planetarium_dome.name", read_only=True, slug_field="name"
    )
    show_session_capacity = serializers.IntegerField(
        source="planetarium_dome.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show_title",
            "planetarium_dome_name",
            "show_time",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer(many=False, read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show",
            "planetarium_dome",
            "show_time",
            "taken_places",
        )
