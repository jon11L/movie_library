import time
import datetime
import traceback
import random

from django.utils import timezone
from django.utils.text import slugify
from django.db import IntegrityError

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

    except Exception as e:
        # Catch any unexpected errors during the process
        print(traceback.format_exc())
        print(f"\n\nAn error occurred: {str(e)}")
        return (None, False)

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

    # fetch and prepare the Serie's data fields.
    created_by = [creator["name"] for creator in serie_data.get("created_by", [])]
    genre = [genre["name"] for genre in serie_data.get("genres", [])]
    spoken_languages = [
        language["english_name"] for language in serie_data.get("spoken_languages", [])
    ]

    production = [
        prod["name"] for prod in serie_data.get("production_companies", [])
        ]

    # external_ids = serie_data.get("External_ids", [])
    imdb_id = serie_data.get("external_ids", {}).get("imdb_id")

    # Convert the first air date (first released) to a datetime object if it exists
    first_air_date = None
    if serie_data.get('first_air_date'):
        try:
            first_air_date = datetime.datetime.strptime(serie_data.get('first_air_date'), '%Y-%m-%d').date()
        except ValueError:
            # If the first_air_date is not available, it stays set to None
            print(f"Invalid date format: {serie_data.get('first_air_date')}")

    # ---- Banner and Poster images -----
    select_posters = [] # will append the images to it an keep the urls only
    select_banners = []# same as above
    # Fetch and store images
    images = serie_data["images"]

    # Fetch and store posters images
    posters = images.get("posters", [])
    if posters is not None:
        select_posters = [sel['file_path'] for sel in posters[:4]] 

    if serie_data.get('poster_path') and serie_data.get('poster_path') not in select_posters:
        # append the original poster // to 1st element
        select_posters.insert(0, serie_data.get('poster_path'))
    elif serie_data.get('poster_path') and serie_data.get('poster_path') in select_posters:
        # remove the 'main' poster path to append it to the beginning
        try:
            select_posters.remove(serie_data.get('poster_path'))
        except ValueError as e:
            print(f"Value error: {e}\n")
            print(f"Could not remove the poster path to append to first index.")
        select_posters.insert(0, serie_data.get('poster_path'))

    poster_images = select_posters # set to save in the object

    # Fetch and store Banner images
    banners = images.get("backdrops", [])
    if banners is not None:
        select_banners = [sel['file_path'] for sel in banners[:4]] 

    if serie_data.get('backdrop_path'):
        # append the original banner to 1st element, index 0
        select_banners.insert(0, serie_data.get('backdrop_path')) 
    elif serie_data.get('backdrop_path') and serie_data.get('backdrop_path') in select_banners:
        # remove the 'main' banner path, to append it to the beginning
        try:
            select_banners.remove(serie_data.get('backdrop_path'))
        except ValueError as e:
            print(f"Value error: {e}\n")
            print(f"Could not remove the poster path to append to first index.")
        select_banners.insert(0, serie_data.get('backdrop_path'))
    banner_images = select_banners # set to save in the object

    # ------ Will check if the serie fetched has enough data to be saved --------
    # store in a Dict to pass in the check_serie_validity function
    processed_data = {
        "production": production,
        "genre": genre,
        "created_by": created_by,
        "first_air_date" : first_air_date,
        "spoken_languages" : spoken_languages,
        "poster_images": poster_images,
        "banner_images": banner_images,
        "imdb_id": imdb_id,
    }

    is_valid = check_serie_validity(serie_data, processed_data)

    if is_valid:
        print(f"serie: {serie_data.get('original_name')} passes validity data-check. Saving the serie")
    else:
        # did not pass the validity check, does not save, stop here.
        print(f"serie: '{serie_data.get('original_name')}' did not pass the validity data-check. NOT saving the serie")
        return None, False

    try:
        # Store the new serie in DB
        serie, is_created = Serie.objects.update_or_create(
            tmdb_id=serie_data.get('id'),
            defaults={  # Fields to update if the object exists
                "imdb_id": imdb_id,
                "original_title": serie_data.get('original_name'), 
                "title": serie_data.get('name'),
                "overview": serie_data.get('overview'),
                "genre": genre,
                "origin_country": serie_data.get('origin_country'),
                "original_language": serie_data.get('original_language'),
                "spoken_languages": spoken_languages,
                "tagline": serie_data['tagline'],
                "production": production,
                "created_by": created_by,
                "first_air_date": first_air_date,
                "last_air_date": serie_data.get('last_air_date') or None,
                "vote_average": serie_data.get('vote_average'),
                "vote_count": serie_data.get('vote_count'),
                "popularity" : serie_data.get("popularity"),
                "poster_images": poster_images,
                "banner_images": banner_images,
                "status": serie_data.get('status'),
            }
        )

    except Exception as e:
        print(f"An error occurred while saving/updating serie: {str(e)}")
        print(f"Serie: '{serie_data.get('name')}' failed to save to DB.")# log print
        print(f"\n" + "=" * 50 + "\n\n")
        time.sleep(2) # so I can see the error message before the next one
        return (None, False)

    if serie and is_created:
        print(f"*New serie Created: {serie}")
    elif serie and not is_created:
        print(f"*Existing serie Updated: {serie}")
    # --------- Passing on the seasons ------------------------------

    number_of_seasons = []
    # extract the seasons number to loop and fetch in api.
    # expecting a list of dicts in 'seasons'
    seasons: list[dict] = serie_data.get('seasons', [])
    number_of_seasons = [season["season_number"] for season in seasons]
    print(f"Serie contains: {len(number_of_seasons)} seasons.")

    # call api and record seasons data
    result = get_seasons(serie, number_of_seasons, tmdb_id)
    if not result:
        print(f"There are no season in this serie. unsual, should remove the serie.")
    else:
        for i in result:
            print(i)
        print("\n")

    return serie, is_created


