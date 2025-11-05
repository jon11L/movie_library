from django.test import TestCase
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
            description="A high school chemistry teacher turned methamphetamine producer navigates the dangers of the drug trade while battling personal demons.",
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

    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        serie = self.serie  # Using the serie created in setUpTestData
        self.assertEqual(type(serie.original_title), str)
        self.assertEqual(serie.original_title, "Breaking Bad")
        self.assertEqual(serie.vote_count, 12000)
        self.assertEqual(serie.popularity, 45.0)
        self.assertEqual(serie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(serie.banner_images, ["banner1.jpg", "banner2.jpg"])

    def test_decription_field(self):
        """Test that the description field is saved correctly."""
        serie = self.serie
        self.assertIsNotNone(serie.description)
        self.assertEqual(type(serie.description), str)
        if serie.description:
            self.assertIn("chemistry teacher turned", serie.description)

    def test_tagline_field(self):
        """Test that the tagline field is saved correctly."""
        serie = self.serie
        self.assertEqual(type(serie.tagline), str)
        self.assertEqual(serie.tagline, "All bad things must come to an end.")

    def test_vote_average_field(self):
        """Test that the vote_average field is saved correctly."""
        serie = self.serie
        self.assertIsNotNone(serie.vote_average)
        self.assertEqual(type(serie.vote_average), float)
        self.assertEqual(serie.vote_average, 8.4)

    def test_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.serie.title, "The Wire")
        self.assertEqual(self.serie.title, "Breaking Bad")
        self.assertEqual(type(self.serie.title), str)

    def test_serie_status_field(self):   
        """Test that a serie can be marked as released."""
        # movie = Movie.objects.get(pk=1)
        self.assertEqual(type(self.serie.status), str)
        # self.assertTrue(self.serie.status)
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
        serie = self.serie
        self.assertIsInstance(serie.created_by, list)
        self.assertIsNotNone(serie.created_by)
        if serie.created_by:
            self.assertIn("Vince Gilligan", serie.created_by)
            self.assertEqual(len(serie.created_by), 1)

    def test_serie_production_field(self):
        """Test that the production field can store a list of strings."""
        serie = self.serie
        self.assertIsInstance(serie.production, list)
        self.assertIsNotNone(serie.production)
        if serie.production:
            self.assertIn("HBO", serie.production)
            self.assertEqual(len(serie.production), 1)

    def test_serie_original_language_field(self):
        """Test that the original_language field is saved correctly."""
        serie = self.serie
        self.assertIsNotNone(serie.original_language)
        self.assertEqual(type(serie.original_language), str)
        if serie.original_language:
            self.assertEqual(serie.original_language, "en")
            self.assertIn("en", serie.original_language)

    def test_serie_spoken_languages_field(self):
        """Test that the spoken_languages field can store a list of strings."""
        serie = self.serie
        self.assertIsInstance(serie.spoken_languages, list)
        self.assertIsNotNone(serie.spoken_languages)
        if serie.spoken_languages:
            self.assertIn("en", serie.spoken_languages)
            self.assertIn("de", serie.spoken_languages)
            self.assertEqual(len(serie.spoken_languages), 2)

    def test_serie_origin_country_field(self):
        """Test that the origin_country field can store a list of strings."""
        serie = self.serie
        self.assertIsInstance(serie.origin_country, list)
        self.assertIsNotNone(serie.origin_country)
        if serie.origin_country:
            self.assertIn("US", serie.origin_country)
            self.assertEqual(len(serie.origin_country), 1)

    def test_serie_first_air_date_field(self):
        """Test that the first_air_date field is saved correctly."""
        serie = self.serie
        self.assertIsNotNone(serie.first_air_date)
        self.assertEqual(type(serie.first_air_date), datetime.date)
        self.assertEqual(serie.first_air_date, datetime.date(2008, 7, 5))

    def test_serie_last_air_date_field(self):
        """Test that the last_air_date field is saved correctly."""
        serie = self.serie
        self.assertIsNotNone(serie.last_air_date)
        self.assertEqual(type(serie.last_air_date), datetime.date)
        self.assertEqual(serie.last_air_date, datetime.date(2013, 8, 5))

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
        Serie.objects.create(title="Dark", tmdb_id=12345)

        with self.assertRaises(Exception):  # Should raise IntegrityError
            Serie.objects.create(title="futurama", tmdb_id=12345)


class SerieModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # ARRANGE: Set up test data
        Serie.objects.create(
            title="Breaking Bad",
            genre=["Action", "Sci-Fi"],
            production=["HBO"],
            created_by=["Vince Gilligan"],
        )

        Serie.objects.create(
            title="Westworld",
            genre=["Action", "Sci-Fi", "Thriller"],
            production=["HBO"],
            created_by=["Jonathan Nolan", "Lisa Joy"]
        )

        print("\n-- **SetupTestData for SerieModelMethodTest started.**\n")

    def test_serie_exists(self):
        """Test that the serie exists in the database."""
        serie_count = Serie.objects.count()
        self.assertEqual(serie_count, 2)
        for serie in Serie.objects.all():
            print(f"{serie} -- {serie.pk}")

    def test_serie_created(self):
        """Test that the serie is created successfully."""
        serie = Serie.objects.get(title="Breaking Bad")
        self.assertIsNotNone(serie)
        self.assertEqual(serie.title, "Breaking Bad")

    def test_serie_str_method(self):
        """Test the __str__ method of the Serie object."""
        serie = Serie.objects.get(title="Breaking Bad")
        self.assertEqual(str(serie), "Breaking Bad")

    def test_render_genre(self):
        serie = Serie.objects.get(title="Breaking Bad")
        serie_2 = Serie.objects.get(title="Westworld")
        self.assertEqual(type(serie.render_genre()), str)
        self.assertEqual(serie.render_genre(), "Action - Sci-Fi")
        self.assertNotEqual(serie_2.render_genre(), "Horror - Sci-Fi")
        self.assertEqual(serie_2.render_genre(), "Action - Sci-Fi - Thriller")

    def test_render_production(self):
        serie = Serie.objects.get(title="Breaking Bad")
        self.assertEqual(type(serie.render_production()), str)
        self.assertEqual(serie.render_production(), "HBO")
        self.assertNotEqual(serie.render_production(), "Warner Bros.")

    def test_render_created_by(self):
        serie = Serie.objects.get(title="Breaking Bad")
        self.assertEqual(type(serie.render_created_by()), str)
        self.assertEqual(serie.render_created_by(), "Vince Gilligan")
        self.assertNotEqual(serie.render_created_by(), "John Doe")

    def test_render_vote_average(self):
        serie = Serie.objects.get(title="Breaking Bad")
        serie.vote_average = 8.456
        self.assertEqual(serie.render_vote_average(), 8.5)
        self.assertNotEqual(serie.render_vote_average(), 6)
        serie.vote_average = 7.123
        self.assertEqual(serie.render_vote_average(), 7.1)


    def test_render_poster_images(self):
            serie = Serie.objects.get(title="Breaking Bad")
            serie.poster_images = ["poster1.jpg", "poster2.jpg"]
            self.assertNotEqual(serie.render_poster(), "poster1.jpg")
            self.assertEqual(serie.render_poster(), "https://image.tmdb.org/t/p/w500poster1.jpg")
            self.assertNotEqual(serie.render_poster(), "poster2.jpg")
