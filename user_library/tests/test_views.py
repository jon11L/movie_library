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
# a registered user login and add a movie in the watchlist -- (toggle_watch)
# non logged user try to add a movie in watchlist. Should fail
# a user remove his own watchlist entry. Should pass
# a user try to remove a watchlist entry of another user. Should fail


class WatchListViewTest(TestCase):

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
        # cls.wlist = WatchList.objects.create(
        #     user=cls.user,
        #     movie=cls.movie,
        #     serie=None,
        #     personal_note="Note to remember to watch",
        #     status="watching",
        # )
        # cls.wlist.full_clean()
        # cls.wlist.save()


    def test_logged_user_watchlist_add_entry(self):
        '''** Test view for the watchlist toggling Add/remove '''
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
        
        self.assertEqual(user.watchlist.count(), 2) 


    def test_logged_user_watchlist_remove_entry(self):
        '''  '''
        # re-create owner's entry again / suppose to delete
        # 1) user logged in
        user = self.user

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
        '''  '''
        # No user being logged in.
        url = reverse("user_library:toggle_watchlist", args=["movie", self.movie.pk])

        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 401) # Should throw Error



    # def test_wrong_user_attempt__create_other_user_entry(self):
    #     pass


    # def test_wrong_user_attempt_remove_other_user_entry(self):
    #     pass
