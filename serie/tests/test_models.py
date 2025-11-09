from django.test import TestCase
from django.db import IntegrityError
from django.templatetags.static import static

from serie.models import Serie, Season, Episode
# import unittest
import datetime

class SerieModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # def setUp(self):
        print("\n-- **SetupTestData for SerieModelSaveTest started.**\n")

        cls.serie = Serie.objects.create(
            imdb_id="tt0903747",
            tmdb_id= 1396,
            original_title="Breaking Bad",
            title="Breaking Bad",
            overview="A high school chemistry teacher turned methamphetamine producer navigates the dangers of the drug trade while battling personal demons.",
            tagline="All bad things must come to an end.",
            genre=["Drama", "Crime", "Thriller" ],
            # first_air_date=datetime.datetime.strptime("2008-07-05 ", '%Y-%m-%d').date(),
            first_air_date=datetime.date(2008, 7, 5),
            last_air_date=datetime.datetime.strptime("2013-08-05", '%Y-%m-%d').date(),
            origin_country=[ "US" ],
            original_language="en",
            spoken_languages=["en", "de"],
            production=["HBO"],
            created_by=["Vince Gilligan"],
            status="Released",
            vote_average=8.4,
            vote_count=12000,
            # imdb_rating=8.8,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
        )

        cls.serie_2 = Serie.objects.create(
            title="Westworld",
            genre=["Action", "Sci-Fi", "Thriller"],
            production=["HBO"],
            created_by=["Jonathan Nolan", "Lisa Joy"]
        )

    def test_serie_created(self):
        """Test that the serie is created successfully."""
        self.assertIsNotNone(self.serie)
        self.assertIsNotNone(self.serie_2)
        self.assertEqual(self.serie.title, "Breaking Bad")
        self.assertEqual(self.serie_2.title, "Westworld")

    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        self.assertEqual(type(self.serie.original_title), str)
        self.assertEqual(self.serie.original_title, "Breaking Bad")
        self.assertEqual(self.serie.vote_count, 12000)
        self.assertEqual(self.serie.popularity, 45.0)
        self.assertEqual(self.serie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(self.serie.banner_images, ["banner1.jpg", "banner2.jpg"])

    def test_decription_field(self):
        """Test that the description field is saved correctly."""
        self.assertIsNotNone(self.serie.overview)
        self.assertEqual(type(self.serie.overview), str)
        if self.serie.overview:
            self.assertIn("chemistry teacher turned", self.serie.overview)

    def test_tagline_field(self):
        """Test that the tagline field is saved correctly."""
        self.assertEqual(type(self.serie.tagline), str)
        self.assertEqual(self.serie.tagline, "All bad things must come to an end.")

    def test_vote_average_field(self):
        """Test that the vote_average field is saved correctly."""
        self.assertIsNotNone(self.serie.vote_average)
        self.assertEqual(type(self.serie.vote_average), float)
        self.assertEqual(self.serie.vote_average, 8.4)

    def test_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.serie.title, "The Wire")
        self.assertEqual(self.serie.title, "Breaking Bad")
        self.assertEqual(type(self.serie.title), str)

    def test_serie_status_field(self):   
        """Test that a serie can be marked as released."""
        self.assertEqual(type(self.serie.status), str)
        self.assertIsNotNone(self.serie.status)
        self.assertTrue(self.serie.status == "Released")

    def test_serie_genre_field(self):
        """Test that the genre field can store a list of strings."""
        self.assertIsInstance(self.serie.genre, list)
        self.assertIsNotNone(self.serie.genre)
        if self.serie.genre:
            self.assertIn("Drama", self.serie.genre)
            self.assertIn("Thriller", self.serie.genre)
            self.assertEqual(len(self.serie.genre), 3)

    def test_serie_created_by_field(self):
        """Test that the created_by field can store a list of strings."""
        self.assertIsInstance(self.serie.created_by, list)
        self.assertIsNotNone(self.serie.created_by)
        if self.serie.created_by:
            self.assertIn("Vince Gilligan", self.serie.created_by)
            self.assertEqual(len(self.serie.created_by), 1)

    def test_serie_production_field(self):
        """Test that the production field can store a list of strings."""
        self.assertIsInstance(self.serie.production, list)
        self.assertIsNotNone(self.serie.production)
        if self.serie.production:
            self.assertIn("HBO", self.serie.production)
            self.assertEqual(len(self.serie.production), 1)

    def test_serie_original_language_field(self):
        """Test that the original_language field is saved correctly."""
        self.assertIsNotNone(self.serie.original_language)
        self.assertEqual(type(self.serie.original_language), str)
        if self.serie.original_language:
            self.assertEqual(self.serie.original_language, "en")
            self.assertIn("en", self.serie.original_language)

    def test_serie_spoken_languages_field(self):
        """Test that the spoken_languages field can store a list of strings."""
        self.assertIsInstance(self.serie.spoken_languages, list)
        self.assertIsNotNone(self.serie.spoken_languages)
        if self.serie.spoken_languages:
            self.assertIn("en", self.serie.spoken_languages)
            self.assertIn("de", self.serie.spoken_languages)
            self.assertEqual(len(self.serie.spoken_languages), 2)

    def test_serie_origin_country_field(self):
        """Test that the origin_country field can store a list of strings."""
        self.assertIsInstance(self.serie.origin_country, list)
        self.assertIsNotNone(self.serie.origin_country)
        if self.serie.origin_country:
            self.assertIn("US", self.serie.origin_country)
            self.assertEqual(len(self.serie.origin_country), 1)

    def test_serie_first_air_date_field(self):
        """Test that the first_air_date field is saved correctly."""
        self.assertIsNotNone(self.serie.first_air_date)
        self.assertEqual(type(self.serie.first_air_date), datetime.date)
        self.assertEqual(self.serie.first_air_date, datetime.date(2008, 7, 5))

    def test_serie_last_air_date_field(self):
        """Test that the last_air_date field is saved correctly."""
        self.assertIsNotNone(self.serie.last_air_date)
        self.assertEqual(type(self.serie.last_air_date), datetime.date)
        self.assertEqual(self.serie.last_air_date, datetime.date(2013, 8, 5))

    # may go with Core app (but here tied to Movie model)
    def test_slug_generated_on_save(self):
        """Test that a slug is generated upon saving the serie."""
        self.assertIsNotNone(self.serie.slug)
        self.assertEqual(type(self.serie.slug), str)
        if self.serie.slug:
            self.assertIn("breaking-bad", self.serie.slug)
            self.assertRegex(self.serie.slug, r'breaking-bad-[0-9]*-\w*\d')

    def test_serie_slug_creation_without_first_air_date(self):
        """Test creating a serie and slug without first_air_date."""
        serie_2 = Serie.objects.create(
            title="serie 2 test",
            tmdb_id=5678,
            )
        self.assertIsNotNone(serie_2.slug)
        self.assertEqual(type(serie_2.slug), str)
        if not serie_2.first_air_date and serie_2.slug:
            self.assertIn("serie-2-test", serie_2.slug)
            self.assertRegex(serie_2.slug, r'serie-2-test-[0-9]*-?\w*\d')
            # self.assertRegex(serie_2.slug, r'serie-2-test-\w*\d')

    def test_serie_creation_with_required_fields_only(self):
        """Test creating a movie with only the title (required field)."""
        serie = Serie.objects.create(
            title="Serie test 1",
            tmdb_id=12405
            )

        self.assertEqual(serie.title, "Serie test 1")
        self.assertIsNotNone(serie.pk)  # Has a database ID

    # Create new series in the setUpTestData to then test it here, avoid missmatch Id
    def test_serie_tmdb_id_unique_constraint(self):
        """Test that tmdb_id must be unique."""
        with self.assertRaises(IntegrityError):  # Should raise IntegrityError
            Serie.objects.create(title="futurama", tmdb_id=1396)


class SerieModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.serie = Serie.objects.create(
            title="Breaking Bad",
            genre=["Action", "Sci-Fi"],
            production=["HBO"],
            created_by=["Vince Gilligan"],
            poster_images=["/poster1.jpg", "/poster2.jpg"],
            banner_images=["/banner1.jpg", "/banner2.jpg"],
        )

        cls.serie_2 = Serie.objects.create(
            title="Westworld",
            genre=["Action", "Sci-Fi", "Thriller"],
            production=["HBO"],
            created_by=["Jonathan Nolan", "Lisa Joy"]
        )

        print("\n-- **SetupTestData for SerieModelMethodTest started.**\n")

    # def test_serie_exists(self):
    #     """Test that the serie exists in the database."""
    #     serie_count = Serie.objects.count()
    #     self.assertEqual(serie_count, 2)
    #     for serie in Serie.objects.all():
    #         print(f"{serie} -- {serie.pk}")

    def test_serie_str_method(self):
        """Test the __str__ method of the Serie object."""
        self.assertEqual(str(self.serie), "Breaking Bad")
        self.assertNotEqual(str(self.serie_2), "Breaking Bad")
        self.assertEqual(str(self.serie_2), "Westworld")

    def test_render_genre(self):
        '''Test the render_genre method of the Serie object.'''
        self.assertEqual(type(self.serie.render_genre()), str)
        self.assertEqual(self.serie.render_genre(), "Action - Sci-Fi")
        self.assertNotEqual(self.serie_2.render_genre(), "Horror - Sci-Fi")
        self.assertEqual(self.serie_2.render_genre(), "Action - Sci-Fi - Thriller")

    def test_render_production(self):
        '''Test the render_production method of the Serie object.'''
        self.assertEqual(type(self.serie.render_production()), str)
        self.assertEqual(self.serie.render_production(), "HBO")
        self.assertNotEqual(self.serie.render_production(), "Warner Bros.")

    def test_render_created_by(self):
        '''Test the render_created_by method of the Serie object.'''
        self.assertEqual(type(self.serie.render_created_by()), str)
        self.assertNotEqual(self.serie.render_created_by(), "John Doe")
        self.assertEqual(self.serie.render_created_by(), "Vince Gilligan")

    def test_render_vote_average(self):
        '''
        Test the render_vote_average method of the Serie object.
        Should render the vote_average rounded to one decimal place.
        '''
        self.serie.vote_average = 8.456
        self.assertNotEqual(self.serie.render_vote_average(), 6)
        self.assertEqual(self.serie.render_vote_average(), 8.5)
        self.serie_2.vote_average = 7.123
        self.assertEqual(self.serie_2.render_vote_average(), 7.1)

    def test_render_banner_images(self):
        ''' 
        test the render_banner method.
        Should return full url: preffix + random image name from the field's list
        '''
        self.assertNotEqual(self.serie.render_banner(), "/banner1.jpg")
        self.assertNotEqual(self.serie.render_banner(), "/banner2.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w1280", self.serie.render_banner())
        # no banner image set in serie_2
        self.assertEqual(self.serie_2.render_banner(), static("images/default_banner_photo.jpg"))

    def test_render_poster_images(self):
        self.assertNotEqual(self.serie.render_poster(), "/poster1.jpg")
        self.assertNotEqual(self.serie.render_poster(), "/poster2.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w500", self.serie.render_poster())
        self.assertEqual(
            self.serie.render_poster(), "https://image.tmdb.org/t/p/w500/poster1.jpg"
        )
        # no poster image set in serie_2
        self.assertEqual(self.serie_2.render_poster(), static("images/default_poster_photo.jpg"))



class SeasonModelSaveTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.serie = Serie.objects.create(
            title="Breaking Bad",
            tmdb_id=1396
        )
        cls.serie_2 = Serie.objects.create(
            title="From",
            tmdb_id=2250
        )
        cls.season_1 = Season.objects.create(
            serie=cls.serie,
            name="Season 1",
            season_number=1,
            overview="The beginning of the end.",
            producer=["Vince Ghiligan"],
            casting=[""],
            poster_images=["poster_1.jpg" "poster_2.jpg",],
            tmdb_id = 21446
        )
        cls.season_2 = Season.objects.create(
            serie=cls.serie,
            name="Season 2",
            season_number=2,
            )

        cls.season_0 = Season.objects.create(
            serie=cls.serie,
            name="Season without num2",
            season_number=0,
            )

        print("\n-- **SetupTestData for SeasonModelSaveTest started.**\n")

    def test_seasons_created(self):
        """Test that the serie is created successfully."""
        self.assertIsNotNone(self.season_1)
        self.assertIsNotNone(self.season_2)
        self.assertEqual(str(self.season_1), "Season 1")
        self.assertEqual(str(self.season_2), "Season 2")

    def test_season_name_field(self):
        """Test that the name field is saved correctly."""
        self.assertIsNotNone(self.season_1.name)
        self.assertEqual(type(self.season_1.name), str)
        if self.season_1.name:
            self.assertIn("Season", self.season_1.name)
            self.assertEqual(self.season_1.name, "Season 1")

    def test_season_number_field(self):
        """Test that the season_number field is saved correctly."""
        self.assertIsNotNone(self.season_1.season_number)
        self.assertEqual(type(self.season_1.season_number), int)
        self.assertEqual(self.season_1.season_number, 1)
        self.assertEqual(self.season_2.season_number, 2)

    def test_season_overview_field(self):
        """Test that the overview field is saved correctly."""
        self.assertIsNotNone(self.season_1.overview)
        self.assertEqual(type(self.season_1.overview), str)
        if self.season_1 .overview:
            self.assertIn("the end", self.season_1.overview)
            self.assertEqual(self.season_1.overview, "The beginning of the end.")

    # test producer and casting
    # def test_season_producer(self):
    #     """Test that the producer field is saved correctly."""
    #     pass


    # def test_season_casting_field(self):
    #     """Test that the casting field is saved correctly."""
    #     pass



    # --- test constraints on model, relationship, and unique constraints -----
    def test_season_has_serie_relationship(self):
        """Test that the season is linked to the correct serie."""
        self.assertIsNotNone(self.season_1.serie)
        self.assertEqual(self.season_1.serie.title, "Breaking Bad")

    # --- Test that are suppose to fails: ---
    def test_season_without_season_number_field(self):
        """Test that the serie fails to save if no season_number field."""
        # Default value '0' already used above in setupdata().
        with self.assertRaises(Exception): 
            season = Season.objects.create(
                name="Season test",
                serie=self.serie
                )

    def test_season_unique_together_constraint(self):
        """Test that the combination of serie and season_number is unique."""
        with self.assertRaises(IntegrityError):
            Season.objects.create(
                serie=self.serie,
                season_number=1,
                name="Duplicate Season 1",
                casting=["Actor A", "Actor B"],
            )

    def test_season_without_serie_field(self):
        """Test that the serie fails to save if no serie field."""
        with self.assertRaises(Exception): 
            season = Season.objects.create(
                name="Season without serie",
                season_number=2
                )
            
    def test_season_tmdb_id_unique_constraint(self):
        """
        Test that season's tmdb_id is unique.\n
        Fail on attempting to create a new season with an already existing tmdb_id.
        """
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Season.objects.create(name="Season test unique id", tmdb_id=21446)



class SeasonModelMethodTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.serie = Serie.objects.create(
            title="Breaking Bad",
            tmdb_id=1396
        )
        cls.season_1 = Season.objects.create(
            serie=cls.serie,
            name="Season 1",
            season_number=1,
            overview="The beginning of the end.",
            casting=[
                {"name": "Bryan Cranston", "role": "Walter White"},
                {"name": "Aaron Paul", "role": "Jesse Pinkman"}
                ],
            poster_images=["/poster_1.jpg", "/poster_2.jpg"]

        )
        cls.season_2 = Season.objects.create(
            serie=cls.serie,
            name="Season 2",
            season_number=2
            )
        
        print("\n-- **SetupTestData for SeasonModelMethodTest started.**\n")


    def test_season_str_method(self):
        """Test the __str__ method of the Season object."""
        self.assertEqual(str(self.season_1), "Season 1")

    def test_render_poster_images(self):
        self.assertNotEqual(self.season_1.render_poster(), "/poster_1.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w500", self.season_1.render_poster())
        # self.assertEqual(
        #     self.season_1.render_poster(), "https://image.tmdb.org/t/p/w500/poster_1.jpg"
        # )
        self.assertNotEqual(self.season_1.render_poster(), "/poster_2.jpg")
        # no poster image set in season_2
        self.assertEqual(self.season_2.render_poster(), static("images/default_poster_photo.jpg"))


class EpisodeModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.serie = Serie.objects.create(
            title="Breaking Bad",
            tmdb_id=1396
        )

        cls.season = Season.objects.create(
            serie=cls.serie,
            season_number=1,
            name="Season 1",
            overview="The beginning of the end."
        )
        cls.episode = Episode.objects.create(
            season=cls.season,
            episode_number=1,
            title="Pilot",
            overview="High school chemistry teacher Walter White's life is suddenly transformed.",
            release_date=datetime.date(2008, 1, 20),
            guest_star = [""],
            director = [""],
            writer = [""],
            banner_images=["banner_1.jpg", "banner_2.jpg"],
            tmdb_id = 12586
        )

        cls.episode_0 = Episode.objects.create(
        season=cls.season,
        title="Episode without num special",
        episode_number=0
        )
        cls.episode_2 = Episode.objects.create(
        season=cls.season,
        title="Episode without num2",
        episode_number=2
        )

        print("\n-- **SetupTestData for EpisodeModelSaveTest started.**\n")

    # # just to check the PK of the series
    # def test_serie_exists(self):
    #     """Test that the serie exists in the database."""
    #     serie_count = Serie.objects.count()
    #     print(f"Total series in DB: {serie_count}")
    #     for serie in Serie.objects.all():
    #         print(f"{serie} -- {serie.pk}")
    # # ----------------------------

    def test_episode_number_field(self):
        """Test that the episode_number field is saved correctly."""
        self.assertIsNotNone(self.episode.episode_number)
        self.assertEqual(type(self.episode.episode_number), int)
        self.assertEqual(self.episode.episode_number, 1)

    def test_episode_title_field(self):
        """Test that the title field is saved correctly."""
        self.assertIsNotNone(self.episode.title)
        self.assertEqual(type(self.episode.title), str)
        self.assertEqual(self.episode.title, "Pilot")

    def test_episode_overview_field(self):
        """Test that the overview field is saved correctly."""
        self.assertIsNotNone(self.episode.overview)
        self.assertEqual(type(self.episode.overview), str)
        if self.episode.overview:
            self.assertIn(
                "Walter White's life", self.episode.overview
            )

    def test_release_date(self):
        """Test the render_release_date method."""
        self.assertIsNotNone(self.episode.release_date)
        self.assertEqual(type(self.episode.release_date), datetime.date)
        self.assertEqual(self.episode.release_date, datetime.date(2008, 1, 20))

    def test_correct_season_association(self):
        """Test that the episode is correctly associated with its season."""
        self.assertEqual(self.episode.season, self.season)
        self.assertEqual(self.episode.season.season_number, 1)
        self.assertEqual(self.episode.season.name, "Season 1")
        # self.assertEqual(self.episode.season.serie.title, "Breaking Bad")

    def test_episode_unique_together_constraint(self):
        """Test that the combination of season and episode_number is unique."""
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Episode.objects.create(
                season=self.season,
                episode_number=1,
                title="Test Duplicate Pilot"
            )

    def test_episode_without_season_field(self):
        """Test that the episode fails to save if no season field."""
        with self.assertRaises(Exception): 
            episode = Episode.objects.create(
                episode_number=2,
                title="Episode without season"
                )

    def test_episode_without_episode_number_field(self):
        """Test that the episode fails to save if no episode_number field."""
        # Default value '0' already used above in setupdata().
        with self.assertRaises(Exception):
            episode = Episode.objects.create(
                season=self.season,
                title="Episode without number"
                )


class EpisodeModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.serie = Serie.objects.create(
            title="Breaking Bad",
            tmdb_id=1396
        )

        cls.season = Season.objects.create(
            serie=cls.serie,
            season_number=1,
            name="Season 1",
            overview="The beginning of the end."
        )
        cls.episode = Episode.objects.create(
            season=cls.season,
            episode_number=1,
            title="Pilot",
            release_date=datetime.date(2008, 1, 20),
            overview="High school chemistry teacher Walter White's life is suddenly transformed.",
            banner_images=["/banner_1.jpg", "/banner_2.jpg"],

        )

        cls.episode_0 = Episode.objects.create(
        season=cls.season,
        title="Episode without num special",
        episode_number=0
        )
        cls.episode_2 = Episode.objects.create(
        season=cls.season,
        title="Episode without num2",
        episode_number=2
        )
        cls.episode_3 = Episode.objects.create(
        season=cls.season,
        title="Episode 3",
        episode_number=3
        )

        print("\n-- **SetupTestData for EpisodeModelMethodTest started.**\n")

    def test_episode_str_method(self):
        """Test the __str__ method of the Episode object."""
        self.assertEqual(str(self.episode), "Episode 1 - Pilot")
        self.assertNotEqual(str(self.episode_3), "Episode 3 - Pilot")
        self.assertEqual(str(self.episode_3), "Episode 3")


    def test_render_banner_images(self):
        ''' 
        test the render_banner method.
        Should return full url: preffix + random image name from the field's list
        '''
        self.assertNotEqual(self.episode.render_banner(), "/banner1.jpg")
        self.assertNotEqual(self.episode.render_banner(), None)
        # self.assertEqual(self.episode.render_banner(), "https://image.tmdb.org/t/p/w1280/banner_1.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w1280", self.episode.render_banner())
        # no banner image set in episode_2
        self.assertEqual(self.episode_2.render_banner(), static("images/default_banner_photo.jpg"))
