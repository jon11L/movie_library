from .models import Serie, Season, Episode
from api_services.TMDB.base_client import TMDBClient
from api_services.TMDB.fetch_series import get_serie_details, get_season_details
import time
import traceback

def add_series_from_tmdb(tmdb_id):
    """
    Fetches a single series and it's content datas from TMDB API 
    Check if the series already exists otherwise saves it in the database.
    """
    try:
        # search for the serie
        serie_data = get_serie_details(tmdb_id)

        # check if te API was called correctly and returned the datas
        if not serie_data:
            print(f"\nFailed to fetch serie data from TMDB api with ID: {tmdb_id}\n")
            return  {
                    'status': 'error',
                    'tmdb_status_code': 34,
                    'message': f'No serie found with TMDB ID: {tmdb_id}',
                } # Handle failure case

        print("passing datas into field for the new serie's instance\n") # debug print

        # Store the Serie data.
        languages = serie_data.get("spoken_languages", [])
        spoken_languages = [language["english_name"] for language in languages]

        # external_ids = serie_data.get("External_ids", [])
        imdb_id = imdb_id = serie_data.get("external_ids", {}).get("imdb_id")

        # store the new serie in DB
        serie = Serie.objects.create(
            original_title=serie_data.get('original_name'), 
            title=serie_data.get('name'),
            description=serie_data.get('overview'),
            genre = [genre["name"] for genre in serie_data.get("genres", [])],
            origin_country = serie_data.get('origin_country'),
            original_language=serie_data.get('original_language'),
            spoken_languages=spoken_languages,
            tagline=serie_data['tagline'],
            production = [company["name"] for company in serie_data.get("production_companies", [])], # List of production companies
            created_by = [creator["name"] for creator in serie_data.get("created_by", [])],
            # casting = cast,
            vote_average=serie_data.get('vote_average'),
            vote_count=serie_data.get('vote_count'),
            image_poster=serie_data.get('poster_path'),
            banner_poster=serie_data.get('backdrop_path'),
            status=serie_data.get('status'),
            tmdb_id=serie_data.get('id'), 
            imdb_id = imdb_id,
        )

        print(f"\nSerie tv: '{serie.title}' added to DB.\n")
        print(f"looking for seasons...\n")

        # --------- Passing on the seasons ------------------------------
        datas_season = [] # to display some result in the json return.
        
        seasons = serie_data.get('seasons', [])
        print(f"seasons: {seasons}") # get all seasons data from serie

        number_of_seasons = []
        number_of_seasons = [season["season_number"] for season in seasons]
        print(f"\nnumber of seasons: {number_of_seasons}\n")

        for season_number in number_of_seasons:
            print(f"trying season {season_number}") # debug print
            time.sleep(4) # to avoid hitting the TMDB API too quickly
            season_data = get_season_details(tmdb_id, season_number)
            # print(f"season_data: {season_data}") # debug print

            # Extract credits from the combined response
            credits_data = season_data.get('credits', {})

            # initialize json fields
            producers =[]
            cast = []
            youtube_trailer = []
            spoken_languages = []
            youtube_trailer = []

            if credits_data:
                # Top 10 cast members (takes the name and role)
                cast = [
                    {
                        "name": member["name"], 
                        "role": member["character"]
                    }
                    for member in credits_data.get("cast", [])[:10] if member["known_for_department"] == "Acting"
                ] 

                producers = [
                    {
                        "name": member["name"], 
                        "job": member["job"]
                    }
                    for member in credits_data.get("crew", [])[:8] if member["department"] == "Production"
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

            print(f"serie: {serie}")

            season = Season.objects.create(
                serie=serie,
                name = season_data.get("name"),
                season_number=season_number,
                producer=producers,
                casting = cast,
                description=season_data.get('overview'),
                image_poster=season_data.get('poster_path'),
                # banner_poster=season_data['still_path'],  will go in episode  ["episode"] and loop through for each episode
                trailers = youtube_trailer,
                tmdb_id = season_data.get('id'),
            )

            print(f"Season {season_number}: '{season.name}' added to DB.\n")
            

            # ------- passing on episodes-------------:
            number_of_episode = season_data.get('episodes', [])
            # print(f"episodes: {number_of_episode["episode_number"]}")

            # pass on the new fields for episode
            for episode in number_of_episode:

                # print(f"Episode: {episode}\n") # debug print

                guest_names = []
                directors = []
                writers = []

                # Extract credits from the combined response

                guest_names = [
                    {
                        "name": guest["name"], 
                        "role": guest["character"]
                    }
                    for guest in episode.get("guest_stars", [])[:10] if guest["known_for_department"] == "Acting"
                ]


                directors = [director["name"] for director in episode.get("crew", [])[:3] if director["department"] == "Directing"]
                # print(f"directors :{directors}\n") # debug print
                

                writers = [writer["name"] for writer in episode.get("crew", []) if writer["department"] == "Writing"]
                # print(f"{writers}") # debug print

                new_episode = Episode.objects.create(
                    season=season,
                    episode_number = episode.get("episode_number"),
                    title=episode.get("name"),
                    description=episode.get('overview'),
                    length=episode.get("runtime"),
                    release_date=episode.get('air_date'),
                    guest_star=guest_names,
                    director = directors,
                    writer = writers,
                    banner_poster = episode.get('still_path'),
                    tmdb_id = episode.get('id'),
                    
                )

                print(f"added episode: {new_episode}")
                time.sleep(0.2)
                
            datas_season.append(
                {
                "season": season_data.get("name"),
                "total episodes for season": len(number_of_episode)
                }
            )

        print("reaching end of import\n")
        print(f"serie: {serie.id}, title: {serie.title}\n")
        print(f"data_season: {datas_season}\n")

        return {
            'status': 'added', 
            'serie_id': serie.id,
            'title': serie.title if serie.title else "Unknown Title",
            "datas_season": datas_season, 
            'tmdb_id': serie.tmdb_id, 
            'message': 'Serie was successfully added to the DB.'
        }
        

    except Exception as e:
        # Catch any unexpected errors during the process
        print(traceback.format_exc())
        return {
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }


# id for breakingbad  1396
# id for black mirror  42009