from rest_framework import serializers

from .models import WatchList
from movie.models import Movie
from serie.models import Serie

from movie.serializers import MovieListSerializer
from serie.serializers import SerieListSerializer


class WatchListSerializer(serializers.ModelSerializer):

    # Writable fields for POST operation
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True,
        required=False,
        allow_null=True,
    )
    serie_id = serializers.PrimaryKeyRelatedField(
        queryset=Serie.objects.all(),
        source="serie",
        write_only=True,
        required=False,
        allow_null=True,
    )

    # to display the Movie/serie instance within the Watchlist object's instance
    movie = MovieListSerializer(read_only=True)
    serie = SerieListSerializer(read_only=True)


    class Meta:
        model = WatchList
        fields = [
            'id',
            'user',
            'movie',
            'movie_id',
            'serie',
            'serie_id',
            'status',
            'personal_note',
        ]
        read_only_fields = ['user']


    def to_representation(self, instance):
        '''
        Remove Null data for Movie or Serie. As only one of is saved by instances\n
        So only the actual media saved in watchlist shows.
        '''
        data = super().to_representation(instance)

        if data['movie'] is None:
            data.pop('movie', None)
        if data['serie'] is None:
            data.pop('serie', None)

        return data


    def validate(self, data):
        '''Only 1 Movie or 1 serie to be saved at a time, one must remain Null'''
        if not data.get('movie') and not data.get('serie'):
            raise serializers.ValidationError("You must provide either a movie or a serie.")
        if data.get('movie') and data.get('serie'):
            raise serializers.ValidationError("You cannot provide both movie and serie, only one.")

        return data
