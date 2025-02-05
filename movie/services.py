from .models import Movie
from api_services.TMDB.base_client import TMDBClient
from api_services.TMDB.fetch_movies import get_movie_details


def add_movies_from_tmdb(tmdb_id):
    """
    Fetches a single movie and it'S content datas from TMDB API 
    Check if the movie already exists otherwise saves it in the database.
    """
    try:
        movie_data = get_movie_details(tmdb_id)

        # check if te API was called correctly and returned the datas
        if not movie_data:
            print(f"Failed to fetch movie data from TMDB api with ID: {tmdb_id}")
            return  {
                    'status': 'error',
                    'tmdb_status_code': 34,
                    'message': f'No movie found with TMDB ID: {tmdb_id}',
                } # Handle failure case

        # to place above in the function
        try:
            exisiting_movie = Movie.objects.get(tmdb_id=movie_data['id'])
            print(f"Movie already exists: movie {exisiting_movie.id}: {exisiting_movie.title}")
            return {
                'status': 'exists', 
                'tmdb_id': exisiting_movie.tmdb_id, 
                'movie_id': exisiting_movie.id,
                'title': exisiting_movie.title
            }

        except Movie.DoesNotExist:

            print("passing datas into field for the new movie's instance") # debug print
            
            # initialize empty list, for future jsonfield reference ... 
            director = []
            writers = []
            cast = []
            origin_country = []

            # Extract credits from the combined response
            credits_data = movie_data.get('credits', {})

            if credits_data:
                for person in credits_data.get("crew", []):
                    # append the directors for the  director field
                    if person["job"] == "Director":
                        director.append(person["name"])

                    # append the writers for the  Writer field
                    if person["job"] in ["Writer", "Screenplay"]:
                        writers.append(person["name"])

            # Top 10 cast members (takes the name and role)
            cast = [
                {
                    "name": member["name"], 
                    "role": member["character"]
                }
                for member in credits_data.get("cast", [])[:10]
            ]


            movie = Movie.objects.create(
                # External unique identifier
                tmdb_id = movie_data["id"],  # check if the movie is already existing in the database
                imdb_id = movie_data.get("imdb_id"),
                # Core Movie Details
                original_title = movie_data.get("original_title"),
                title=movie_data.get("title") or movie_data.get("original_title"),  # Use original_title if title is missing
                release_date = movie_data.get("release_date"),
                origin_country = movie_data.get("origin_country"),
                original_language = movie_data.get("original_language"),
                production = [company["name"] for company in movie_data.get("production_companies", [])], # List of production companies
                director = director,
                writer = writers,
                casting = cast,
                length = movie_data.get("runtime"),
                vote_average = movie_data.get("vote_average"),
                description = movie_data.get("overview"),
                genre = [genre["name"] for genre in movie_data.get("genres", [])],
                budget = movie_data.get("budget"),
                revenue = movie_data.get("revenue"),
                tagline = movie_data.get("tagline"),
                # Metrics
                released = True if movie_data.get("status") == "Released" else False,
                vote_count = movie_data.get("vote_count"),
                popularity = movie_data.get("popularity"),
                # images
                image_poster = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get("poster_path") else None,
                banner_poster = f"https://image.tmdb.org/t/p/w1280{movie_data.get('backdrop_path')}" if movie_data.get("backdrop_path") else None,
        )

            return {
                'status': 'added', 
                'movie_id': movie.id, 
                'tmdb_id': movie.tmdb_id, 
                'title': movie.title,
                'message': 'Movie was successfully added to the DB.'
            }
        
    except Exception as e:
        # Catch any unexpected errors during the process
        return {
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }
