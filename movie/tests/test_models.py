from django.test import TestCase
from movie.models import Movie
# import unittest
import datetime

class MovieModelSaveTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
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
            vote_count=12000,
            popularity=45.0,
            poster_images=["poster1.jpg", "poster2.jpg"],
            banner_images=["banner1.jpg", "banner2.jpg"],
            trailers=[{"key": "8hP9D6kZseM", "website": "youtube"}],
        )


    def test_fields_saved_correctly(self):
        """Test that all fields are saved and retrieved correctly."""
        movie = self.movie  # Using the movie created in setUpTestData
        self.assertEqual(movie.tagline, "Mischief. Mayhem. Soap.")
        self.assertEqual(movie.director, ["David Fincher"])
        self.assertEqual(movie.writer, ["Chuck Palahniuk", "Jim Uhls"])
        self.assertEqual(movie.production, ["20th Century Fox"])
        self.assertEqual(movie.origin_country, ["US"])
        self.assertEqual(movie.original_language, "en")
        self.assertEqual(movie.spoken_languages, ["en", "de"])
        self.assertEqual(movie.status, "Released")
        self.assertEqual(movie.budget, 63000000)
        self.assertEqual(movie.revenue, 100853753)
        self.assertEqual(movie.vote_average, 8.4)
        self.assertEqual(movie.vote_count, 12000)
        self.assertEqual(movie.popularity, 45.0)
        self.assertEqual(movie.poster_images, ["poster1.jpg", "poster2.jpg"])
        self.assertEqual(movie.banner_images, ["banner1.jpg", "banner2.jpg"])

    def test_movie_str_method(self):
        """Test the __str__ method of the Movie model."""
        self.assertEqual(str(self.movie), "Fight Club")
    
    def test_title_correct(self):
        """Test that the title field is saved correctly."""
        self.assertNotEqual(self.movie.title, "Inception")
        self.assertEqual(self.movie.title, "Fight Club")
        self.assertEqual(type(self.movie.title), str)

    def test_description_field(self):
        """Test that the description field is saved correctly."""
        movie = self.movie
        self.assertIsNotNone(self.movie.description)
        self.assertEqual(type(movie.description), str)
        if self.movie.description:
            self.assertIn("insomniac and a slippery soap", self.movie.description)

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


    def test_movie_creation_missing_required_fields(self):
        """Test creating a movie without required fields raises an error."""
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Movie.objects.create(
                tmdb_id=54321
            )


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
        Movie.objects.create(
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
            vote_average=8.8,
            spoken_languages=["en", "fr"],
        )

        Movie.objects.create(
            title="the dark knight",
            genre=["Action", "Sci-Fi", "Thriller"],
            casting=[{"name": "Christian Bale", "role": "Bruce Wayne"}, {"name": "Heath Ledger", "role": "Joker"}],
            writer=["Christopher Nolan"],
            production=["Warner Bros."],
            director=["Christopher Nolan"]

        )

        print("         --SetupTestData for MovieModelMethodTest completed.\n")
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
        '''
        Test the render_genre method for correct formatting.
        '''
        # check movie 1
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_genre(), "Action - Sci-Fi")
        # check movie 2
        movie = Movie.objects.get(id=2)
        self.assertEqual(movie.render_genre(), "Action - Sci-Fi - Thriller")
        movie = Movie.objects.get(id=2)
        self.assertNotEqual(movie.render_genre(), "Horror - Sci-Fi")


    def test_render_length(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_length(), "2h28")

        movie_2 = Movie.objects.get(id=2)
        self.assertEqual(movie_2.render_length(), "N/a")

    def test_render_casting(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")

        movie_2 = Movie.objects.get(id=2)
        self.assertEqual(type(movie_2.render_casting()), str)
        self.assertNotEqual(movie_2.render_casting(), "Leonardo DiCaprio as Cobb || Joseph Gordon-Levitt as Arthur")
        self.assertEqual(movie_2.render_casting(), "Christian Bale as Bruce Wayne || Heath Ledger as Joker")

    def test_render_writer(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_writer(), "Christopher Nolan")

    def test_render_production(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_production(), "Warner Bros.")

    def test_render_director(self):
        movie = Movie.objects.get(id=1)
        self.assertEqual(movie.render_director(), "Christopher Nolan")

    # def test_render_trailers(self):
    #     movie = Movie.objects.get(id=1)
    #     # self.assertEqual(type(movie.render_trailer), str)
    #     # self.assertIn("youtube", movie.render_trailer)
    #     # self.assertIn("8hP9D6kZseM", movie.render_trailer())
    #     self.assertEqual(movie.render_trailer(), "https://www.youtube.com/watch?v=8hP9D6kZseM")

