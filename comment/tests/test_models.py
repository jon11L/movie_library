from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from comment.models import Comment
from user.models import User
from movie.models import Movie
from serie.models import Serie


class CommentModelTestCase(TestCase):


    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user01', password='testpass')
        cls.user.full_clean()
        cls.user.save()

        cls.user_2 = User.objects.create_user(username='user02', password='testpass')
        cls.user_2.full_clean()
        cls.user_2.save()

        cls.movie = Movie.objects.create(title='Test Movie')
        cls.movie.full_clean()
        cls.movie.save()

        cls.serie = Serie.objects.create(title='Test Serie')
        cls.serie.full_clean()
        cls.serie.save()

    def test_create_comment_on_movie(self):
        ''' Test creating a comment on a movie '''
        comment = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is a comment on a movie.'
        )
        comment.full_clean()
        comment.save()
        self.assertEqual(comment.kind, 'movie')
        self.assertEqual(comment.content_object, self.movie)

    def test_create_comment_on_serie(self):
        ''' Test creating a comment on a serie '''
        comment = Comment.objects.create(
            user=self.user,
            serie=self.serie,
            body='This is a comment on a movie.'
        )
        comment.full_clean()
        comment.save()
        self.assertEqual(comment.kind, 'serie')
        self.assertEqual(comment.content_object, self.serie)

    def test_create_second_comment_on_movie(self):
        ''' Test creating a comment on a movie '''
        comment = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is a comment on a movie.'
        )
        comment.full_clean()
        comment.save()

        comment_2 = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is the second comment.'
        )
        comment_2.full_clean()
        comment_2.save()

        self.assertEqual(comment.kind, 'movie')
        self.assertEqual(comment.content_object, self.movie)

        # check that the user posted 2 comments on the same movie
        self.assertEqual(self.user.comments.filter(movie=self.movie).count(), 2)

    def test_create_several_comments_on_different_content_types(self):
        ''' Test creating several comments on different content types '''
        comment_movie = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is a comment on a movie.'
        )
        comment_movie.full_clean()
        comment_movie.save()

        comment_2_movie = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is a comment on a movie.'
        )
        comment_2_movie.full_clean()
        comment_2_movie.save()

        comment_serie = Comment.objects.create(
            user=self.user,
            serie=self.serie,
            body='This is a comment on a serie.'
        )
        comment_serie.full_clean()
        comment_serie.save()

        self.assertEqual(comment_movie.kind, 'movie')
        self.assertEqual(comment_movie.content_object, self.movie)

        self.assertEqual(comment_serie.kind, 'serie')
        self.assertEqual(comment_serie.content_object, self.serie)


    # --- Test Constraints, validation that fails --------
    def test_create_comment_without_user_raises_error(self):
        ''' Test that creating a comment without a user raises an IntegrityError '''
        with self.assertRaises(IntegrityError):
            Comment.objects.create(
                movie=self.movie,
                body='This comment without a user should fail.'
            )

    def test_create_comment_with_both_movie_and_serie_raises_error(self):
        ''' Test that creating a comment with both a movie and serie raises an IntegrityError '''
        with self.assertRaises(IntegrityError):
            Comment.objects.create(
                user=self.user,
                movie=self.movie,
                serie=self.serie,
                body='This comment with a movie and a serie should fail.'
            )

    def test_create_comment_with_neither_movie_nor_serie_raises_error(self):
        ''' Test that creating a comment without a movie or serie raises an IntegrityError '''
        with self.assertRaises(IntegrityError):
            Comment.objects.create(
                user=self.user,
                body='This comment should without a serie or movie  should fail.'
            )
    
    def test_str_representation(self):
        comment = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            body='This is a comment on a movie.'
        )
        expected_str = (
            f"{self.user.username} commented on {comment.kind} ({self.movie}) "
            f"at {comment.created_at:%Y-%m-%d %H%M}:"
            f"'{comment.body[:50]}'..."
        )
        self.assertEqual(str(comment), expected_str)
