from django.test import TestCase
from accounts.forms import UserRegistrationForm
from accounts.models import User, UserBankAccount, BankAccountType
import datetime


class UserRegistrationFormTestCase(TestCase):
    def setUp(self):
        self.account_type = BankAccountType.objects.create(
            name="Test Account Type",
            maximum_withdrawal_amount=1000,
            annual_interest_rate=1,
            interest_calculation_per_year=12,
        )

    def test_user_registration_form_valid(self):
        form = UserRegistrationForm(
            data={
                "first_name": "cris",
                "last_name": "ron",
                "email": "crisron@example.com",
                "password1": "mypassword123",
                "password2": "mypassword123",
                "account_type": self.account_type.id,
                "gender": "M",
                "birth_date": "1990-01-01",
            }
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        # Check if the user was created
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "cris")
        self.assertEqual(user.last_name, "ron")
        self.assertEqual(user.email, "crisron@example.com")

        # Check if the UserBankAccount was created
        user_bank_account = UserBankAccount.objects.get(user=user)
        self.assertIsNotNone(user_bank_account)
        self.assertEqual(user_bank_account.account_type, self.account_type)
        self.assertEqual(user_bank_account.gender, "M")
        self.assertEqual(user_bank_account.birth_date, datetime.date(1990, 1, 1))
