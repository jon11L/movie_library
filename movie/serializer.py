from rest_framework import serializers

from .models import Movie


# Serializer for the Movie model:
# serialize the movie model and sanitize the data, and create api endpoints so that other apps can use it
# This serializer will be used to convert the Movie model instances into JSON format and vice versa
# It will also handle validation and serialization of the data.
# This is a basic serializer that will includes most fields of the Movie model

# user or externals apps should be able to use this serializer to retrieve movies. by title and genre
#  limited to read-only access to regular user and POST/PUT/UPDATE for ADMIN/Superuser/staff


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            'id',
            'title',
            'description',
            'tagline',
            'release_date',
            'genre',
            'origin_country',
            'original_language',
            'director',
            'vote_average',
            'poster_images',
            'trailers',
        )        