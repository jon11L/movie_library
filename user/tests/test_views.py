from django.test import TestCase

# import datetime

from user.models import User
from django.urls import reverse


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