def get_seasons(serie: object, number_of_seasons: list[int], tmdb_id: int):

    datas_season = [] # to display some result in the json return.

    # loop through the list of season and calling the databas
    for season_number in number_of_seasons:
        time.sleep(4) # to avoid hitting the TMDB API too quickly
        print("\n" + "=" * 50 + "\n\n")
        print(f"Fetching season {season_number} out of {len(number_of_seasons)} -- ({serie})") # debug print

        # Get the Seasons and Episode details data to save.
        season_data = get_api_data(
            tmdb_id=tmdb_id,
            season_number=season_number,
            t_type = 'season'
            )

        # Need to look over this part below, if logic is correct.
        # continue may just go over the next iteration
        if not season_data:
            print(f"Failed fetching season {season_number} for {serie} due to api misscall.")
            print(f"recalling the url endpoint for: {serie} season: {season_number}.")
            season_data = get_api_data(
                tmdb_id=tmdb_id,
                season_number=season_number,
                t_type = 'season'
                )
            # pass
        if season_data:

            # initialize json fields
            producers =[]
            cast = []
            yt_trailer = []

            credits_data = season_data.get('credits', {})
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
            # main_trailer = []

            second_trailer = []
            for trailer in trailer_data:

                if trailer['site'] != "YouTube":
                    continue

                if trailer["type"] in ["Trailer", "Teaser"]:
                    yt_trailer.append(
                        {
                            "website": trailer["site"],
                            "key": trailer["key"]
                        }
                    )

                if trailer["type"] in ["Featurette"]:
                    second_trailer.append(
                        {"website": trailer["site"], "key": trailer["key"]}
                    )

            print(f"trailer count: {len(yt_trailer)}")
            # if not enough trailer we append the featurette
            if len(yt_trailer) <= 3:
                need = 6 - len(yt_trailer)
                for i in second_trailer[:need]:
                    yt_trailer.append(i)

            # Fetch and store images
            posters = [] # will append the images to it an keep the urls only to
            images = season_data["images"]

            posters_data = images.get("posters", [])
            if posters_data is not None:
                posters = [sel['file_path'] for sel in posters_data[:4]] 

            if season_data.get('poster_path') and season_data.get('poster_path') not in posters:
                # append the original poster // to 1st element
                posters.insert(0, season_data.get('poster_path')) 

            try:
                # probably need to change the key with tmdb_id check for serie/season_number unique constraint
                # as tmdb_id may change
                # Create or update the season iterated
                season, created = Season.objects.update_or_create(
                    tmdb_id = season_data.get('id'),
                    defaults={  # Fields to update if the object exists
                    "serie" : serie,
                    "season_number" : season_number,
                    "name" : season_data.get("name"),
                    "producer" : producers[:8],
                    "casting" :  cast[:10],
                    "overview" : season_data.get('overview'),
                    "poster_images": posters,
                    "trailers" : yt_trailer,
                    }
                )

            except Exception as e:
                print(
                    f"An error occurred while saving/updating episode:\n{str(e)}\n"
                    f"Season: '{season_data.get('name')}' failed to save into DB.\n"
                    "----------"
                    )# log print

                continue  # Skip to the next season if an error occurs

            list_episodes = season_data.get('episodes', [])# all episodes here
            print(f"-- *{season}* contains {len(list_episodes)} episodes. ---")

            datas_season.append(
                f"{season_data.get("name")} -- total episodes: {len(list_episodes)}"
            )

            if season and created:
                print(f"New season Created: *{season}* to DB")
                get_episodes(list_episodes, season)
            elif season and not created:
                print(f"Existing season Updated: *{season}*")
                get_episodes(list_episodes, season)

            else:
                print("No seasons were created or updated... -- Warning--")

    return datas_season


