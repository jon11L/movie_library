import datetime
import traceback
import random

from import_data.api_clients.TMDB.fetch_data import get_api_data
from movie.models import Movie


def save_or_update_movie(tmdb_id: int):
    """
    - Fetches a single movie and retrive it's corresponding  datas from TMDB API\n
    - Then create or update the movie and records it in the database.
    """
    try:
        # search for the movie
        # movie_data = get_movie_data(tmdb_id)

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
            for member in movie_credit.get("cast", [])
        ]

        # Extract trailer from the combined response
        trailer_data = movie_data.get("videos", {}).get("results", [])

        for trailer in trailer_data:
            if trailer["type"] in ["Trailer", "Featurette", "Teaser"] and trailer['site'] == "YouTube":
                youtube_trailer.append(
                    {"website": trailer["site"], "key": trailer["key"]}
                )
        youtube_trailer = random.sample(
            youtube_trailer, min(len(youtube_trailer), 4)
            )  # Select up to 4 random trailers

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

        select_posters = [] # will append the images to it an keep the urls only
        select_banners = [] # will append the images to it an keep the urls only
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

        # ------ Will check if the movie fetched has enough data to be saved --------
        # store in a Dict to pass in the check_movie_validity function
        processed_data = {
            "production": production,
            "director": director,
            "writers": writers,
            "cast": cast,
            "release_date" : release_date,
            "spoken_languages" : spoken_languages,
            "poster_images": poster_images,
            "banner_images": banner_images,
            "youtube_trailer": youtube_trailer
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
                    "casting" : cast[:12],
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
                    "poster_images" : poster_images,
                    "banner_images" : banner_images,
                    "trailers" : youtube_trailer
                    }
                )

        print(f"movie: '{movie.title}' {'-- Created.' if created else '-- Updated.'}")
        return (movie, created)

    except Exception as e:
        # print(f"an error occurred while saving/updating movie: '{movie_data.get('id')}-{movie_data.get('title')}' ", str(e))
        print(f"an error occurred while saving/updating movie: '{tmdb_id}' ", str(e))
        return None, False


def check_movie_validity(movie_data, processed_data: dict):
    '''
    ### Check the amount of data concerning the new imported movie.
    The movie will not be imported/saved in DB if:
    - grade gets below MIN_REQUIRED_SCORE (32) then Movie considered broken / will not be imported in Database
    - too many fields are missing datas **8**
    - Or 2/3 of critical fields are missing (title / poster_image / release_date / director / casting) 
    - priorities (pts): low (1) - medium (2) -- hard (5)
    - assume a total start score of 50 When all datas are present.
    - remove points depending on their priorities.
    - 
    Total fields to check: **24**
    '''
    is_valid = True
    BASE_SCORE = 50 # if missing data, point are subtracted according to the priority set
    MAX_MISSING_DATA = 8

    today = datetime.date.today()
    release_date = processed_data.get("release_date")
    # if isinstance(release_date, str):
    #     try:
    #         release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d').date()
    #     except (ValueError, TypeError):
    #         release_date = None

    if release_date and release_date > today:
        print(f"Movie has a future release date: {release_date}. ")
        MIN_REQUIRED_SCORE = 31
    else:
        print(f"Movie already released or no release date found: {release_date}. ")
        MIN_REQUIRED_SCORE = 35

    # CRITICAL_FIELDS =  ("title", "poster_images", "casting", "description")
    # priorities:
    low = 1 # (11 fields), 
    medium = 2 # (7 fields), 
    high = 5 # (5)

    processed_data = processed_data

    all_datas = {
        # high priority
        "title": {
            "value": bool(movie_data.get("title") or bool(movie_data.get("original_title"))),
            "priority": high,
        },
        "director": {
            "value": len(processed_data.get("director", [])) > 0,
            "priority": high,
        },
        "casting": {"value": len(processed_data.get("cast", [])) > 0, "priority": high},
        "poster_images": {
            "value": len(processed_data.get("poster_images", [])) > 0,
            "priority": high,
        },
        "release_date": {
            "value": bool(processed_data.get("release_date")),
            "priority": high,
        },
        # medium priority
        "genre": {"value": len(movie_data.get("genres", [])) > 0, "priority": medium},
        "production": {
            "value": len(processed_data.get("production", [])) > 0,
            "priority": medium,
        },
        "banner_images": {
            "value": len(processed_data.get("banner_images", [])) > 0,
            "priority": medium,
        },
        "trailers": {
            "value": len(processed_data.get("youtube_trailer", [])) > 0,
            "priority": medium,
        },
        "writers": {
            "value": len(processed_data.get("writers", [])) > 0,
            "priority": medium,
        },
        "length": {
            "value": movie_data.get("runtime") is not None
            and movie_data.get("runtime") > 0,
            "priority": medium,
        },
        "description": {"value": bool(movie_data.get("overview")), "priority": medium},
        # low priority
        "imdb_id": {"value": bool(movie_data.get("imdb_id")), "priority": low},
        "original_title": {
            "value": bool(movie_data.get("original_title")),
            "priority": low,
        },
        "origin_country": {
            "value": len(movie_data.get("origin_country", [])) > 0,
            "priority": low,
        },
        "original_language": {
            "value": bool(movie_data.get("original_language")),
            "priority": low,
        },
        "vote_average": {
            "value": movie_data.get("vote_average") is not None,
            "priority": low,
        },
        "budget": {
            "value": movie_data.get("budget") is not None
            and movie_data.get("budget") > 0,
            "priority": low,
        },
        "revenue": {
            "value": movie_data.get("revenue") is not None
            and movie_data.get("revenue") > 0,
            "priority": low,
        },
        "tagline": {"value": bool(movie_data.get("tagline")), "priority": low},
        "spoken_languages": {
            "value": len(processed_data.get("spoken_languages", [])) > 0,
            "priority": low,
        },
        # "released": {"value": movie_data.get("status") == "Released", "priority": low},
        "vote_count": {
            "value": movie_data.get("vote_count") is not None
            and movie_data.get("vote_count") > 0,
            "priority": low,
        },
        "popularity": {
            "value": movie_data.get("popularity") is not None,
            "priority": low,
        },
    }

    # loop through processed fields, check how many fields are missing
    # and how much point taken out per priority
    missing_fields = [field for field, data in all_datas.items() if not data['value']]

    result = 0
    score = [data['priority'] for field, data in all_datas.items() if not data['value']]
    for s in score:
        result += s

    print(
        f"-- missing fields: {len(missing_fields)}, {missing_fields}.\n"
        f"-- missing score: {result} -- {score}"
    )

    if BASE_SCORE - result <= MIN_REQUIRED_SCORE:
        print(f" Too many missing fields! BREAK! No import. -- score: {BASE_SCORE - result}/{BASE_SCORE}")
        is_valid = False
    else:
        print(f"Considerable amount of data, Can be imported! score: {BASE_SCORE - result}/{BASE_SCORE}")

    return is_valid
