from import_data.api_services.TMDB.fetch_movies import get_movie_data
from import_data.api_services.TMDB.fetch_series import get_serie_data, get_season_data
from movie.models import Movie
from serie.models import Serie, Season, Episode
import time
import traceback

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
        # origin_country = []
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

        production = [company["name"] for company in movie_data.get("production_companies", [])] # List of production companies  #Tuple of list instead of list why ?


        movie, created = Movie.objects.update_or_create(
            tmdb_id=movie_data.get('id'), # check if the movie is already existing in the database
                defaults={
                    # External unique identifier
                    'imdb_id' : movie_data.get("imdb_id"),
                    # Core Movie Details
                    "original_title" : movie_data.get("original_title"),
                    "title" : movie_data.get("title") or movie_data.get("original_title"),  # Use original_title if title is missing
                    "release_date" : movie_data.get("release_date") or None,
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

        # print(f"Movie: '{movie_data.get('title')}' was added to DB.\n")
        # if created:
        #     print(f"New movie created: '{movie}'")
        #     print("---------")
        # else:
        #     print(f"Existing movie Updated: '{movie}'")
            # print("---------")

        print(f"movie: '{movie.title}' {'-- Created.' if created else '-- Updated.'}")
        print("---------")
        time.sleep(0.5) # to not trigger rate limit
        return (movie, created)

    except Exception as e:
        print(f"an error occurred while saving/updating movie: '{movie}' ", str(e))
        return None, False




def save_or_update_series(tmdb_id):
    """
    Fetches a single serie and it's content datas from TMDB API
    It Will also then retrieve the Season and Episodes data from that serie.
    - One new Api call is made per season fetched 
    (No call for episodes, datas are retrieved within that same call)
    """
    try:
        # search for the serie
        serie_data = get_serie_data(tmdb_id)

        # check if te API was called correctly and returned the datas
        if not serie_data:
            print(f"Failed to fetch serie data from TMDB api with ID: {tmdb_id}")
            # return  {
            #         'status': 'error',
            #         'tmdb_status_code': 34,
            #         'message': f'No serie found with TMDB ID: {tmdb_id}',
            #     } # Handle failure case
            return None, False

        print("Passing the new serie's instance\n") # debug print

        # Store the Serie data.
        languages = serie_data.get("spoken_languages", [])
        spoken_languages = [language["english_name"] for language in languages]

        # external_ids = serie_data.get("External_ids", [])
        imdb_id = serie_data.get("external_ids", {}).get("imdb_id")

        try:
            # Store the new serie in DB
            serie, is_created = Serie.objects.update_or_create(
                tmdb_id=serie_data.get('id'),
                defaults={  # Fields to update if the object exists
                    "imdb_id": imdb_id,
                    "original_title": serie_data.get('original_name'), 
                    "title": serie_data.get('name', 'Unknown Title'),
                    "description": serie_data.get('overview', 'No description available'),
                    "genre": [genre["name"] for genre in serie_data.get("genres", [])],
                    "origin_country": serie_data.get('origin_country'),
                    "original_language": serie_data.get('original_language'),
                    "spoken_languages": spoken_languages,
                    "tagline": serie_data['tagline'],
                    "production": [company["name"] for company in serie_data.get("production_companies", [])],
                    "created_by": [creator["name"] for creator in serie_data.get("created_by", [])],
                    "first_air_date": serie_data.get('first_air_date')  or None,
                    "last_air_date": serie_data.get('last_air_date')  or None,
                    "vote_average": serie_data.get('vote_average'),
                    "vote_count": serie_data.get('vote_count'),
                    "image_poster": serie_data.get('poster_path'),
                    "banner_poster": serie_data.get('backdrop_path'),
                    "status": serie_data.get('status'),
                }
            )

            if is_created:
                print(f"Created new serie: {serie}\n")
            else:
                print(f"Updated existing serie: {serie}\n")
        except Exception as e:
            print(f"An error occurred while saving/updating serie: {str(e)}")
            print(f"Serie: '{serie_data.get('name')}' failed to add fully to DB.\n")# log print
            print("--------------")
            return (None, False)

        # --------- Passing on the seasons ------------------------------
        datas_season = [] # to display some result in the json return.
        
        seasons = serie_data.get('seasons', [])
        # print(f"seasons: {seasons}") # get all seasons data from serie

        number_of_seasons = []
        number_of_seasons = [season["season_number"] for season in seasons]
        print(f"Number of seasons: {len(number_of_seasons)}\n")

        for season_number in number_of_seasons:
            time.sleep(3) # to avoid hitting the TMDB API too quickly
            print("--------------")
            print(f"Fetching season {season_number} out of {len(number_of_seasons)} ({serie})\n") # debug print
            season_data = get_season_data(tmdb_id, season_number)
            # print("DONE DONE")
            # Extract credits from the combined response

            if season_data is None:
                print(f"Failed fetching season {season_number} for {serie} due to api misscall.")
                print(f"recalling the url endpoint for: {serie} season: {season_number}.")
                season_data = get_season_data(tmdb_id, season_number)
                continue 

            credits_data = season_data.get('credits', {})

            # initialize json fields
            producers =[]
            cast = []
            spoken_languages = []
            youtube_trailer = []

            if credits_data:
                # Top 10 cast members (takes the name and role)
                cast = [
                    {
                        "name": member["name"], 
                        "role": member["character"]
                    }
                    for member in credits_data.get("cast", [])[:10] 
                    if member.get("known_for_department") == "Acting"
                ] 

                producers = [
                    {
                        "name": member["name"], 
                        "job": member["job"]
                    }
                    for member in credits_data.get("crew", [])[:8] 
                    if member.get("department") == "Production"
                ]

            # Extract trailer from the combined response
            trailer_data = season_data.get("videos", {}).get("results", [])

            for trailer in trailer_data[:4]:
                if trailer["type"] in ["Trailer", "Featurette", "Teaser"] and trailer['site'] == "YouTube":
                    youtube_trailer.append(
                        {
                            "website": trailer["site"],
                            "key": trailer["key"]
                        }
                    )

            # TODO
            # check what seasons already exist
            # check if current seasons has more than one season ahead, skip
            # example: looping season 4, if more than 6 seasons available, skip
            # one season behind the last one, might need episode updates, and create the latest season

            season, created = Season.objects.update_or_create(
                tmdb_id = season_data.get('id'),
                defaults={  # Fields to update if the object exists
                "serie" : serie,
                "name" : season_data.get("name"),
                "season_number" : season_number,
                "producer" : producers,
                "casting" :  cast,
                "description" : season_data.get('overview'),
                "image_poster" : season_data.get('poster_path'),
                "trailers" : youtube_trailer,
                # banner_poster=season_data['still_path'],  will go in episode  ["episode"] and loop through for each episode
                }
            )

            if created:
                print(f"Created new season: *{season}* to DB\n")
            else:
                print(f"Updated existing season: *{season}*\n")

            # ---------------------- Importing episodes-------------------------:

            # to update episode instance creation with Bulkupdate / bulk create instead of update or create
            # to avoid many queries
            # instantiate a list for episodes to create in bulk (saves on query) // Bulk purpose 
            existing_episodes = []
            new_episodes = []
            
            list_episodes = season_data.get('episodes', [])# all episodes here
            print(f"Season contains {len(list_episodes)} episodes: ")

            datas_season.append(
                [season_data.get("name"), f"total episodes: {len(list_episodes)}"]
            )

            # Loop through each episode, Update existing episode or create new ones.
            for episode in list_episodes:
                # print(f"Episode: {episode}\n") # debug print
                guest_names = []
                directors = []
                writers = []

                # Extract credits from the combined response / actors, wrtiters, directors
                # check if credit available before trying to insert
                guest_names = [
                    {
                        "name": guest["name"], 
                        "role": guest["character"]
                    }
                    for guest in episode.get("guest_stars", [])[:10] 
                    if guest.get("known_for_department") == "Acting"
                ]

                directors = [
                    director["name"] for director in episode.get("crew", [])[:3]
                    if director.get("department") == "Directing"
                    ]
                
                writers = [
                    writer["name"] for writer in episode.get("crew", [])[:4]
                    if writer.get("department") == "Writing"
                    ]
                # print(f"directors :{directors}\n") # debug print
                # print(f"{writers}") # debug print
                
                try:

                    episode, created = Episode.objects.update_or_create(
                        season = season,
                        episode_number = episode.get("episode_number"),
                        defaults={  # Fields to update if the object exists
                            'title' : episode.get("name", "Unknown Title"),
                            'description' : episode.get('overview', "No description available"),
                            'length' : episode.get("runtime"),
                            'release_date' : episode.get('air_date') or None,
                            'guest_star' : guest_names,
                            'director' : directors,
                            'writer' : writers,
                            'banner_poster' : episode.get('still_path'),
                            'tmdb_id' : episode.get('id'),
                        }
                        # title = episode.get("name", "Unknown Title"),
                        # description = episode.get('overview', "No description available"),
                        # length = episode.get("runtime"),
                        # release_date = episode.get('air_date') or None,
                        # guest_star = guest_names,
                        # director = directors,
                        # writer = writers,
                        # banner_poster = episode.get('still_path'),
                        # tmdb_id = episode.get('id'),
                    )

                    if created:
                        print(f"Added new episode: *{episode}*")
                    else:
                        print(f"Updated existing episode: *{episode}*")
                # except IntegrityError:
                #     # Fetch the serie again if the constraint is hit
                #     episode = Episode.objects.get(tmdb_id=serie_data["tmdb_id"])
                #     created = False

                except Exception as e:
                    print(f"An error occurred while saving/updating episode: {str(e)}")
                    print(f"Episode: '{episode.get('name', 'Unknown Title')}' failed to add fully to DB.\n")# log print
                    print("----------")
                time.sleep(0.1) # space time between episodes to avoid overcharging cpu

        print(f"title: {serie.title} -- (id {serie.id}) -- Contains:")
        print(datas_season)

        # return serie if Created or Updated, is_created allow to log differece between these 2
        return (serie, is_created)

    except Exception as e:
        # Catch any unexpected errors during the process
        print(traceback.format_exc())
        print(f"An error occurred: {str(e)}")
        return (None, False)
