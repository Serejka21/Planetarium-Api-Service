from django.contrib import admin

from .models import (
    User,
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    Reservation,
    ShowSession, Ticket
)

admin.site.register(User)
admin.site.register(PlanetariumDome)
admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(Reservation)
admin.site.register(ShowSession)
admin.site.register(Ticket)
