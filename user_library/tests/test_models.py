from django.test import TestCase
from django.db import IntegrityError
# from django.templatetags.static import static
from django.core.exceptions import ValidationError

import datetime

from movie.models import Movie
from user.models import User
from user_library.models import WatchList


class WatchlistModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.movie = Movie.objects.create(
            title="Mad Max",
            overview="some desert story..",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        cls.movie.full_clean()
        cls.movie.save()

        cls.movie_test = Movie.objects.create(
            title="Mad Max",
            overview="some desert story..",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        cls.movie_test.full_clean()
        cls.movie_test.save()

        cls.user = User.objects.create(
            username = "new_user",
            password = "someword"
            
        )
        cls.user.full_clean()
        cls.user.save()

        cls.wlist = WatchList.objects.create(
            user=cls.user,
            movie=cls.movie,
            serie=None,
            personal_note="Note to remember to watch",
            status="watching",
        )

        cls.wlist.full_clean()
        cls.wlist.save()

    def test_create_watchlist_instance(self):
        ''''''
        self.assertEqual(self.wlist.user.username, "new_user")
        self.assertIsNone(self.wlist.serie)
        self.assertIsNotNone(self.wlist.movie)
        self.assertEqual(str(self.wlist.movie), "Mad Max")

        self.assertEqual(type(self.wlist.personal_note), str)
        self.assertIn("to watch", self.wlist.personal_note)

    def test_status_valid(self):
        '''
        Check that Status entered is valid, as per the choice field.
        '''
        movie = Movie.objects.create(
            title="Mad Max2",
            overview="some new desert story..",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        movie.full_clean()
        movie.save()

        user_1 = User.objects.create(
            username = "user_1",
            password = "somepword"
            
        )
        user_1.full_clean()
        user_1.save()

        user_2 = User.objects.create(
            username = "user_2",
            password = "somepword2"
            
        )
        user_2.full_clean()
        user_2.save()

        wlist = WatchList.objects.create(
            user=user_1,
            movie=self.movie,
            serie=None,
            personal_note="",
            status="to watch",
        )

        wlist.full_clean()
        wlist.save()

        self.assertEqual(type(self.wlist.status), str)
        self.assertEqual(self.wlist.status, "watching")

    def test_status_constraints_validation(self):
        '''
        Check that Status entered is not valid, 
        if not as per the choice field .
        '''
        user_2 = User.objects.create(
            username = "user_2",
            password = "somepword2"
            
        )
        user_2.full_clean()
        user_2.save()

        # status random string, not in choices.
        wlist = WatchList.objects.create(
            user=user_2,
            movie=self.movie,
            serie=None,
            personal_note="",
            status="something ...",
        )

        # status empty string
        wlist_2 = WatchList.objects.create(
            user=self.user,
            movie=self.movie_test,
            serie=None,
            personal_note="",
            status="",
        )
        
        with self.assertRaises(ValidationError):
            wlist.full_clean()
            wlist.save()

        with self.assertRaises(ValidationError):
            wlist_2.full_clean()
            wlist_2.save()