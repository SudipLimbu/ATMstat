from django.test import TestCase
from accounts.models import User


class UserTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.assertEqual(user.email, "test@example.com")
