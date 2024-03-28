from django.test import TestCase
from django.contrib.auth import get_user_model

from user.serializers import UserSerializer


class UserManagerTestCase(TestCase):
    def test_create_user(self):
        user = get_user_model()
        email = "test@test.com"
        password = "testpassword"
        user = user.objects.create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = get_user_model()
        email = "admin@test.com"
        password = "adminpassword"
        superuser = user.objects.create_superuser(email, password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class UserSerializerTestCase(TestCase):
    def test_create_user(self):
        data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertFalse(user.is_staff)

    def test_create_user_with_invalid_password(self):
        data = {
            "email": "test@example.com",
            "password": "1234",
        }
        serializer = UserSerializer(data=data)
        is_valid = serializer.is_valid()

        if not is_valid:
            errors = serializer.errors
            error_message = errors["password"][0]
            self.assertEqual(error_message, "Ensure this field has at least 5 characters.")

    def test_update_user(self):
        user = get_user_model().objects.create_user(
            email="test1@test.com",
            password="testpassword",
        )
        new_email = "new_email@test.com"
        data = {
            "email": new_email,
        }
        serializer = UserSerializer(instance=user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.email, new_email)

    def test_update_user_with_password(self):
        user = get_user_model().objects.create_user(
            email="test2@test.com",
            password="testpassword",
        )
        new_password = "newpassword"
        data = {
            "password": new_password,
        }
        serializer = UserSerializer(instance=user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password(new_password))
