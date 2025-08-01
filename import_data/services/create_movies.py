from datetime import datetime
import traceback

from import_data.api_clients.TMDB.fetch_movies import get_movie_data
from movie.models import Movie


def save_or_update_movie(tmdb_id: int):
    """
    Fetches a single movie and it'S content datas from TMDB API 
    Check if the movie already exists otherwise saves it in the database.
    """
    try:
        # search for the movie
        movie_data = get_movie_data(tmdb_id)

        # check if te API was called correctly and returned the datas
        if not movie_data:
            print(f"Failed to fetch movie data from TMDB api with ID: {tmdb_id}")
            return  None, False
        else:
            print(f"Movie found with TMDB ID: {tmdb_id}")
        
        # initialize empty list, for future jsonfield reference ... 
        director = []
        writers = []
        cast = []
        youtube_trailer = []
        spoken_languages = []

        # Extract credits from the combined response
        movie_credit = movie_data.get('credits', {})

        if movie_credit:
            for person in movie_credit.get("crew", []):
                # append the directors for the  director field
                if person["job"] == "Director":
                    director.append(person["name"])
                # append the writers for the Writer field
                if person["job"] in ["Writer", "Screenplay"]:
                    writers.append(person["name"])

        # Top 10 cast members (takes the name and role)
        cast = [
            {"name": member["name"], "role": member["character"]}
            for member in movie_credit.get("cast", [])[:10]
        ]

        # Extract trailer from the combined response
        trailer_data = movie_data.get("videos", {}).get("results", [])

        for trailer in trailer_data[:4]:
            if trailer["type"] in ["Trailer", "Featurette", "Teaser"] and trailer['site'] == "YouTube":
                youtube_trailer.append(
                    {"website": trailer["site"], "key": trailer["key"]}
                )

        languages = movie_data.get("spoken_languages", [])
        spoken_languages = [language["english_name"] for language in languages]

        production = [company["name"] for company in movie_data.get("production_companies", [])] # List of production companies

        # Convert the release date to a datetime object if it exists
        release_date = None
        if movie_data.get('release_date'):
            try:
                release_date = datetime.strptime(movie_data.get('release_date'), '%Y-%m-%d').date()
            except ValueError:
                # If the release date is not available, it stays set to None
                print(f"Invalid date format: {movie_data.get('release_date')}")

        # Store the new movie in DB
        movie, created = Movie.objects.update_or_create(
            tmdb_id=movie_data.get('id'), # check if the movie is already existing in the database
                defaults={
                    # External unique identifier
                    'imdb_id' : movie_data.get("imdb_id"),
                    # Core Movie Details
                    "original_title" : movie_data.get("original_title"),
                    "title" : movie_data.get("title") or movie_data.get("original_title"),  # Use original_title if title is missing
                    "release_date" : release_date,
                    "origin_country" : movie_data.get("origin_country"),
                    "original_language" : movie_data.get("original_language"),
                    "production" : production, # List of production companies
                    "director" : director,
                    "writer" : writers,
                    "casting" : cast,
                    "length" : movie_data.get("runtime"),
                    "vote_average" : movie_data.get("vote_average"),
                    "description" : movie_data.get("overview"),
                    "genre" : [genre["name"] for genre in movie_data.get("genres", [])],
                    "budget" : movie_data.get("budget"),
                    "revenue" : movie_data.get("revenue"),
                    "tagline" : movie_data.get("tagline"),
                    "spoken_languages" : spoken_languages,
                    # Metrics
                    "released" : True if movie_data.get("status") == "Released" else False,
                    "vote_count" : movie_data.get("vote_count"),
                    "popularity" : movie_data.get("popularity"),
                    # images & trailer
                    "image_poster" : movie_data.get('poster_path') if movie_data.get("poster_path") else None,
                    "banner_poster" : movie_data.get('backdrop_path') if movie_data.get("backdrop_path") else None,
                    "trailers" : youtube_trailer
                    }
                )

        print(f"movie: '{movie.title}' {'-- Created.' if created else '-- Updated.'}")
        print("---------")
        return (movie, created)

    except Exception as e:
        print(f"an error occurred while saving/updating movie: '{movie_data.get('id')}-{movie_data.get('title')}' ", str(e))
        return None, False
