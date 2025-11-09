from django.test import TestCase
from django.templatetags.static import static

import datetime

from movie.models import Movie


class MovieModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.movie = Movie.objects.create(
            tmdb_id=550,
            imdb_id="tt0137523",
            original_title="Fight Club",
            title="Fight Club",
            overview="A ticking-time-bomb insomniac and a slippery soap salesman channel primal..",
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
            vote_count=12000,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
            trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}],
        )

    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        movie = self.movie  # Using the movie created in setUpTestData
        self.assertEqual(movie.director, ["David Fincher"])
        self.assertEqual(movie.writer, ["Chuck Palahniuk", "Jim Uhls"])
        self.assertEqual(movie.origin_country, ["US"])
        self.assertEqual(movie.budget, 63000000)
        self.assertEqual(movie.revenue, 100853753)
        self.assertEqual(movie.vote_count, 12000)
        self.assertEqual(movie.popularity, 45.0)
        self.assertEqual(movie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(movie.banner_images, ["banner1.jpg", "banner2.jpg"])

    def test_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.movie.title, "Inception")
        self.assertEqual(self.movie.title, "Fight Club")
        self.assertEqual(type(self.movie.title), str)

    def test_tagline_field(self):
        """Test that the tagline field is saved correctly."""
        movie = self.movie
        self.assertEqual(type(movie.tagline), str)
        self.assertEqual(movie.tagline, "Mischief. Mayhem. Soap.")

    def test_overview_field(self):
        """Test that the description field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(self.movie.overview)
        self.assertEqual(type(movie.overview), str)
        if self.movie.overview:
            self.assertIn("insomniac and a slippery soap", self.movie.overview)

    def test_movie_genre_field(self):
        """Test that the genre field can store a list of strings."""
        self.assertIsInstance(self.movie.genre, list)
        self.assertIsNotNone(self.movie.genre)
        self.assertEqual(self.movie.genre, ["Drama", "Thriller"])
        if self.movie.genre:
            self.assertIn("Drama", self.movie.genre)
            self.assertIn("Thriller", self.movie.genre)
            self.assertEqual(len(self.movie.genre), 2)

    def test_movie_released_field(self):   
        """Test that a movie can be marked as released."""
        self.assertEqual(type(self.movie.released), bool)
        self.assertTrue(self.movie.released)

    def test_serie_status_field(self):   
        """Test that a movie can be marked as released."""
        # movie = Movie.objects.get(pk=1)
        self.assertEqual(type(self.movie.status), str)
        # self.assertTrue(self.serie.status)
        self.assertIsNotNone(self.movie.status)
        self.assertTrue(self.movie.status == "Released")

    def test_movie_length_field(self):
        """Test that the length field is saved correctly."""
        self.assertIsNotNone(self.movie.length)
        self.assertEqual(type(self.movie.length), int)
        self.assertEqual(self.movie.length, 139)

    def test_movie_release_date_field(self):
        """Test that the release_date field is saved correctly."""
        self.assertIsNotNone(self.movie.release_date)
        self.assertEqual(type(self.movie.release_date), datetime.date)
        self.assertEqual(self.movie.release_date, datetime.date(1999, 10, 15))

    def test_casting_field(self):
        """Test that the casting field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(movie.casting)
        self.assertEqual(type(movie.casting), list)
        if movie.casting:
            self.assertEqual(len(movie.casting), 4)
            self.assertEqual(type(movie.casting[0]), dict)
            self.assertEqual(movie.casting[0]['name'], "Brad Pitt")
            self.assertEqual(movie.casting[0]['role'], "Tyler Durden")
            self.assertEqual(movie.casting[2]['name'], "Helena Bonham Carter")
            self.assertEqual(movie.casting[2]['role'], "Marla Singer")

    def test_serie_production_field(self):
        """Test that the production field can store a list of strings."""
        movie = self.movie
        self.assertIsInstance(movie.production, list)
        self.assertIsNotNone(movie.production)
        if movie.production:
            self.assertEqual(len(movie.production), 1)
            self.assertIn("20th Century Fox", movie.production)

    def test_serie_original_language_field(self):
        """Test that the original_language field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(movie.original_language)
        self.assertEqual(type(movie.original_language), str)
        if movie.original_language:
            self.assertEqual(movie.original_language, "en")
            self.assertIn("en", movie.original_language)
    
    def test_serie_spoken_languages_field(self):
        """Test that the spoken_languages field can store a list of strings."""
        movie = self.movie
        self.assertIsNotNone(movie.spoken_languages)
        self.assertIsInstance(movie.spoken_languages, list)
        if movie.spoken_languages:
            self.assertIn("en", movie.spoken_languages)
            self.assertIn("de", movie.spoken_languages)
            self.assertEqual(len(movie.spoken_languages), 2)

    def test_vote_average_field(self):
        """Test that the vote_average field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(movie.vote_average)
        self.assertEqual(type(movie.vote_average), float)
        self.assertEqual(movie.vote_average, 8.4)

    # may go with Core app (but here tied to Movie model at the moment)
    def test_slug_generated_on_save(self):
        """Test that a slug is generated upon saving the movie."""
        self.assertIsNotNone(self.movie.slug)
        self.assertEqual(type(self.movie.slug), str)
        if self.movie.slug:
            self.assertIn("fight-club", self.movie.slug)
            self.assertRegex(self.movie.slug, r'fight-club-[0-9]*-\w*\d')

    def test_movie_create_required_fields_only(self):
        """Test creating a movie with only the title (required field)."""
        movie = Movie.objects.create(
            title="Inception",
            tmdb_id=27205
            )
        self.assertEqual(movie.title, "Inception")
        self.assertIsNotNone(movie.pk)  # Has a database ID

    def test_movie_tmdb_id_unique_constraint(self):
        """
        Test that tmdb_id must be unique.\n
        Fail on attempting to create a new movie with an already existing tmdb_id.
        """
        Movie.objects.create(title="Movie 1", tmdb_id=12345)
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Movie.objects.create(title="Movie 2", tmdb_id=12345)

    def test_movie_trailers_field(self):
        """Test that the trailers field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(movie.trailers)
        self.assertEqual(type(movie.trailers), list)
        if movie.trailers:
            self.assertEqual(len(movie.trailers), 1)
            self.assertEqual(type(movie.trailers[0]), dict)
            self.assertEqual(movie.trailers[0]['key'], "8hP9D6kZseM")
            self.assertEqual(movie.trailers[0]['website'], "youtube")


class MovieModelMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.movie_1 = Movie.objects.create(
            title="Inception",
            genre=["Action", "Sci-Fi"],
            casting=[{"name": "Leonardo DiCaprio", "role": "Cobb"}, {"name": "Joseph Gordon-Levitt", "role": "Arthur"}],
            writer=["Christopher Nolan"],
            production=["Warner Bros."],
            director=["Christopher Nolan"],
            length=148,
            trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}],
            released=True,
            origin_country=["US"],
            vote_average=8.812,
            spoken_languages=["en", "fr"],
        )

        cls.movie_2 = Movie.objects.create(
            title="the dark knight",
            genre=["Action", "Sci-Fi", "Thriller"],
            casting=[{"name": "Christian Bale", "role": "Bruce Wayne"}, {"name": "Heath Ledger", "role": "Joker"}],
            writer=["Christopher Nolan"],
            production=["Warner Bros."],
            director=["Christopher Nolan"]

        )

        cls.movie_3 = Movie.objects.create(
            original_title="Fight Club",
            title="Fight Club",
            overview="A ticking-time-bomb insomniac and a slippery soap salesman channel primal..",
            tagline="Mischief. Mayhem. Soap.",
            genre=["Drama", "Thriller"],
            release_date=datetime.datetime.strptime("1999-10-15", '%Y-%m-%d').date(),
            length=139,
            released=True,
            director=["David Fincher"],
            writer=["Chuck Palahniuk", "Jim Uhls"],
            production=["20th Century Fox"],
            casting=[
                {"name": "Brad Pitt", "role": "Tyler Durden"},
                {"name": "Edward Norton", "role": "The Narrator"},
                {"name": "Helena Bonham Carter", "role": "Marla Singer"},
                {"name": "Meat Loaf", "role": "Robert 'Bob' Paulson"}
                ],
            origin_country=["US"],
            original_language="en",
            spoken_languages=["en", "de"],
            status="Released",
            budget=63000000,
            revenue=100853753,
            vote_average=8.4,
            vote_count=1700000,
            imdb_rating=8.8,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
            trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}]
        )

        print("         --SetupTestData for MovieModelMethodTest completed.\n")

    # def setUp(self):
    #     Movie.objects.create(
    #         title="Inception",
    #         genre=["Action", "Sci-Fi"],
    #         casting=[{"name": "Leonardo DiCaprio", "role": "Cobb"}, {"name": "Joseph Gordon-Levitt", "role": "Arthur"}],
    #         writer=["Christopher Nolan"],
    #         production=["Warner Bros."],
    #         director=["Christopher Nolan"]
    #     )

    def test_movie_str_method_returns_title(self):
        """Test that the __str__ method returns the movie's title."""
        self.assertEqual(str(self.movie_1), "Inception")
        self.assertEqual(str(self.movie_2), "the dark knight")

    def test_render_genre(self):
        '''
        Test the render_genre method for correct formatting.
        '''
        # check movie 1
        self.assertEqual(self.movie_1.render_genre(), "Action - Sci-Fi")
        # check movie 2
        self.assertNotEqual(self.movie_2.render_genre(), "Horror - Sci-Fi")
        self.assertEqual(self.movie_2.render_genre(), "Action - Sci-Fi - Thriller")

    def test_render_length(self):
        self.assertEqual(self.movie_1.render_length(), "2h28")
        self.assertEqual(self.movie_2.render_length(), "N/a")

    def test_render_writer(self):
        self.assertNotEqual(self.movie_1.render_writer(), "Robbert eggers")
        self.assertEqual(self.movie_1.render_writer(), "Christopher Nolan")

    def test_render_production(self):
        self.assertEqual(type(self.movie_1.render_production()), str)
        self.assertNotEqual(self.movie_1.render_production(), "20th Century Fox")
        self.assertEqual(self.movie_1.render_production(), "Warner Bros.")

    def test_render_director(self):
        self.assertEqual(type(self.movie_1.render_director()), str)
        self.assertNotEqual(self.movie_1.render_director(), "")
        self.assertNotEqual(self.movie_1.render_director(), "Steven Spielberg")
        self.assertEqual(self.movie_1.render_director(), "Christopher Nolan")

    def test_render_vote_average(self):
        self.assertNotEqual(self.movie_3.render_vote_average(), 6)
        self.assertEqual(self.movie_3.render_vote_average(), 8.4)
        self.assertEqual(self.movie_1.render_vote_average(), 8.8)

    def test_render_banner_images(self):
        ''' 
        test the render_banner method.
        Should return full url: preffix + random image name from the field's list
        '''
        self.assertNotEqual(self.movie_3.render_banner(), "banner1.jpg")
        # self.assertEqual(serie.render_banner(), "https://image.tmdb.org/t/p/w1280banner1.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w1280", self.movie_3.render_banner())
        self.assertNotEqual(self.movie_3.render_banner(), "banner2.jpg")
        # no banner image set in movie_2
        self.assertEqual(self.movie_2.render_banner(), static("images/default_banner_photo.jpg"))

    def test_render_poster_images(self):
        ''' 
        test the render_poster method.
        Should return full url: preffix + random image name from the field's list
        '''
        self.assertNotEqual(self.movie_3.render_poster(), "poster1.jpg")
        self.assertNotEqual(self.movie_3.render_poster(), "poster2.jpg")
        self.assertIn("https://image.tmdb.org/t/p/w500", self.movie_3.render_poster())
        self.assertEqual(
            self.movie_3.render_poster(), "https://image.tmdb.org/t/p/w500poster1.jpg"
        )
        # no poster image set in movie_2
        self.assertEqual(self.movie_2.render_poster(), static("images/default_poster_photo.jpg"))

