import datetime
import traceback
import random

from import_data.api_clients.TMDB.fetch_data import get_api_data
from import_data.tools.check_media_validity import check_movie_validity
from movie.models import Movie


def save_or_update_movie(tmdb_id: int):
    """
    - Fetches a single movie and retrive it's corresponding  datas from TMDB API\n
    - Then create or update the movie and records it in the database.
    """
    try:
        # Fetch movie details from TMDB API
        movie_data = get_api_data(
            t_type = 'movie_detail',
            tmdb_id=tmdb_id
            )

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
        yt_trailer = []
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
            for member in movie_credit.get("cast", [])
        ]

        # Extract trailer from the combined response
        trailer_data = movie_data.get("videos", {}).get("results", [])

        second_trailer = [] # append optional "Featurette"
        for trailer in trailer_data:

            if trailer['site'] != "YouTube":
                continue

            if trailer["type"] in ["Trailer", "Teaser"]:
                yt_trailer.append(
                    {"website": trailer["site"], "key": trailer["key"]}
                )

            if trailer["type"] in ["Featurette"]:
                second_trailer.append(
                    {"website": trailer["site"], "key": trailer["key"]}
                )

        print(f"trailer count: {len(yt_trailer)}")
        if len(yt_trailer) <= 3:
            need = 6 - len(yt_trailer) # Set to keep 6 trailers max
            for i in second_trailer[:need]:
                yt_trailer.append(i)


        languages = movie_data.get("spoken_languages", [])
        spoken_languages = [language["english_name"] for language in languages]

        production = [company["name"] for company in movie_data.get("production_companies", [])] # List of production companies

        # Convert the release date to a datetime object if it exists
        release_date = None
        if movie_data.get('release_date'):
            try:
                release_date = datetime.datetime.strptime(movie_data.get('release_date'), '%Y-%m-%d').date()
            except ValueError:
                # If the release date is not available, it stays set to None
                print(f"Invalid date format: {movie_data.get('release_date')}")

        select_posters = [] # will append the images to it and keep the urls only
        select_banners = [] 
        # Fetch and store images
        images = movie_data["images"]

        # Fetch and store posters images
        posters = images.get("posters", [])
        if posters is not None:
            select_posters = [sel['file_path'] for sel in posters[:4]] 

        if movie_data.get('poster_path') and movie_data.get('poster_path') not in select_posters:
            # append the original poster // to 1st element
            select_posters.insert(0, movie_data.get('poster_path')) 
        elif movie_data.get('poster_path') and movie_data.get('poster_path') in select_posters:
            # remove the 'main' poster path, to append it to the beginning
            try:
                select_posters.remove(movie_data.get('poster_path'))
            except ValueError as e:
                print(f"Value error: {e}\n")
                print(f"Could not remove the poster path to append to first index.")
            select_posters.insert(0, movie_data.get('poster_path'))

        poster_images = select_posters # set to save in the object

        # Fetch and store Banner images
        banners = images.get("backdrops", [])
        if banners is not None:
            select_banners = [sel['file_path'] for sel in banners[:4]] 

        if movie_data.get('backdrop_path')  and movie_data.get('backdrop_path') not in select_banners :
            # append the original banner // to 1st element
            select_banners.insert(0, movie_data.get('backdrop_path')) 
        elif movie_data.get('backdrop_path') and movie_data.get('backdrop_path') in select_banners:
            # remove the 'main' banner path, to append it to the beginning
            try:
                select_banners.remove(movie_data.get('backdrop_path'))
            except ValueError as e:
                print(f"Value error: {e}\n")
                print(f"Could not remove the poster path to append to first index.")
            select_banners.insert(0, movie_data.get('backdrop_path'))

        banner_images = select_banners # set to save in the object

        genre = [genre["name"] for genre in movie_data.get("genres", [])]

        # ------ Will check if the movie fetched has enough data to be saved --------
        # store in a Dict to pass in the check_movie_validity function
        processed_data = {
            "production": production,
            "director": director,
            "writers": writers,
            "cast": cast,
            "genre": genre,
            "release_date" : release_date,
            "spoken_languages" : spoken_languages,
            "poster_images": poster_images,
            "banner_images": banner_images,
            "youtube_trailer": yt_trailer
        }

        is_valid = check_movie_validity(movie_data, processed_data)

        if is_valid:
            print(f"movie: {movie_data.get("title")} passes validity data-check. Saving the movie")
        else:
            # did not pass the validity check, does not save, stop here.
            print(f"movie: '{movie_data.get("title")}' did not pass the validity data-check. NOT saving the movie")
            return None, False

        # Store the new movie in DB
        movie, created = Movie.objects.update_or_create(
            tmdb_id=movie_data.get('id'), # check if the movie is already existing in the database
                defaults={
                    # External unique identifier
                    'imdb_id' : movie_data.get("imdb_id") if movie_data.get("imdb_id") != "" else None,
                    # Core Movie Details
                    "original_title" : movie_data.get("original_title"),
                    "title" : movie_data.get("title") or movie_data.get("original_title"),  # Use original_title if title is missing
                    "release_date" : release_date,
                    "origin_country" : movie_data.get("origin_country"),
                    "original_language" : movie_data.get("original_language"),
                    "production" : production, # List of production companies
                    "director" : director,
                    "writer" : writers,
                    "casting" : cast[:12],
                    "length" : movie_data.get("runtime"),
                    "status": movie_data.get('status'),

                    "vote_average" : movie_data.get("vote_average"),
                    "overview" : movie_data.get("overview"),
                    "genre" : genre,
                    "budget" : movie_data.get("budget"),
                    "revenue" : movie_data.get("revenue"),
                    "tagline" : movie_data.get("tagline"),
                    "spoken_languages" : spoken_languages,
                    # Metrics
                    "vote_count" : movie_data.get("vote_count"),
                    "popularity" : movie_data.get("popularity"),
                    # images & trailer
                    "poster_images" : poster_images,
                    "banner_images" : banner_images,
                    "trailers" : yt_trailer
                    }
                )

        print(f"movie: '{movie.title}' {'-- Created.' if created else '-- Updated.'}")
        return (movie, created)

    except Exception as e:
        # print(f"an error occurred while saving/updating movie: '{movie_data.get('id')}-{movie_data.get('title')}' ", str(e))
        print(f"an error occurred while saving/updating movie: '{tmdb_id}' ", str(e))
        return None, False
