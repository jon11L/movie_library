from rest_framework import serializers

from .models import Serie


class SerieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = [
            'id',
            'title',
            'first_air_date',
            'status',
            'genre',
            'origin_country',
            'original_language',
            'vote_average',
        ]     


class SerieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = [
            'id',
            'title',
            'description',
            'tagline',
            'first_air_date',
            'last_air_date',
            'status',
            'genre',
            'origin_country',
            'original_language',
            'production',
            'created_by',
            'vote_average',
            'poster_images',
        ]        