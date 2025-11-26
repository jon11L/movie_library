from django.test import TestCase
from django.db import IntegrityError
# from django.templatetags.static import static
from django.core.exceptions import ValidationError
from django.urls import reverse

import datetime

from movie.models import Movie
from serie.models import Serie
from user.models import User
from user_library.models import WatchList


# what test needed.
# a registered user login and add a movie in the watchlist -- Pass V
# a user remove his own watchlist entry. Should pass V
# non logged user try to add a movie in watchlist. Should fail
# a user try to remove a watchlist entry of another user. Should fail


class WatchListToggleEntryTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.movie = Movie.objects.create(
            title="Mad Max",
            overview="some desert story..",
            tmdb_id="1234",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        cls.movie.full_clean()
        cls.movie.save()

        cls.movie_2 = Movie.objects.create(
            title="Test movie",
            tmdb_id="4563",
            overview="some desert story..",
            release_date=datetime.datetime.strptime("2000-03-01", "%Y-%m-%d").date(),
        )
        cls.movie_2.full_clean()
        cls.movie_2.save()

        cls.serie = Serie.objects.create(
            title="Test serie",
            tmdb_id="1518",
            overview="some desert story..",
            first_air_date=datetime.datetime.strptime("2000-03-01", "%Y-%m-%d").date(),
        )
        cls.serie.full_clean()
        cls.serie.save()

        cls.user = User.objects.create_user(
            username = "new_user",
            password = "testpass"
        )
        cls.user.full_clean()
        cls.user.save()

        cls.user_2 = User.objects.create_user(
            username = "test_user",
            password = "someword"
            
        )
        cls.user_2.full_clean()
        cls.user_2.save()

        print(
            "\n\n ** Loading necessary component for testing watchlist's view with setUpTestDAta **\n\n",
        )


    def test_logged_user_watchlist_add_entry(self):
        '''
        ** Test view for the watchlist toggling Add/remove
        '''
        # 1) user logged in
        user = self.user

        login = self.client.login(username="new_user", password="testpass")
        self.assertTrue(login)

        #  Owner can Add an entry via POST on the toggle_watchlist() view
        # Technically by clicking on the bookmark icon button on the front-end
        # This will send the type of content that it is and the pk of the object
        url = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # check that the watchlist entry was created

        data = response.json()
        # Expect the view to report it was removed
        self.assertIn("in_watchlist", data)
        self.assertTrue(data["in_watchlist"])
        self.assertIn("added", data["message"])

        # user add another entry
        url_1 = reverse("user_library:toggle_watchlist", args=["serie", self.serie.pk])
        response_1 = self.client.post(url_1)

        new_data = response_1.json()
        self.assertTrue(new_data["in_watchlist"])

        wlist = WatchList.objects.filter(user=self.user)

        self.assertTrue(wlist.exists())
        self.assertEqual(str(wlist.last().movie), "Mad Max")

        self.assertTrue(wlist.first().serie)
        self.assertEqual(str(wlist.first().serie), "Test serie")
        self.assertEqual(wlist.first().serie.overview, "some desert story..")
        self.assertEqual(user.watchlist.count(), 2) # User has 2 entries

    def test_logged_user_watchlist_remove_entry(self):
        '''
        Test adding and removing a watchlist entry with an authenticated user
        '''
        # re-create owner's entry again / suppose to delete
        # 1) user logged in
        login = self.client.login(username="new_user", password="testpass")
        self.assertTrue(login)
        # Sent Post request
        url = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # check new Watchlist entry exist
        self.assertIn("in_watchlist", data)
        self.assertTrue(data["in_watchlist"])
        self.assertIn("added", data["message"])

        wlist = WatchList.objects.filter(user=self.user)

        self.assertTrue(wlist.exists())
        self.assertEqual(str(wlist.last().movie), "Mad Max")

        # Sent Post request, with the same existing Movie instance
        # therefore should remove it from DB
        url_2 = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])
        resp2 = self.client.post(url_2)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()

        # Check Watchlist entry does no longer exist
        self.assertIn("in_watchlist", data)
        self.assertFalse(data2["in_watchlist"])
        self.assertIn("removed", data2["message"])

        wlist_2 = WatchList.objects.filter(user=self.user)

        self.assertIn("in_watchlist", data2)
        self.assertFalse(wlist_2.exists())


    def test_user_not_logged_attempt_creating_entry(self):
        '''
        Test attempting to create a watchlist entry without an authenticated user.\n
        The attempt should fail and Throw an error
        '''
        # No user being logged in doing a POST request
        url = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])

        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 401) # Should throw Error
        self.assertFalse(WatchList.objects.filter(movie=self.movie).exists())
        
        data = response.json()
        self.assertEqual(data["error"], "Login required")
        self.assertIn("You must be logged", data["message"])


    def test_users_add_same_media_in_watchlist(self):
        '''
        -- Several users can add the same Movie or Serie
        indepently.
        one user action over their Watchlist entry does not affect the other
        '''
        user_1 = self.user
        user_2 = self.user_2

        # User_1 adding content in watchlist
        self.client.force_login(user_1)
        
        # Adding 1st movie
        url_1 = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])

        resp_1 = self.client.post(url_1)
        self.assertEqual(resp_1.status_code, 200)
        data_1 = resp_1.json()
        self.assertIn("added", data_1["message"])

        # Adding 1st serie
        url_2 = reverse("user_library:toggle_watchlist", args=["serie", self.serie.pk])

        resp_2 = self.client.post(url_2)
        self.assertEqual(resp_2.status_code, 200)
        data_2 = resp_2.json()
        self.assertTrue(data_2["in_watchlist"])
        self.assertIn("added", data_2["message"]) # confirm Media being added

        # logging the user 2
        self.client.force_login(user_2)

        # Adding 1st serie on New user 2 
        url_3 = reverse("user_library:toggle_watchlist", args=["serie", self.serie.pk])

        resp_3 = self.client.post(url_3)
        self.assertEqual(resp_3.status_code, 200)
        data_3 = resp_3.json()
        self.assertTrue(data_3["in_watchlist"])
        self.assertIn("added", data_3["message"])
        
        wlist_user_1 = user_1.watchlist.all().count()
        wlist_user_2 = user_2.watchlist.all().count()

        self.assertEqual(wlist_user_1, 2)# 2 entries with user_1
        self.assertEqual(wlist_user_2, 1)# 1 entry with user_2


class WatchListViewAccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.movie = Movie.objects.create(
            title="Mad Max",
            overview="some desert story..",
            tmdb_id="1234",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        cls.movie.full_clean()
        cls.movie.save()

        cls.movie_2 = Movie.objects.create(
            title="Test movie",
            tmdb_id="4563",
            overview="some desert story..",
            release_date=datetime.datetime.strptime("2000-03-01", "%Y-%m-%d").date(),
        )
        cls.movie_2.full_clean()
        cls.movie_2.save()

        cls.serie = Serie.objects.create(
            title="Test serie",
            tmdb_id="1518",
            overview="some desert story..",
            first_air_date=datetime.datetime.strptime("2000-03-01", "%Y-%m-%d").date(),
        )
        cls.serie.full_clean()
        cls.serie.save()


        cls.user = User.objects.create_user(
            username = "user01",
            password = "testpass"
        )
        cls.user.full_clean()
        cls.user.save()

        cls.user_2 = User.objects.create_user(
            username = "user02",
            password = "someword"
            
        )
        cls.user_2.full_clean()
        cls.user_2.save()
        print(
            "\n\n ** Loading necessary component for testing watchlist's view with setUpTestDAta **\n\n",
        )

        cls.wlist = WatchList(
            user=cls.user,
            movie=cls.movie,
            serie=None,
            personal_note="Note to remember to watch",
            status="watching",
        )
        cls.wlist.full_clean()
        cls.wlist.save()

        
        cls.wlist_2 = WatchList.objects.create(
            user=cls.user,
            movie=cls.movie_2,
            serie=None,
            personal_note="to watch",
            status="finished",
        )
        cls.wlist_2.full_clean()
        cls.wlist_2.save()

        cls.wlist_3 = WatchList.objects.create(
            user=cls.user,
            movie=None,
            serie=cls.serie,
            personal_note="Note to remember",
            status="dropped",
        )
        cls.wlist_3.full_clean()
        cls.wlist_3.save()


    def test_user_access_own_watchlist_view(self):
        '''
        Test that a logged in user can access his own watchlist view
        '''
        login = self.client.login(username="user01", password="testpass")
        self.assertTrue(login)
        url = reverse("user_library:watch_list", args=[self.user.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_library/watch_list.html")

    def test_user_canont_access_other_private_watchlist_(self):
        '''
        Test that a logged in user can not access another user watchlist view if set to private
        '''
        # user.private_watchlist is set to True by default
        # login with the 2nd user
        login = self.client.login(username="user02", password="someword")
        self.assertTrue(login)

        url = reverse("user_library:watch_list", args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Redirect 
        # self.assertTemplateUsed(response, "user/profile_page.html")


# Test that user can access the page of his watchlist list entries.
# test that if user.status_watchlist == "True" then watchlist is private
# else is public -> other users can access.
