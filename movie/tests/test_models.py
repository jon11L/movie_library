from django.test import TestCase
from movie.models import Movie
# import unittest
import datetime

class MovieModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
    # def setUp(self):
        cls.movie = Movie.objects.create(
            tmdb_id=550,
            imdb_id="tt0137523",
            original_title="Fight Club",
            title="Fight Club",
            description="A ticking-time-bomb insomniac and a slippery soap salesman channel primal..",
            tagline="Mischief. Mayhem. Soap.",
            genre=["Drama", "Thriller"],
            release_date=datetime.datetime.strptime("1999-10-15", '%Y-%m-%d').date(),
            origin_country=["US"],
            original_language="en",
            spoken_languages=["en", "de"],
            length=139,
            released=True,
            production=["20th Century Fox"],
            director=["David Fincher"],
            writer=["Chuck Palahniuk", "Jim Uhls"],
            casting=[
                {"name": "Brad Pitt", "role": "Tyler Durden"},
                {"name": "Edward Norton", "role": "The Narrator"},
                {"name": "Helena Bonham Carter", "role": "Marla Singer"},
                {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
                ],
            status="Released",
            budget=63000000,
            revenue=100853753,
            vote_average=8.4,
            vote_count=1700000,
            imdb_rating=8.8,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
            trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}],
        )


    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        movie = self.movie  # Using the movie created in setUpTestData
        self.assertEqual(movie.original_title, "Fight Club")
        self.assertEqual(movie.description, "A ticking-time-bomb insomniac and a slippery soap salesman channel primal..")
        self.assertEqual(movie.tagline, "Mischief. Mayhem. Soap.")
        self.assertEqual(movie.genre, ["Drama", "Thriller"])
        self.assertEqual(movie.release_date, datetime.date(1999, 10, 15))
        self.assertEqual(movie.length, 139)
        self.assertTrue(movie.released)
        self.assertEqual(movie.director, ["David Fincher"])
        self.assertEqual(movie.writer, ["Chuck Palahniuk", "Jim Uhls"])
        self.assertEqual(movie.production, ["20th Century Fox"])
        self.assertEqual(movie.casting, [
            {"name": "Brad Pitt", "role": "Tyler Durden"},
            {"name": "Edward Norton", "role": "The Narrator"},
            {"name": "Helena Bonham Carter", "role": "Marla Singer"},
            {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
            ])
        self.assertEqual(movie.origin_country, ["US"])
        self.assertEqual(movie.original_language, "en")
        self.assertEqual(movie.spoken_languages, ["en", "de"])
        self.assertEqual(movie.status, "Released")
        self.assertEqual(movie.budget, 63000000)
        self.assertEqual(movie.revenue, 100853753)
        self.assertEqual(movie.vote_average, 8.4)
        self.assertEqual(movie.vote_count, 1700000)
        self.assertEqual(movie.imdb_rating, 8.8)
        self.assertEqual(movie.popularity, 45.0)
        self.assertEqual(movie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(movie.banner_images, ["banner1.jpg", "banner2.jpg"])
        self.assertEqual(movie.trailers, [{"key": "8hP9D6kZseM", "website": "youtube"}])


    def test_movie_str_method(self):
        """Test the __str__ method of the Movie model."""
        # movie = self.movie
        self.assertEqual(str(self.movie), "Fight Club")
    
    def check_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.movie.title, "Inception")
        self.assertEqual(self.movie.title, "Fight Club")

    def test_movie_released_field(self):   
        """Test that a movie can be marked as released."""
        # movie = Movie.objects.get(pk=1)
        self.assertTrue(self.movie.released)

    def test_movie_genre_field(self):
        """Test that the genre field can store a list of strings."""
        self.assertIsInstance(self.movie.genre, list)
        self.assertIn("Drama", self.movie.genre)
        self.assertIn("Thriller", self.movie.genre)
        self.assertEqual(len(self.movie.genre), 2)

    # may go with Core app (but here tied to Movie model)
    def test_slug_generated_on_save(self):
        """Test that a slug is generated upon saving the movie."""
        self.assertIsNotNone(self.movie.slug)
        self.assertEqual(type(self.movie.slug), str)
        self.assertIn("fight-club", self.movie.slug)
        self.assertRegex(self.movie.slug, r'fight-club-[0-9]*-\w*\d')

    def test_movie_creation_with_required_fields_only(self):
        """Test creating a movie with only the title (required field)."""
        movie = Movie.objects.create(
            title="Inception",
            tmdb_id=27205
            )
        
        self.assertEqual(movie.title, "Inception")
        self.assertIsNotNone(movie.pk)  # Has a database ID


    def test_movie_tmdb_id_unique_constraint(self):
        """Test that tmdb_id must be unique."""
        Movie.objects.create(title="Movie 1", tmdb_id=12345)
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Movie.objects.create(title="Movie 2", tmdb_id=12345)

    # def test_movie_creation_missing_required_fields(self):
    #     pass


class MovieModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # ARRANGE: Set up test data
        Movie.objects.create(
            title="Inception",
            genre=["Action", "Sci-Fi"],
            casting=[{"name": "Leonardo DiCaprio", "role": "Cobb"}, {"name": "Joseph Gordon-Levitt", "role": "Arthur"}],
            writer=["Christopher Nolan"],
            production=["Warner Bros."],
            director=["Christopher Nolan"]
        )
        Movie.objects.create(
            title="the dark knight",
            genre=["Action", "Sci-Fi", "Thriller"],
            casting=[{"name": "Christian Bale", "role": "Bruce Wayne"}, {"name": "Heath Ledger", "role": "Joker"}],
            writer=["Christopher Nolan"],
            production=["Warner Bros."],
            director=["Christopher Nolan"]
        )
        # Movie.objects.create(
        #     original_title="Fight Club",
        #     title="Fight Club",
        #     description="A ticking-time-bomb insomniac and a slippery soap salesman channel primal..",
        #     tagline="Mischief. Mayhem. Soap.",
        #     genre=["Drama", "Thriller"],
        #     release_date="1999-10-15",
        #     length=139,
        #     released=True,
        #     director=["David Fincher"],
        #     writer=["Chuck Palahniuk", "Jim Uhls"],
        #     production=["20th Century Fox"],
        #     casting=[
        #         {"name": "Brad Pitt", "role": "Tyler Durden"},
        #         {"name": "Edward Norton", "role": "The Narrator"},
        #         {"name": "Helena Bonham Carter", "role": "Marla Singer"},
        #         {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
        #         ],
        #     origin_country=["US"],
        #     original_language="en",
        #     spoken_languages=["en", "de"],
        #     status="Released",
        #     budget=63000000,
        #     revenue=100853753,
        #     vote_average=8.4,
        #     vote_count=1700000,
        #     imdb_rating=8.8,
        #     popularity=45.0,
        #     poster_images=["poster1.jpg", "poster2.jpg"],
        #     banner_images=["banner1.jpg", "banner2.jpg"],
        #     trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}]
        # )


    # def setUp(self):
    #     Movie.objects.create(
    #         title="Inception",
    #         genre=["Action", "Sci-Fi"],
    #         casting=[{"name": "Leonardo DiCaprio", "role": "Cobb"}, {"name": "Joseph Gordon-Levitt", "role": "Arthur"}],
    #         writer=["Christopher Nolan"],
    #         production=["Warner Bros."],
    #         director=["Christopher Nolan"]
    #     )

    def test_movie_str_returns_title(self):
        """
        Test that the __str__ method returns the movie's title.
        """
        movie=Movie.objects.get(id=1)
        # movie = Movie.objects.create(
        #     title="Inception",
        #     tmdb_id=27205
        # )
        result = str(movie)
        self.assertEqual(result, "Inception")

    def test_render_genre(self):
        # Suppose to pass
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_genre(), "Action - Sci-Fi")
        movie = Movie.objects.get(id=2)
        self.assertEqual(movie.render_genre(), "Action - Sci-Fi - Thriller")
        # Suppose to fail
        movie = Movie.objects.get(id=2)
        self.assertNotEqual(movie.render_genre(), "Horror - Sci-Fi")

    def test_render_casting(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")

        movie_2 = Movie.objects.get(id=2)
        self.assertNotEqual(movie_2.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")

    def test_render_writer(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_writer(), "Christopher Nolan")

    def test_render_production(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_production(), "Warner Bros.")

    def test_render_director(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_director(), "Christopher Nolan")
