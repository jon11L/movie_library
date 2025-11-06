from django.test import TestCase

import datetime

from user.models import User

# TODO test for:
# -  user, profile creation
#  login, logout views.
# test post save when user is created, profile is also created.
# profile views
# update profile

# Create your tests here.

class CreateUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_user(self):
        self.assertIsNotNone(self.user)
        self.assertNotEqual(self.user.username, 'user')
        self.assertEqual(self.user.username, 'testuser')
        self.assertFalse(self.user.check_password('password'))
        self.assertTrue(self.user.check_password('testpass'))

    def test_update_user(self):
        self.user.username = 'testuser001'
        self.user.save()
        self.assertNotEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.username, 'testuser001')


class ProfileTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def test_user_profile_created(self):
        '''
        test that when a user is created, a profile is also created via post_save signal
        Then test that we can update the profile fields.
        '''
        profile = self.user.profile
        profile.date_of_birth = datetime.datetime.strptime("1992-10-08", '%Y-%m-%d').date()
        profile.bio = 'This is a test bio.'
        profile.save()

        self.assertIsNotNone(profile)
        self.assertEqual(type(profile.date_of_birth), datetime.date)
        self.assertEqual(profile.date_of_birth, datetime.date(1992,10,8))
        self.assertEqual(type(profile.bio), str)
        self.assertEqual(profile.bio, 'This is a test bio.')

    def test_update_profile_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/user/profile/{self.user.pk}/update_profile', {
            # 'username': 'updateduser',
            'date_of_birth': datetime.datetime.strptime("1991-10-24", '%Y-%m-%d').date(),
            'bio': 'Updated bio.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertNotEqual(profile.date_of_birth, datetime.date(1992, 10, 8))
        self.assertEqual(profile.date_of_birth, datetime.date(1991, 10, 24))
        self.assertNotEqual(profile.bio, 'This is a test bio.')
        self.assertEqual(profile.bio, 'Updated bio.')


class LoginLogoutTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def test_login_page(self):
        '''Test that the login page loads correctly.'''
        response = self.client.get('/user/login')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)
        self.assertContains(response, 'login')
        self.assertTemplateUsed(response, 'user/login.html')

    def test_user_can_login(self):
        '''Test that a user can log in with correct credentials.'''
        fail_login = self.client.login(username='user', password='password')
        login = self.client.login(username='testuser', password='testpass')
        self.assertFalse(fail_login)
        self.assertTrue(login)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/user/logout')
        self.assertNotEqual(response.status_code, 404)  # Redirect after logout
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertRedirects(response, '/')


class ProfileViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(f'/user/profile/{self.user.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile_page.html')

    def test_profile_view_not_logged_in(self):
        response = self.client.get(f'/user/profile/{self.user.pk}')
        self.assertEqual(response.status_code, 302)  # Redirect to login page