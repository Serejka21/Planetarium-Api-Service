from datetime import datetime
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status

from services.models import ShowTheme, AstronomyShow, PlanetariumDome, ShowSession, Ticket, Reservation
from services.serializers import AstronomyShowSerializer, TicketSerializer, ReservationSerializer


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def tearDown(self):
        get_user_model().objects.all().delete()
        Token.objects.all().delete()


class ShowThemeViewSetTestCase(BaseTestCase):
    def test_list_show_themes_authorized_user(self):
        response = self.client.get("/api/planetarium/show_themes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_show_theme(self):
        data = {'name': 'Test Theme'}
        response = self.client.post("/api/planetarium/show_themes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShowTheme.objects.filter(
            name=data['name']).exists()
                        )


class AstronomyShowViewSetTestCase(BaseTestCase):

    def test_list_astronomy_shows(self):
        response = self.client.get("/api/planetarium/shows/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_astronomy_show(self):
        theme_data = {'name': 'Test Theme'}
        theme = ShowTheme.objects.create(**theme_data)
        show_data = {'title': 'Test Show',
                     'description': 'testdescr',
                     'theme': [theme.id]}
        response = self.client.post(
            "/api/planetarium/shows/", show_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AstronomyShow.objects.filter(title="Test Show").exists())
        created_object = AstronomyShow.objects.get(title="Test Show")
        serializer = AstronomyShowSerializer(created_object)
        data_without_id = serializer.data.copy()
        del data_without_id['id']
        self.assertEqual(data_without_id, show_data)


class PlanetariumDomeViewSetTestCase(BaseTestCase):

    def test_list_planetarium_domes(self):
        response = self.client.get("/api/planetarium/domes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_planetarium_dome(self):
        data = {'name': 'Test Dome',
                'rows': 15,
                'seats_in_row': 15}
        response = self.client.post("/api/planetarium/domes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PlanetariumDome.objects.filter(
            name=data['name']).exists()
                        )

    def test_capacity_dome(self):
        data = {'name': 'Test Dome',
                'rows': 5,
                'seats_in_row': 10}
        dome = PlanetariumDome.objects.create(**data)
        self.assertEqual(
            dome.capacity, data['rows'] * data['seats_in_row']
        )


class ShowSessionViewSetTestCase(BaseTestCase):

    def test_list_show_sessions(self):
        response = self.client.get("/api/planetarium/sessions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_show_session(self):
        theme = ShowTheme.objects.create(name="Test Theme")
        astronomy_show = AstronomyShow.objects.create(
            title="Test Show", description="Test Description"
        )
        astronomy_show.theme.add(theme)
        planetarium_dome = PlanetariumDome.objects.create(
            name="Test Dome", rows=5, seats_in_row=10
        )
        data = {
            'astronomy_show': astronomy_show.id,
            'planetarium_dome': planetarium_dome.id,
            'show_time': datetime.now().isoformat()
        }

        response = self.client.post(
            "/api/planetarium/sessions/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(ShowSession.objects.filter(
            astronomy_show=astronomy_show,
            planetarium_dome=planetarium_dome).exists()
                        )


class ReservationViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.planetarium_dome = PlanetariumDome.objects.create(
            name="Test Dome", rows=5, seats_in_row=10
        )
        self.theme = ShowTheme.objects.create(name="Test Theme")
        self.astronomy_show = AstronomyShow.objects.create(
            title="Test Show", description="Test Description"
        )
        self.astronomy_show.theme.add(self.theme)
        data = {
            'astronomy_show': self.astronomy_show,
            'planetarium_dome': self.planetarium_dome,
            'show_time': datetime.now().isoformat()
        }
        self.show_session = ShowSession.objects.create(
            **data
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_reservation_creation(self):
        tickets_data = [
            {'row': 1,
             'seat': 1,
             'show_session': self.show_session.id},
            {'row': 2,
             'seat': 2,
             'show_session': self.show_session.id}]
        user = get_user_model().objects.create_user(
            email="test2@test.com",
            password="testpass",
            is_staff=True,
        )
        serializer = ReservationSerializer(
            data={"user": user.id,
                  "tickets": tickets_data},
        )
        self.assertTrue(serializer.is_valid())
        reservation = serializer.save()
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.user, user)

        self.assertEqual(reservation.tickets.count(), len(tickets_data))
        for ticket_data in tickets_data:
            self.assertTrue(Ticket.objects.filter(
                reservation=reservation, **ticket_data).exists()
            )

    def test_list_reservations(self):
        response = self.client.get("/api/planetarium/reservations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TicketSerializerTestCase(TestCase):
    def setUp(self):
        self.planetarium_dome = PlanetariumDome.objects.create(
            name="Test Dome", rows=5, seats_in_row=10
        )
        self.theme = ShowTheme.objects.create(name="Test Theme")
        self.astronomy_show = AstronomyShow.objects.create(
            title="Test Show", description="Test Description"
        )
        self.astronomy_show.theme.add(self.theme)
        data = {
            'astronomy_show': self.astronomy_show,
            'planetarium_dome': self.planetarium_dome,
            'show_time': datetime.now().isoformat()
        }
        self.show_session = ShowSession.objects.create(
            **data
        )

    def test_ticket_validation_in_serializer(self):
        reservation = Reservation.objects.create(
            user=get_user_model().objects.create_user(
                email="test@test.com",
                password="testpassword",
                is_staff=True,
            )
        )
        valid_data = {
            'row': 1,
            'seat': 1,
            'show_session': self.show_session.id,
            'reservation': reservation.id
        }
        serializer = TicketSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        Ticket.objects.create(
            row=1,
            seat=1,
            show_session=self.show_session,
            reservation=reservation)
        invalid_data = {
            'row': 1,
            'seat': 1,
            'show_session': self.show_session.id,
            'reservation': reservation.id
        }
        serializer = TicketSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "This seat is already occupied for this show session.",
            serializer.errors["non_field_errors"])

    def test_ticket_validation(self):
        ticket = Ticket()
        ticket.row = 1
        ticket.seat = 1
        planetarium_dome = self.planetarium_dome

        self.assertIsNone(Ticket.validate_ticket(1, 1, planetarium_dome, ValidationError))

        with self.assertRaises(ValidationError) as context:
            Ticket.validate_ticket(0, 1, planetarium_dome, ValidationError)
        self.assertEqual(
            context.exception.messages,
            ['row number must be in available range: '
             '(1, rows): (1, 5)'])

        with self.assertRaises(ValidationError) as context:
            Ticket.validate_ticket(1, 0, planetarium_dome, ValidationError)
        self.assertEqual(
            context.exception.messages,
            ['seat number must be in available range: '
             '(1, seats_in_row): (1, 10)'])
