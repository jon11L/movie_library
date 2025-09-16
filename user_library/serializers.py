from rest_framework import serializers

from .models import WatchList

from movie.serializers import MovieListSerializer, MovieDetailSerializer
from serie.serializers import SerieListSerializer, SerieDetailSerializer



# Serializer for the Movie model:
# serialize the movie model and sanitize the data, and create api endpoints so that other apps can use it
# This serializer will be used to convert the Movie model instances into JSON format and vice versa
# It will also handle validation and serialization of the data.
# This is a basic serializer that will includes most fields of the Movie model

# user or externals apps should be able to use this serializer to retrieve movies. by title and genre
#  limited to read-only access to regular user and POST/PUT/UPDATE for ADMIN/Superuser/staff

class WatchListSerializer(serializers.ModelSerializer):

    movie = MovieListSerializer(read_only=True)
    serie = SerieListSerializer(read_only=True)

    class Meta:
        model = WatchList
        fields = [
            'id',
            'user',
            'movie',
            'serie',
            'status',
            'personal_note',
        ]

    def to_representation(self, instance):
        '''
        Clean out Null data for Movie or Serie. As only one of is saved by instances
        '''
        data = super().to_representation(instance)

        if data['movie'] is None:
            data.pop('movie', None)
        if data['serie'] is None:
            data.pop('serie', None)
            
        return data
    

    
# class WatchListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WatchList
#         fields = (
#             'id',
#             'user',
#             'movie',
#             'serie',
#             'status',
#             'personal_note',
#         )        
