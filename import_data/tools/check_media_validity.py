import datetime
import traceback

from movie.models import Movie
from serie.models import Serie

def check_movie_validity(movie_data, processed_data: dict):
    '''
    ### Check the amount of data concerning the new imported movie.
    The movie will not be imported/saved in DB if:
    - grade gets below **MIN_REQUIRED_SCORE** then Movie considered broken / will not be imported in Database
    - priorities (pts): low (1) - medium (2) -- hard (4.5)
    - assume a total start score of 50 When all datas are present.
    - remove points depending on their priorities.
    
    Total fields to check: **24**
    '''
    is_valid = True
    BASE_SCORE = 50 # if missing data, point are subtracted according to the priority set
    # priorities:
    LOW = 1 # (11 fields), 
    MEDIUM = 2 # (8 fields), 
    HIGH = 4.5 # (5)

    today = datetime.date.today()
    processed_data = processed_data
    release_date = processed_data.get("release_date")

    if release_date and release_date > today:
        print(f"Movie has a future release date: {release_date}. ")
        MIN_REQUIRED_SCORE = 30
    else:
        print(f"Movie already released or no release date found: {release_date}. ")
        MIN_REQUIRED_SCORE = 33

    all_datas = {
        # high priority
        "title": {
            "value": bool(
                movie_data.get("title") or bool(movie_data.get("original_title"))
            ),
            "priority": HIGH,
        },
        "director": {
            "value": len(processed_data.get("director", [])) > 0,
            "priority": HIGH,
        },
        "casting": {"value": len(processed_data.get("cast", [])) > 0, "priority": HIGH},
        "poster_images": {
            "value": len(processed_data.get("poster_images", [])) > 0,
            "priority": HIGH,
        },
        "release_date": {
            "value": bool(processed_data.get("release_date")),
            "priority": HIGH,
        },
        # medium priority
        "genre": {
            "value": len(processed_data.get("genre", [])) > 0,
            "priority": MEDIUM,
        },
        "production": {
            "value": len(processed_data.get("production", [])) > 0,
            "priority": MEDIUM,
        },
        "banner_images": {
            "value": len(processed_data.get("banner_images", [])) > 0,
            "priority": MEDIUM,
        },
        "trailers": {
            "value": len(processed_data.get("youtube_trailer", [])) > 0,
            "priority": MEDIUM,
        },
        "writers": {
            "value": len(processed_data.get("writers", [])) > 0,
            "priority": MEDIUM,
        },
        "length": {
            "value": movie_data.get("runtime") is not None
            and movie_data.get("runtime") > 0,
            "priority": MEDIUM,
        },
        "overview": {"value": bool(movie_data.get("overview")), "priority": MEDIUM},
        "imdb_id": {"value": bool(movie_data.get("imdb_id")), "priority": MEDIUM},
        # low priority
        "original_title": {
            "value": bool(movie_data.get("original_title")),
            "priority": LOW,
        },
        "origin_country": {
            "value": len(movie_data.get("origin_country", [])) > 0,
            "priority": LOW,
        },
        "original_language": {
            "value": bool(movie_data.get("original_language")) or len(movie_data.get("origin_language", [])) > 0,
            "priority": LOW,
        },
        "vote_average": {
            "value": movie_data.get("vote_average") is not None
            and (
                type(movie_data.get("vote_average")) == int
                if release_date and release_date > today
                else movie_data.get("vote_average") > 0
            ),
            "priority": LOW,
        },
        "budget": {
            "value": movie_data.get("budget") is not None
            and (
                type(movie_data.get("budget")) == int
                if release_date and release_date > today
                else movie_data.get("budget") > 0
            ),
            "priority": LOW,
        },
        "revenue": {
            "value": movie_data.get("revenue") is not None
            and (
                type(movie_data.get("revenue")) == int
                if release_date and release_date > today
                else movie_data.get("revenue") > 0
            ),
            "priority": LOW,
        },
        "status": {"value": bool(movie_data.get("status")), "priority": LOW},
        "tagline": {"value": bool(movie_data.get("tagline")), "priority": LOW},
        "spoken_languages": {
            "value": len(processed_data.get("spoken_languages", [])) > 0,
            "priority": LOW,
        },
        # "released": {"value": movie_data.get("status") == "Released", "priority": low},
        "vote_count": {
            "value": movie_data.get("vote_count") is not None
            and (
                type(movie_data.get("vote_count")) == int
                if release_date and release_date > today
                else movie_data.get("vote_count") > 0
            ),
            "priority": LOW,
        },
        "popularity": {
            "value": movie_data.get("popularity") is not None
            and (
                type(movie_data.get("popularity")) == float
                if release_date and release_date > today
                else movie_data.get("popularity") > 0
            ),
            "priority": LOW,
        },
    }

    # pass the datas in function to return the score result of the serie 
    result, missing_fields = check_score_media(all_datas)

    if BASE_SCORE - result <= MIN_REQUIRED_SCORE:
        print(f"No import. Too many missing fields! -- score: {BASE_SCORE - result}/{BASE_SCORE}")
        is_valid = False

        #  help remove movies with insufficient data already saved in DB
        if Movie.objects.filter(tmdb_id=movie_data.get('id')).exists():
            print(f" -- More than half of the fields are missing! ({len(missing_fields)}/24) --")
            print(f"Deleting the movie from DB if existing...")
            try:
                Movie.objects.filter(tmdb_id=movie_data.get('id')).delete()
                print(f"Movie with TMDB ID: {movie_data.get('id')} deleted from DB.")
            except Exception as e:
                print(f"An error occurred while deleting movie with TMDB ID: {movie_data.get('id')}. Error: {str(e)}")
                traceback.print_exc()

    else:
        print(f"Considerable amount of data, Can be imported! score: {BASE_SCORE - result}/{BASE_SCORE}")

    return is_valid


