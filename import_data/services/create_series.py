import time
from datetime import datetime
import traceback
import random

from django.utils import timezone
from django.utils.text import slugify


# from import_data.api_clients.TMDB.fetch_series import get_serie_data, get_season_data
from import_data.api_clients.TMDB.fetch_data import get_api_data
from serie.models import Serie, Season, Episode


def save_or_update_series(tmdb_id):
    """
    - Fetches a single serie and it's content datas from TMDB API
    It Will also then retrieve the Season and Episodes data from that serie.
    - One new Api call is made per season fetched 
    (No call for episodes, datas are retrieved within that same call)
    """
    try:
        # search for the serie
        serie_data = get_api_data(
            t_type = 'serie',
            tmdb_id=tmdb_id
        )

        # check if te API was called correctly and returned the datas
        if not serie_data:
            print(f"Failed to fetch serie data from TMDB api with ID: {tmdb_id}")
            # return  {
            #         'status': 'error',
            #         'tmdb_status_code': 34,
            #         'message': f'No serie found with TMDB ID: {tmdb_id}',
            #     } # Handle failure case
            return None, False

        print(f"Passing the new serie's instance name: {serie_data.get('original_name')}") # debug print

        # Store the Serie data.
        languages = serie_data.get("spoken_languages", [])
        spoken_languages = [language["english_name"] for language in languages]

        # external_ids = serie_data.get("External_ids", [])
        imdb_id = serie_data.get("external_ids", {}).get("imdb_id")

        # Convert the first air date (first released) to a datetime object if it exists
        first_air_date = None
        if serie_data.get('first_air_date'):
            try:
                first_air_date = datetime.strptime(serie_data.get('first_air_date'), '%Y-%m-%d').date()
            except ValueError:
                # If the first_air_date is not available, it stays set to None
                print(f"Invalid date format: {serie_data.get('first_air_date')}")

        try:
            # Store the new serie in DB
            serie, is_created = Serie.objects.update_or_create(
                tmdb_id=serie_data.get('id'),
                defaults={  # Fields to update if the object exists
                    "imdb_id": imdb_id,
                    "original_title": serie_data.get('original_name'), 
                    "title": serie_data.get('name'),
                    "description": serie_data.get('overview'),
                    "genre": [genre["name"] for genre in serie_data.get("genres", [])],
                    "origin_country": serie_data.get('origin_country'),
                    "original_language": serie_data.get('original_language'),
                    "spoken_languages": spoken_languages,
                    "tagline": serie_data['tagline'],
                    "production": [company["name"] for company in serie_data.get("production_companies", [])],
                    "created_by": [creator["name"] for creator in serie_data.get("created_by", [])],
                    "first_air_date": first_air_date,
                    "last_air_date": serie_data.get('last_air_date') or None,
                    "vote_average": serie_data.get('vote_average'),
                    "vote_count": serie_data.get('vote_count'),
                    "popularity" : serie_data.get("popularity"),
                    "image_poster": serie_data.get('poster_path'),
                    "banner_poster": serie_data.get('backdrop_path'),
                    "status": serie_data.get('status'),
                }
            )

            if is_created:
                print(f"*New serie Created: {serie}")
            else:
                print(f"*Existing serie Updated: {serie}")
        except Exception as e:
            print(f"An error occurred while saving/updating serie: {str(e)}")
            print(f"Serie: '{serie_data.get('name')}' failed to add fully to DB.")# log print
            print("--------------", "\n")
            time.sleep(2) # so I can see the error message before the next one
            return (None, False)

        # --------- Passing on the seasons ------------------------------
        datas_season = [] # to display some result in the json return.
        
        seasons = serie_data.get('seasons', [])
        # print(f"seasons: {seasons}") # get all seasons data from serie

        number_of_seasons = []
        number_of_seasons = [season["season_number"] for season in seasons]
        print(f"Number of seasons: {len(number_of_seasons)}")

        # ------------IN PROGRESS Trying to not update every single season if only one is new ------------------

        if not is_created and len(number_of_seasons) == 0:
            print(f"Serie: {serie} has no seasons to update.")
            return (serie, is_created)


        # TODO
        # check what seasons already exist
        # if not is_created and len(number_of_seasons) > 0
        #     existing_seasons = Season.objects.filter(serie_id=serie.pk).values_list('season_number', flat=True).order_by('season_number')
        #     if existing_seasons:
        #         existing_seasons = list(existing_seasons)
        #         print(f"Existing seasons: {existing_seasons}\nlen: {len(existing_seasons)}") # debug print
        #     print(f"TEST TEST TEST\n")


        # # check if current seasons fetched has more than one season ahead that what is already DB,
        # # if so, we can skip the seasons that are already in the DB and only update the new ones and the last in DB.
        #     if existing_seasons and number_of_seasons:
        #         print(f"Serie: {serie} has no new seasons to update., updating the last one.")
        #         # check if the last season in DB is the same as the last one in TMDB
        #         last_season_in_db = existing_seasons[-1]
        #         if last_season_in_db.season_name == number_of_seasons[-1].season_name:
        #             print(f"Serie: {serie} has no new seasons to update., updating the last one.")
        #             print(f"TEST TEST TEST22\n")
        #             time.sleep(4) # so i can check what is happening
        #             pass
            

        # ------------END OF IN PROGRESS  ------------------


        for season_number in number_of_seasons:
            time.sleep(4) # to avoid hitting the TMDB API too quickly
            print("--------------")
            print(f"Fetching season {season_number} out of {len(number_of_seasons)} ({serie})") # debug print
            
            # Get the Seasons and Episode details data to save.
            season_data = get_api_data(
                tmdb_id=tmdb_id,
                season_number=season_number,
                t_type = 'season'

                )
            # print("DONE DONE")
            # Extract credits from the combined response

            # Need to look over this part below, if logic is correct. 
            # continue may just go over the next iteration
            if season_data is None:
                print(f"Failed fetching season {season_number} for {serie} due to api misscall.")
                print(f"recalling the url endpoint for: {serie} season: {season_number}.")
                
                season_data = get_api_data(
                    tmdb_id=tmdb_id,
                    season_number=season_number,
                    t_type = 'season'
                    )
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
                    for member in credits_data.get("cast", []) 
                    if member.get("known_for_department") == "Acting"
                ] 

                producers = [
                    {
                        "name": member["name"], 
                        "job": member["job"]
                    }
                    for member in credits_data.get("crew", []) 
                    if member.get("department") == "Production"
                ]

            # Extract trailer from the combined response
            trailer_data = season_data.get("videos", {}).get("results", [])

            for trailer in trailer_data:
                if trailer["type"] in ["Trailer", "Featurette", "Teaser"] and trailer['site'] == "YouTube":
                    youtube_trailer.append(
                        {
                            "website": trailer["site"],
                            "key": trailer["key"]
                        }
                    )
            youtube_trailer = random.sample(
                youtube_trailer, min(len(youtube_trailer), 4)
                ) # Select up to 4 random trailers

            season, created = Season.objects.update_or_create(
                tmdb_id = season_data.get('id'),
                defaults={  # Fields to update if the object exists
                "serie" : serie,
                "name" : season_data.get("name"),
                "season_number" : season_number,
                "producer" : producers[:8],
                "casting" :  cast[:10],
                "description" : season_data.get('overview'),
                "image_poster" : season_data.get('poster_path'),
                "trailers" : youtube_trailer,
                }
            )

            if created:
                print(f"New season Created: *{season}* to DB")
            else:
                print(f"Existing season Updated: *{season}*")

            # ---------------------- Importing episodes!! -------------------------:

            # instantiate lists for new episodes and existing  to pass in bulk (saves on query)
            update_episodes_obj = []
            new_episodes_obj = []
            
            list_episodes = season_data.get('episodes', [])# all episodes here
            print(f"--- Season contains *{season}* {len(list_episodes)} episodes. ---")

            datas_season.append(
                [season_data.get("name"), f"total episodes: {len(list_episodes)}"]
            )

            # Retrieve existing episode IDs for this season (to differentiate between new & existing episodes)
            existing_episodes = {
                ep.tmdb_id: ep for ep in Episode.objects.filter(season=season)
            }
            print(f"Existing episodes: {len(existing_episodes)}") # debug print

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
                    for guest in episode.get("guest_stars", []) 
                    if isinstance(guest, dict) and guest.get("known_for_department") == "Acting"
                ]

                # Extract directors and writers
                crew_members = episode.get("crew", [])
                episode_tmdb_id = episode.get('id')
                episode_number = episode.get("episode_number")
                episode_title = episode.get("name", "Unknown Title")

                for member in crew_members:
                    if isinstance(member, dict):
                        if member.get("department") == "Directing":
                            directors.append(member["name"])
                        elif member.get("department") == "Writing":
                            writers.append(member["name"])

                try:
                    # Check if the episode already exists in the database
                    # If it does, update it; if not, create a new one.
                    if episode_tmdb_id in existing_episodes:
                        # prepare episode for update the already existing.
                        existing_episode = existing_episodes[episode_tmdb_id]

                        existing_episode.episode_number = episode_number

                        existing_episode.title = episode_title
                        existing_episode.description = episode.get('overview', "No description available")
                        existing_episode.length = episode.get("runtime") or None
                        existing_episode.release_date = episode.get('air_date') or None
                        existing_episode.guest_star = guest_names[:10]
                        existing_episode.director = directors[:4]  # Limit to first 5 directors
                        existing_episode.writer = writers[:4]
                        existing_episode.banner_poster = episode.get('still_path')
                        existing_episode.updated_at = timezone.now() # trigger updated_at as Bulk_update do not use .save()
                    
                        update_episodes_obj.append(existing_episode)  # Add to the list for bulk update
                        # print(f"Updating existing episode: {existing_episode}\n")
                    
                    else:
                        # Create a new episode instance if it doesn't exist
                        new_episodes_obj.append(Episode(
                            season = season,
                            episode_number = episode_number,
                            title = episode.get("name", "Unknown Title"),
                            description = episode.get('overview', "No description available"),
                            length = episode.get("runtime") or None,
                            release_date = episode.get('air_date') or None,
                            guest_star = guest_names[:10],
                            director = directors[:4],
                            writer = writers[:4],
                            banner_poster = episode.get('still_path'),
                            tmdb_id = episode_tmdb_id,
                        ))

                except Exception as e:
                    print(f"An error occurred while saving/updating episode: {str(e)}")
                    print(f"Episode: '{episode.get('name', 'Unknown Title')}' failed to add fully to DB.\n")# log print
                    print("----------")
                    continue  # Skip to the next episode if an error occurs
                # time.sleep(0.1) # space time between episodes

            # bulk create new episodes
            if new_episodes_obj:
                Episode.objects.bulk_create(new_episodes_obj)
                print(f"Added {len(new_episodes_obj)} new episodes to DB.")

            # bulk update for existing episodes
            if update_episodes_obj:
                Episode.objects.bulk_update(update_episodes_obj, [
                    'title', 'episode_number', 'description', 'length',
                    'release_date', 'guest_star', 'director', 'writer',
                    'banner_poster', 'updated_at'
                ])
                print(f"Updated {len(update_episodes_obj)} existing episodes in DB.")

            generate_episode_slug(season)

        print(f"title: {serie.title} -- (id {serie.pk}) -- Contains:")
        print(datas_season)

        # return serie if Created or Updated, is_created allow to log differece between these 2
        return (serie, is_created)

    except Exception as e:
        # Catch any unexpected errors during the process
        print(traceback.format_exc())
        print(f"\n\nAn error occurred: {str(e)}")
        return (None, False)


