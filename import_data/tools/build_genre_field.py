from django.utils.text import slugify

from media_library.models import Genre

GENRE_NAME_MAP = {
    "Sci-Fi & Fantasy":   ["Science Fiction", "Fantasy"],
    "Action & Adventure": ["Action", "Adventure"],
    "Sci-Fi":             ["Science Fiction"],
    "War & Politics":     ["War", "Politics"],
}

def sync_genres(media, raw_genres):
    """
    Finds or creates Genre instance from the raw_genres, then sets them on the media object.
    """
    genre_objects = []
    for item in raw_genres:
        raw_name = item["name"].strip()
        # Normalize name if needed
        genre_names = GENRE_NAME_MAP.get(raw_name, [raw_name])

        for name in genre_names:
            genre, created = Genre.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)}
            )
            if created:
                print(f"  [Genre] New genre created: '{name}'")
            genre_objects.append(genre)

    media.genres.set(genre_objects)