def check_serie_validity(serie_data, processed_data: dict):
    '''
    ### Check the amount of data concerning the new imported serie.
    The serie will not be imported/saved in DB if:
    - grade gets below MIN_REQUIRED_SCORE then the serie is considered broken
    - priorities (pts): low (1.5) - medium (3) -- hard (4.5)
    - assume a total start score of 50 When all datas are present.
    - remove points depending on their priorities.

    Total fields to check: **20**
    '''
    BASE_SCORE = 50 # if missing data, point are subtracted according to the priority set
    # priorities:
    LOW = 1.5 # (11 fields), 
    MEDIUM = 3 # (5 fields), 
    HIGH = 4.5 # (4)

    is_valid = True
    today = datetime.date.today()
    processed_data = processed_data
    first_air_date = processed_data.get("first_air_date")

    if first_air_date and first_air_date > today:
        print(f"Serie has a future release date: {first_air_date}.")
        MIN_REQUIRED_SCORE = 31
    else:
        print(f"Serie already released or no release date found: {first_air_date}.")
        MIN_REQUIRED_SCORE = 35

    all_datas = {
        # high priority
        "title": {
            "value": bool(serie_data.get("name") or bool(serie_data.get("original_name"))),
            "priority": HIGH,
        },
        "poster_images": {
            "value": len(processed_data.get("poster_images", [])) > 0,
            "priority": HIGH,
        },
        "first_air_date": {
            "value": bool(processed_data.get("first_air_date")),
            "priority": HIGH,
        },
        "production": {
            "value": len(processed_data.get("production", [])) > 0,
            "priority": HIGH,
        },
        # medium priority
        "genre": {"value": len(processed_data.get("genre", [])) > 0, "priority": MEDIUM},
        "banner_images": {
            "value": len(processed_data.get("banner_images", [])) > 0,
            "priority": MEDIUM,
        },
        "created_by": {
            "value": len(processed_data.get("created_by", [])) > 0,
            "priority": MEDIUM,
        },
        # check seasons field, if no season, no point taken out
        "seasons": {
            "value": len(serie_data.get("seasons", [])) > 0,
            "priority": MEDIUM,
        },
        "overview": {"value": bool(serie_data.get("overview")), "priority": MEDIUM},
        # low priority
        "imdb_id": {"value": bool(processed_data.get("imdb_id")), "priority": LOW},
        "original_title": {
            "value": bool(serie_data.get("original_name")),
            "priority": LOW,
        },
        "last_air_date": {
            "value": bool(serie_data.get("last_air_date")),
            "priority": LOW,
        },
        "origin_country": {
            "value": len(serie_data.get("origin_country", [])) > 0,
            "priority": LOW,
        },
        "original_language": {
            "value": bool(serie_data.get("original_language")),
            "priority": LOW,
        },
        "vote_average": {
            "value": serie_data.get("vote_average") is not None
            and (
                type(serie_data.get("vote_average")) == int
                if first_air_date and first_air_date > today
                else serie_data.get("vote_average") > 0
            ),
            "priority": LOW,
        },
        "tagline": {"value": bool(serie_data.get("tagline")), "priority": LOW},
        "spoken_languages": {
            "value": len(processed_data.get("spoken_languages", [])) > 0,
            "priority": LOW,
        },
        "status": {"value": bool(serie_data.get("status")), "priority": LOW},
        "vote_count": {
            "value": serie_data.get("vote_count") is not None
            and (
                type(serie_data.get("vote_count")) == int
                if first_air_date and first_air_date > today
                else serie_data.get("vote_count") > 0
            ),
            "priority": LOW,
        },
        "popularity": {
            "value": serie_data.get("popularity") is not None
            and (
                type(serie_data.get("popularity")) == float
                if first_air_date and first_air_date > today
                else serie_data.get("popularity") > 0
            ),
            "priority": LOW,
        },
    }
    
    # pass the datas in function to return the score result of the serie 
    result, missing_fields = check_score_media(all_datas)

    if BASE_SCORE - result <= MIN_REQUIRED_SCORE:
        print(f" Too many missing fields! BREAK! No import. -- score: {BASE_SCORE - result}/{BASE_SCORE}")
        is_valid = False

        #-------------------------------------------------------------------
        # Temporary may help remove movies with insufficient data already in DB
        if Serie.objects.filter(tmdb_id=serie_data.get('id')).exists():
            print(f" -- More than half of the fields are missing! ({len(missing_fields)}/24) --")
            print(f"Deleting the serie from DB if existing...")
            try:
                Serie.objects.filter(tmdb_id=serie_data.get('id')).delete()
                print(f"serie with TMDB ID: {serie_data.get('id')} deleted from DB.")
            except Exception as e:
                print(f"An error occurred while deleting serie with TMDB ID: {serie_data.get('id')}. Error: {str(e)}")
                traceback.print_exc()

    else:
        print(f"Considerable amount of data, Can be imported! score: {BASE_SCORE - result}/{BASE_SCORE}")

    return is_valid


def check_score_media(all_datas):
    '''
    loop through processed fields, check how many fields are missing 
    and how much point taken out per priority
    '''
    missing_fields = [field for field, data in all_datas.items() if not data['value']]

    result = 0
    score = [data['priority'] for field, data in all_datas.items() if not data['value']]
    for s in score:
        result += s

    print(
        f"-- missing fields: {len(missing_fields)}, {missing_fields}.\n"
        f"-- missing score: {result} -- {score}"
    )
    return result, missing_fields