def generate_episode_slug(season):
    '''
    Generate unique slugs for all episodes in a given season.\n
    As Episode are recorded with Bulk update or create, they do not have slugs generated.
    '''
    start_time = time.time()
    count= 0

    episodes = Episode.objects.filter(season=season, slug__isnull=True)
    updated_episodes = []
    total = episodes.count()

    if total == 0: # no episodes recorded in the season, stops here.
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("✅ All episodes already have slugs. No action needed.")
        # print(f"time: {elapsed_time:.2f} seconds.")
        return

    # print(f"Found {total} Episodes without slugs. Processing...")
    existing_slugs = set(Episode.objects.filter(season=season).values_list('slug', flat=True))
    new_slugs = set()

    for episode in episodes:
        count += 1
        if episode.season and episode.title:
            base_slug = slugify(f"{episode.season.serie.slug} S{episode.season.season_number} E{episode.episode_number} {episode.title}")
            unique_slug = base_slug
            counter = 1

            # ensure slug is unique in the database and in the new slugs set
            while unique_slug in existing_slugs or unique_slug in new_slugs:
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            episode.slug = unique_slug
            updated_episodes.append(episode)
            new_slugs.add(unique_slug)

    if updated_episodes:
        Episode.objects.bulk_update(updated_episodes, ['slug'])
        print(f"✅ Successfully Added slugs to {len(updated_episodes)} Episodes .")
    else:
        print("⚠️ No Episodes needed updating.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"time: {elapsed_time:.2f} seconds.\n")