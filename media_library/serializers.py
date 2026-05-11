from rest_framework import serializers

from .models import Media


# Serializer for the Movie model:
# serialize the movie model and sanitize the data, and create api endpoints so that other apps can use it
# This serializer will be used to convert the Movie model instances into JSON format and vice versa
# It will also handle validation and serialization of the data.
# This is a basic serializer that will includes most fields of the Movie model

# user or externals apps should be able to use this serializer to retrieve movies. by title and genre
#  limited to read-only access to regular user and POST/PUT/UPDATE for ADMIN/Superuser/staff


# create a filter for serializing in Media between movie and serie.

class MediaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            'id',
            'title',
            'release_date',
            'genre',
            'origin_country',
            'original_language',
            'vote_average',
        ]      


class MediaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            'id',
            'title',
            'overview',
            'tagline',
            'release_date',
            'genre',
            'origin_country',
            'original_language',
            # 'casting', # belongs in Movie
            # 'director', 
            'vote_average',
            'poster_images',
            # 'trailers',
        ]       