from django.test import TestCase
from django.db import IntegrityError
# from django.templatetags.static import static
from django.core.exceptions import ValidationError

import datetime

from media_library.models import Media, Movie, Serie

from user.models import User
from watchlist.models import WatchList


# what test needed.

# Full valid watchlist - should pass - done V
# Watchlist without Media (serie, movie) - should fail  V
# Watchlist with both Media (serie, movie) - should fail V
# - check media from watchlist - should pass V
# removie watchlist entry - should pass V
# - check valid status (choice field) - should pass V
# - check status not valid if not in (choice field) - should fail - done V
# Create a watchlist entry without a user - should fail
# using another user , not request.user (logged in user) - should fail
# create a watchlist entry, with already existing user-media - should fail, already existing


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
            title="Test movie",
            overview="some desert story..",
            release_date=datetime.datetime.strptime("2000-03-01", "%Y-%m-%d").date(),
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
            media=cls.movie,
            personal_note="Note to remember to watch",
            status="watching",
        )
        cls.wlist.full_clean()
        cls.wlist.save()


    def test_check_watchlist_instance_correctly_saved(self):
        ''''''
        self.assertEqual(self.wlist.user.username, "new_user")
        # self.assertIsNone(self.wlist.serie)
        self.assertIsNotNone(self.wlist.media)
        self.assertEqual(str(self.wlist.media), "Mad Max")

        self.assertEqual(type(self.wlist.personal_note), str)
        self.assertIn("Note to remember", self.wlist.personal_note)
        self.assertEqual(self.wlist.status, "watching")

    def test_remove_watchlist_entry(self):
        """
        Deleting a watchlist entry should remove it from the database.
        only authenticated user if equal to user related to the watchlist can delete it
        """
        # to check with current user 
        w = WatchList.objects.create(
            user=self.user,
            media=self.movie_test,
            personal_note="to delete",
            status="to watch",
        )
        w.full_clean()
        w.save()
        self.assertEqual(w.media.title, "Test movie")
        self.assertEqual(w.user.username, "new_user")

        w.delete()

        self.assertFalse(WatchList.objects.filter(id=w.pk).exists())
        with self.assertRaises(Exception):
            w.refresh_from_db()

    def test_status_in_choice_status_valid(self):
        '''
        Check that Status entered is valid, as per the Status.choice field.
        '''
        movie = Movie.objects.create(
            title="Mad Max 2",
            overview="some new desert story..",
            release_date=datetime.datetime.strptime("1998-10-08", "%Y-%m-%d").date(),
        )
        movie.full_clean()
        movie.save()

        wlist = WatchList.objects.create(
            user=self.user,
            media=movie,
            personal_note="test status choice field",
            status="to watch",
        )
        wlist.full_clean()
        wlist.save()

        self.assertEqual(type(wlist.status), str)
        self.assertNotEqual(wlist.status, "watching")
        self.assertEqual(wlist.status, "to watch")

    def test_status_null_value_is_valid(self):
        '''
        Check that Status entered is valid, as per the choice field.
        '''
        movie = Movie.objects.create(
            title="test status null",
            overview="",
            release_date=datetime.datetime.strptime("2000-10-01", "%Y-%m-%d").date(),
        )
        movie.full_clean()
        movie.save()

        user_1 = User.objects.create(
            username = "user_1",
            password = "somepword"

        )
        user_1.full_clean()
        user_1.save()
        wlist_null = WatchList.objects.create(
            user=user_1,
            media=movie,
            personal_note="",
            status=None,
        )
        wlist_null.full_clean()
        wlist_null.save()
        self.assertNotEqual(wlist_null.status, "watching")
        self.assertIsNone(wlist_null.status)

    def test_user_has_several_watchlist_entry(self):
        ''''
        Test that a user can have several watchlist entries.
        '''
        movie = Movie.objects.create(
            title="Some movie",
            overview="movie one",
            release_date=datetime.datetime.strptime("2001-02-03", "%Y-%m-%d").date(),
        )
        movie.full_clean()
        movie.save()

        serie = Serie.objects.create(
            title="Some Serie",
            overview="serie one",
            first_air_date=datetime.datetime.strptime("2001-02-03", "%Y-%m-%d").date(),
        )
        serie.full_clean()
        serie.save()

        new_user = User.objects.create(
            username="new_user22",
            password="passs_123"
        )
        new_user.full_clean()
        new_user.save()

        wlist_1 = WatchList(
            user=new_user,
            media=serie,
            personal_note="",
            status="to watch",
        )
        wlist_1.full_clean()
        wlist_1.save()

        wlist_2= WatchList(
            user=new_user,
            media=movie,
            personal_note="duplicate",
            status="watching",
        )
        wlist_2.full_clean()
        wlist_2.save()

        wlist_3 = WatchList(
            user=new_user,
            media=self.movie, # "Mad Max. in setUpData"
            personal_note="duplicate...",
            status="to watch",
        )
        wlist_3.full_clean()
        wlist_3.save()

        # ordered by is -id therefore last() for 1st entry
        # 3 object created in wathclist with ths user
        self.assertEqual(new_user.watchlist.count(), 3) 
        self.assertEqual(str(new_user.watchlist.last().media), "Some Serie")
        # self.assertIsNone(new_user.watchlist.last().movie)
        self.assertEqual(str(new_user.watchlist.first().media), "Mad Max")
        # self.assertIsNone(new_user.watchlist.first().serie)

    def test_media_accessible_from_watchlist(self):
        """
        Ensure Media (movie or serie) references on watchlist entries behave as expected.
        and are then accessible from Watchlist object with foreign relationship
        """
        # movie entry (already present in setUpTestData as self.wlist)
        self.assertIsNotNone(self.wlist.media)
        self.assertEqual(str(self.wlist.media), "Mad Max")

        # serie entry
        serie = Serie.objects.create(
            title="Some Serie",
            overview="serie overview",
            first_air_date=datetime.datetime.strptime("2001-02-03", "%Y-%m-%d").date(),
        )
        serie.full_clean()
        serie.save()

        w_list = WatchList.objects.create(
            user=self.user,
            media=serie,
            personal_note="serie note",
            status="to watch",
        )
        w_list.full_clean()
        w_list.save()

        self.assertIsNotNone(w_list.media)
        self.assertEqual(str(w_list.media), "Some Serie")
        self.assertEqual(w_list.media.release_date, datetime.date(2001, 2, 3))



    # --- Test Constraints, validation that fails --------
    def test_status_not_in_choice_constraints_validation(self):
        '''
        Check that Status entered is not valid.\n 
        if not validated as per the choice field .
        '''
        user_2 = User.objects.create(
            username = "user_2",
            password = "somepword2"
            
        )
        user_2.full_clean()
        user_2.save()

        # status random string, not in Status.choices. - Should fail
        wlist = WatchList.objects.create(
            user=user_2,
            media=self.movie,
            personal_note="",
            status="not in status Choice",
        )
        
        with self.assertRaises(ValidationError):
            wlist.full_clean()
            wlist.save()

    def test_status_empty_string_constraints_validation(self):
        ''' '''
        # status empty string -- Should fail
        wlist_2 = WatchList.objects.create(
            user=self.user,
            media=self.movie_test,
            personal_note="",
            status="",
        )
        wlist_2.full_clean()
        wlist_2.save()

        self.assertIsNotNone(wlist_2.status)
        self.assertEqual(wlist_2.status, "")

    def test_media_null_raise_validation_error(self):
        '''
        A watchlist entry must reference a Media instance.\n
        Test without reference should raise a validation error
        '''
        duplicate = WatchList(
            user=self.user,
            media=None,
            personal_note="duplicate",
            status="to watch",
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
            duplicate.save()

    def test_create_without_user_raises_integrity_error(self):
        """
        User is required on WatchList; attempting to save without a user.\n
        Test should fail.
        """
        # prepare the object instance without a user
        wlist = WatchList(
            media=self.movie_test,
            personal_note="no user",
            status="to watch",
        )

        with self.assertRaises(IntegrityError):
            wlist.save()

    def test_prevent_duplicate_user_media_entry(self):
        """
        The model should prevent creating duplicate watchlist entries for the same user+media.\n
        Attempting to create the same user/movie pair again should fail 
        (DB validator constraint).\n
        - DB constraint: user-movie-serie must be unique combination 
        - Also if movie == something then Serie must == None 
        """
        # prepare the object instance 
        duplicate = WatchList(
            user=self.user,
            media=self.movie,
            personal_note="duplicate",
            status="to watch",
        )
        # depending on model validations, either full_clean or save will raise;
        # we check save for DB-level unique constraint.
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
            duplicate.save()