def get_episodes(list_episodes, season: object):
    '''
        load any existing episodes from the season given.\n
        loop through the episodes from the season data api response\n
        update if episode number already exist. create if not
    '''
    # ---------------------- Importing episodes!! -------------------------:

    # instantiate lists for new episodes and existing  to pass in bulk (saves on query)
    update_episodes_obj = []
    new_episodes_obj = []

    # Retrieve existing episode IDs for this season
    # (to differentiate between new & existing episodes)
    existing_episodes = {
        (ep.season.pk, ep.episode_number): ep
        for ep in Episode.objects.filter(season=season)
    }
    print(f"Existing episodes: {len(existing_episodes)}") # debug print
    print(f"total episode in serie: {len(list_episodes)}")

    # Loop through each episode, Update existing episode or create new ones.
    for episode in list_episodes:
        # print(f"Episode: {episode}\n") # debug print
        guest_names = []
        directors = []
        writers = []
        ep_banner_img = []
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

        # do not take if value is Null for banner_image,  better empty file than Null
        if episode.get('still_path') != None:
            ep_banner_img = [episode.get('still_path')]

        try:
            # Check if the episode already exists in the database
            # If it does, update it; if not, create a new one.
            key = (season.pk, episode_number)
            # print(f"key check to see if episode already exist or not:")
            # print(f"key {key}")
            if key in existing_episodes:
                # prepare episode for update the already existing.
                existing_episode = existing_episodes[key]

                existing_episode.season = season
                existing_episode.episode_number = episode_number
                existing_episode.title = episode_title
                existing_episode.overview = episode.get('overview', "")
                existing_episode.length = episode.get("runtime") or None
                existing_episode.release_date = episode.get('air_date') or None
                existing_episode.guest_star = guest_names[:10]
                existing_episode.director = directors[:4]  # Limit to first 5 directors
                existing_episode.writer = writers[:4]
                existing_episode.banner_images = ep_banner_img
                existing_episode.updated_at = timezone.now() # trigger updated_at as Bulk_update do not use .save()
                existing_episode.tmdb_id = episode_tmdb_id

                update_episodes_obj.append(existing_episode)  # Add to the list for bulk update
                # print(f"Updating existing episode: {existing_episode}\n")

            else:
                # Create a new episode instance if it doesn't exist
                new_episodes_obj.append(Episode(
                    season = season,
                    episode_number = episode_number,
                    title = episode.get("name", "Unknown Title"),
                    overview = episode.get('overview', ""),
                    length = episode.get("runtime") or None,
                    release_date = episode.get('air_date') or None,
                    guest_star = guest_names[:10],
                    director = directors[:4],
                    writer = writers[:4],
                    banner_images = ep_banner_img,
                    tmdb_id = episode_tmdb_id
                ))

        except IntegrityError as e:
            print(f"An error occurred while saving/updating episode:\n{str(e)}\n")
            print(f"Episode: '{episode.get('name', 'Unknown Title')}' failed to save into DB.\n")# log print
            print("----------")
            continue  # Skip to the next episode if an error occurs
        except Exception as e:
            print(f"An error occurred while saving/updating episode:\n{str(e)}\n")
            print(f"Episode: '{episode.get('name', 'Unknown Title')}' failed to save into DB.\n")# log print
            print("----------")
            continue  # Skip to the next episode if an error occurs
        # time.sleep(0.1) # space time between episodes

    # bulk update for existing episodes
    if update_episodes_obj:
        try:
            Episode.objects.bulk_update(update_episodes_obj, [
                'episode_number', 'title', 'overview', 'length',
                'release_date', 'guest_star', 'director', 'writer',
                'banner_images', "tmdb_id", 'updated_at'
            ])
            print(f"Updated {len(update_episodes_obj)} episodes for season {season}.")

        except IntegrityError as e:
            print(f"Integrity Error during bulk update of episodes:\n{str(e)}\n")
            print(traceback.format_exc())
            print(f"\nEpisode: '{episode.get('name', '')}' failed to be saved in DB.\n")# log print
            print("----------")
            for ep in update_episodes_obj:
                try:
                    ep.save()
                except IntegrityError as e:
                    print(f"Integrity Error during bulk update of episodes:\n{str(e)}\n")
                    print(f"Skipping duplicate episode '{ep.episode_number}' in season: {season}")

        except Exception as e:
            print(f"An error occurred during bulk update of episodes:\n{str(e)}\n")
            print(traceback.format_exc())
            print(f"\nEpisode: '{episode.get('name', '')}' failed to be saved in DB.\n")# log print
            print("----------")
            for ep in update_episodes_obj:
                try:
                    ep.save()
                except IntegrityError as e:
                    print(f"Integrity Error during bulk update of episodes:\n{str(e)}\n")
                    print(f"Skipping duplicate episode '{ep.episode_number}' in season: {season}")

    if new_episodes_obj:
        try:
            # bulk create new episodes
            Episode.objects.bulk_create(new_episodes_obj)
            print(f"Added {len(new_episodes_obj)} new episodes for season {season}.")

        except IntegrityError as e:
            print(f"Integrity Error during bulk create of episodes:\n{str(e)}\n")
            print(traceback.format_exc())

            print(f"\nEpisode: '{episode.get('name', '')}' failed to be saved in DB.\n")# log print
            print("----------")

        except Exception as e:
            print(f"An error occurred during bulk create of episodes:\n{str(e)}\n")
            print(traceback.format_exc())
            print(f"\nEpisode: '{episode.get('name', '')}' failed to be saved in DB.\n")# log print
            print("----------")

    generate_episode_slug(season)


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

    for ep in episodes:
        count += 1
        if ep.season and ep.title:
            base_slug = slugify(
                f"{ep.season.serie.slug} S{ep.season.season_number}E{ep.episode_number} {ep.title}",
                allow_unicode=True
            )
            unique_slug = base_slug
            counter = 1

            # ensure slug is unique in the database and in the new slugs set
            while unique_slug in existing_slugs or unique_slug in new_slugs:
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            ep.slug = unique_slug
            updated_episodes.append(ep)
            new_slugs.add(unique_slug)

    if updated_episodes:
        Episode.objects.bulk_update(updated_episodes, ['slug'])
        print(f"Successfully Added slugs to {len(updated_episodes)} Episodes.")
    else:
        print("No Episodes needed updating.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"time: {elapsed_time:.2f} seconds.\n")


def check_serie_validity(serie_data, processed_data: dict):
    '''
    ### Check the amount of data concerning the new imported serie.
    The serie will not be imported/saved in DB if:
    - grade gets below MIN_REQUIRED_SCORE (32) then serie considered broken / will not be imported in Database
    - too many fields are missing datas **8**
    - Or 2/3 of critical fields are missing (title / poster_image / first_air_date / production / seasons) 
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
    first_air_date = processed_data.get("first_air_date")

    if first_air_date and first_air_date > today:
        print(f"Serie has a future release date: {first_air_date}.")
        MIN_REQUIRED_SCORE = 31
    else:
        print(f"Serie already released or no release date found: {first_air_date}.")
        MIN_REQUIRED_SCORE = 35

    # CRITICAL_FIELDS =  ("title", "poster_images", "casting", "description")
    # priorities:
    low = 1.5 # (11 fields), 
    medium = 3 # (5 fields), 
    high = 5 # (4)

    processed_data = processed_data
    # total fields to check: 19 for serie +1 for seasons = 20
    # check if there already some tale tell of seasons data.

    all_datas = {
        # high priority
        "title": {
            "value": bool(serie_data.get("name") or bool(serie_data.get("original_name"))),
            "priority": high,
        },
        "poster_images": {
            "value": len(processed_data.get("poster_images", [])) > 0,
            "priority": high,
        },
        "first_air_date": {
            "value": bool(processed_data.get("first_air_date")),
            "priority": high,
        },
        "production": {
            "value": len(processed_data.get("production", [])) > 0,
            "priority": high,
        },
        # medium priority
        "genre": {"value": len(processed_data.get("genre", [])) > 0, "priority": medium},
        "banner_images": {
            "value": len(processed_data.get("banner_images", [])) > 0,
            "priority": medium,
        },
        "created_by": {
            "value": len(processed_data.get("created_by", [])) > 0,
            "priority": medium,
        },
        # check seasons field, if no season, no point taken out
        "seasons": {
            "value": len(serie_data.get("seasons", [])) > 0,
            "priority": medium,
        },
        "overview": {"value": bool(serie_data.get("overview")), "priority": medium},
        # low priority
        "imdb_id": {"value": bool(processed_data.get("imdb_id")), "priority": low},
        "original_title": {
            "value": bool(serie_data.get("original_name")),
            "priority": low,
        },
        "last_air_date": {
            "value": bool(serie_data.get("last_air_date")),
            "priority": low,
        },
        "origin_country": {
            "value": len(serie_data.get("origin_country", [])) > 0,
            "priority": low,
        },
        "original_language": {
            "value": bool(serie_data.get("original_language")),
            "priority": low,
        },
        "vote_average": {
            "value": serie_data.get("vote_average") is not None
            and (
                type(serie_data.get("vote_average")) == int
                if first_air_date and first_air_date > today
                else serie_data.get("vote_average") > 0
            ),
            "priority": low,
        },
        "tagline": {"value": bool(serie_data.get("tagline")), "priority": low},
        "spoken_languages": {
            "value": len(processed_data.get("spoken_languages", [])) > 0,
            "priority": low,
        },
        "status": {"value": bool(serie_data.get("status")), "priority": low},
        "vote_count": {
            "value": serie_data.get("vote_count") is not None
            and (
                type(serie_data.get("vote_count")) == int
                if first_air_date and first_air_date > today
                else serie_data.get("vote_count") > 0
            ),
            "priority": low,
        },
        "popularity": {
            "value": serie_data.get("popularity") is not None
            and (
                type(serie_data.get("popularity")) == float
                if first_air_date and first_air_date > today
                else serie_data.get("popularity") > 0
            ),
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
