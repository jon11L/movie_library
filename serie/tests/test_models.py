from django.test import TestCase
from serie.models import Serie, Season, Episode
# import unittest
import datetime

class SerieModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
    # def setUp(self):
        cls.serie = Serie.objects.create(
            imdb_id="tt0903747",
            tmdb_id= 1396,
            original_title="Breaking Bad",
            title="Breaking Bad",
            description="A high school chemistry teacher turned methamphetamine producer navigates the dangers of the drug trade while battling personal demons.",
            tagline="All bad things must come to an end.",
            genre=["Drama", "Crime", "Thriller" ],
            # first_air_date=datetime.datetime.strptime("2008-07-05 ", '%Y-%m-%d').date(),
            first_air_date=datetime.date(1999, 10, 15),
            last_air_date=datetime.datetime.strptime("2013-08-05", '%Y-%m-%d').date(),
            origin_country=[ "US" ],
            original_language="en",
            spoken_languages=["en", "de"],
            production=["HBO"],
            # director=["David Fincher"],
            created_by=["Vince Gilligan"],
            status="Released",
            # budget=63000000,
            # revenue=100853753,
            vote_average=8.4,
            vote_count=12000,
            # imdb_rating=8.8,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
            # trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}],
        )

            # casting=[
            #     {"name": "Brad Pitt", "role": "Tyler Durden"},
            #     {"name": "Edward Norton", "role": "The Narrator"},
            #     {"name": "Helena Bonham Carter", "role": "Marla Singer"},
            #     {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
            #     ],

    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        serie = self.serie  # Using the movie created in setUpTestData
        self.assertEqual(serie.original_title, "Breaking Bad")
        # self.assertEqual(serie.description, "A high school chemistry teacher turned methamphetamine producer navigates the dangers of the drug trade while battling personal demons.")
        # self.assertEqual(type(serie.description), str)
        self.assertEqual(serie.tagline, "All bad things must come to an end.")
        self.assertEqual(serie.genre, ["Drama", "Crime", "Thriller"])
        self.assertEqual(serie.first_air_date, datetime.date(1999, 10, 15))
        self.assertEqual(serie.last_air_date, datetime.date(2013, 8, 5))
        # self.assertEqual(serie.length, 139)
        self.assertTrue(serie.status)
        # self.assertEqual(serie.director, ["David Fincher"])
        self.assertEqual(serie.created_by, ["Vince Gilligan"])
        self.assertEqual(serie.production, ["HBO"])
        # self.assertEqual(serie.casting, [
        #     {"name": "Brad Pitt", "role": "Tyler Durden"},
        #     {"name": "Edward Norton", "role": "The Narrator"},
        #     {"name": "Helena Bonham Carter", "role": "Marla Singer"},
        #     {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
        #     ])
        self.assertEqual(serie.origin_country, ["US"])
        self.assertEqual(serie.original_language, "en")
        self.assertEqual(serie.spoken_languages, ["en", "de"])
        self.assertEqual(serie.status, "Released")
        # self.assertEqual(serie.budget, 63000000)
        # self.assertEqual(serie.revenue, 100853753)
        self.assertEqual(serie.vote_average, 8.4)
        self.assertEqual(serie.vote_count, 12000)
        self.assertEqual(serie.popularity, 45.0)
        self.assertEqual(serie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(serie.banner_images, ["banner1.jpg", "banner2.jpg"])
        # self.assertEqual(serie.trailers, [{"key": "8hP9D6kZseM", "website": "youtube"}])

    def test_serie_str_method(self):
        """Test the __str__ method of the Serie model."""
        # movie = self.movie
        self.assertEqual(str(self.serie), "Breaking Bad")


    def test_decription_field(self):
        """Test that the description field is saved correctly."""
        serie = self.serie
        self.assertEqual(serie.description, "A high school chemistry teacher turned methamphetamine producer navigates the dangers of the drug trade while battling personal demons.")
        self.assertEqual(type(serie.description), str)

    def test_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.serie.title, "The Wire")
        self.assertEqual(self.serie.title, "Breaking Bad")
        self.assertEqual(type(self.serie.title), str)

    def test_serie_status_field(self):   
        """Test that a movie can be marked as released."""
        # movie = Movie.objects.get(pk=1)
        self.assertEqual(type(self.serie.status), str)
        self.assertTrue(self.serie.status)
        self.assertTrue(self.serie.status == "Released")
        self.assertIsNotNone(self.serie.status)

    def test_serie_genre_field(self):
        """Test that the genre field can store a list of strings."""
        self.assertIsInstance(self.serie.genre, list)
        self.assertIsNotNone(self.serie.genre)
        if self.serie.genre:
            self.assertIn("Drama", self.serie.genre)
            self.assertIn("Thriller", self.serie.genre)
            self.assertEqual(len(self.serie.genre), 3)

    # may go with Core app (but here tied to Movie model)
    def test_slug_generated_on_save(self):
        """Test that a slug is generated upon saving the serie."""
        self.assertIsNotNone(self.serie.slug)
        self.assertEqual(type(self.serie.slug), str)
        self.assertIn("breaking-bad", self.serie.slug)
        self.assertRegex(self.serie.slug, r'breaking-bad-[0-9]*-\w*\d')

    def test_serie_creation_with_required_fields_only(self):
        """Test creating a movie with only the title (required field)."""
        serie = Serie.objects.create(
            title="Inception",
            tmdb_id=27205
            )
        
        self.assertEqual(serie.title, "Inception")
        self.assertIsNotNone(serie.pk)  # Has a database ID


    def test_serie_tmdb_id_unique_constraint(self):
        """Test that tmdb_id must be unique."""
        Serie.objects.create(title="", tmdb_id=12345)
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Serie.objects.create(title="", tmdb_id=12345)

    # def test_movie_creation_missing_required_fields(self):
    #     pass


class SerieModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # ARRANGE: Set up test data
        Serie.objects.create(
            title="Breaking Bad",
            genre=["Action", "Sci-Fi"],
            # casting=[{"name": "Leonardo DiCaprio", "role": "Cobb"}, {"name": "Joseph Gordon-Levitt", "role": "Arthur"}],
            # writer=["Christopher Nolan"],
            created_by=["Vince Gilligan"],
            production=["HBO"],
            # director=["Christopher Nolan"]
        )
        Serie.objects.create(
            title="Westworld",
            genre=["Action", "Sci-Fi", "Thriller"],
            # casting=[{"name": "Evan Rachel Wood", "role": "Dolores"}, {"name": "Thandie Newton", "role": "Maeve"}],
            # writer=["Christopher Nolan"],
            production=["HBO"],
            # director=["Jonathan Nolan", "Lisa Joy"]
        )


    def test_serie_str_returns_title(self):
        """
        Test that the __str__ method returns the serie's title.
        """
        serie = Serie.objects.get(id=1)

        result = str(serie)
        self.assertEqual(result, "Breaking Bad")

    def test_render_genre(self):
        # Suppose to pass
        serie = Serie.objects.get(id=1)
        self.assertEqual(serie.render_genre(), "Action - Sci-Fi")
        serie = Serie.objects.get(id=2)
        self.assertEqual(serie.render_genre(), "Action - Sci-Fi - Thriller")
        # Suppose to fail
        serie = Serie.objects.get(id=2)
        self.assertNotEqual(serie.render_genre(), "Horror - Sci-Fi")

    # def test_render_casting(self):
    #     movie = Serie.objects.get(id=1)
    #     self.assertEqual(movie.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")

    #     movie_2 = Movie.objects.get(id=2)
    #     self.assertNotEqual(movie_2.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")

    def test_render_created_by(self):
        serie = Serie.objects.get(id=1)
        self.assertEqual(serie.render_created_by(), "Vince Gilligan")

    def test_render_production(self):
        serie = Serie.objects.get(id=1)
        self.assertEqual(serie.render_production(), "HBO")

    # def test_render_director(self):
    #     serie = Serie.objects.get(id=1)
    #     self.assertEqual(serie.render_director(), "Christopher Nolan")
