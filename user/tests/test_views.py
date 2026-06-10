from django.test import TestCase

# import datetime

from user.models import User
from django.urls import reverse

class LoginLogoutTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")

        print(
            "\n\n ** Loading  necessary component for testing User's login/logout with setUpTestDAta **\n\n",
        )

    def test_login_page(self):
        """Test that the login page loads correctly."""
        # response = self.client.get("/user/login")
        response = self.client.get(reverse("user:login"))
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")
        self.assertTemplateUsed(response, "user/login.html")

    def test_user_login(self):
        """Test that a user can log in with correct credentials."""
        fail_login = self.client.login(username="user", password="password")
        login = self.client.login(username="testuser", password="testpass")
        self.assertFalse(fail_login)
        self.assertTrue(login)

    def test_user_logout(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("user:logout"))
        self.assertNotEqual(response.status_code, 404)  # Redirect after logout
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertRedirects(response, "/")


class ProfileViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")

        print(
            "\n\n ** Loading necessary component for testing Profile's view with setUpTestDAta **\n\n",
        )

    def test_profile_view_logged_in(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(f"/user/profile/{self.user.pk}")
        url = reverse("user:profile_page", kwargs={"pk": self.user.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/profile_page.html")

    def test_profile_view_not_logged_in(self):
        url = reverse("user:profile_page", kwargs={"pk": self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/user/profile/{self.user.pk}")
        self.assertEqual(response.status_code, 302)  # Redirect to login page




