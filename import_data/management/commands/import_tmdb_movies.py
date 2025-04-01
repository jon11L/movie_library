# import requests
import logging
import time
import random
import os

from django.core.management.base import BaseCommand

from movie.models import Movie
from import_data.api_services.TMDB.fetch_movies import get_movie_list
from import_data.services import save_or_update_movie


# Configure Logging
logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists

LOG_FILE = os.path.join(LOG_DIR, "tmdb_import.log")


logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",  # Append to existing log file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class Command(BaseCommand):
    help = 'Import movies from TMDB'

    def handle(self, *args, **kwargs):
        self.import_movies()

    def import_movies(self):
        """
        Bulk import strategy:
        1. Fetch a list of movies varying upon on the selected endpoint
        2.  loop through each movie to query their data 
        3. Check if the movies already exists otherwise saves it in the database.
        """

        endpoint = ("popular", "top_rated", "now_playing", "upcoming")

        selected_endpoint = random.choice(endpoint)
        if selected_endpoint == "now_playing":
            max_pages = 200
        elif  selected_endpoint == "upcoming":
            max_pages = 50
        else:
            max_pages = 500  # Define the range of pages to fetch

        pages_to_fetch = random.sample(range(1, max_pages + 1), 5)  # Randomly select 5 pages

        # Track the number of movies imported and skipped
        created = 0
        imported_count = 0  # Tracks how many movies were imported
        skipped_count = 0  # Tracks how many movies already existed

        try:
            # Loop pages 
            for page in pages_to_fetch:
                self.stdout.write(f"----------------------------") # debug print
                self.stdout.write(f"Fetching movies from '{selected_endpoint}' list, With page n: {page}\n") # debug print
                list_movies = get_movie_list(page, selected_endpoint)

                if not list_movies:
                    self.stdout.write(self.style.ERROR(f"No movie list found... Check the url for possible error (or outside range)."))
                    continue  # Skip this page if no movies are found

                # Fetch and process each movie from the selected endpoint
                self.stdout.write("Processing the list of movies and pass the Ids to get the datas.\n")
                for movie in list_movies['results']:
                    imported_count += 1
                    movie_id = movie['id']
                    movie_title = movie['title']
                    adult = movie['adult']  
                    self.stdout.write(f"passing movie {imported_count} in {len(list_movies['results']*5)}")
                    self.stdout.write(f"Importing Movie title: {movie_title} (ID: {movie_id})\n") # debug print

                    if adult:
                        self.stdout.write(self.style.WARNING(f"Movie {movie_id} is marked as adult content. Skipping..."))
                        skipped_count += 1
                        continue

                    # Check if movie exists
                    if not Movie.objects.filter(tmdb_id=movie_id).exists():
                        try:
                            save_or_update_movie(movie_id)
                            created += 1
                            # self.stdout.write(self.style.SUCCESS(f"Imported movie: **{new_movie['title']}** \n"))  # not sure it is imported if already exist
                            # logger.info(f"Imported: {movie_title} (ID: {movie_id})")
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error importing {movie['title']}: {e}"))
                            skipped_count += 1

                            # logger.error(f"Error importing {movie_title}: {e}")
                    else:
                        self.stdout.write(self.style.WARNING(f"'{movie['title']}' already exists in DB."))
                        print("-----------")
                        skipped_count += 1
                        # logger.info(f"Skipped (Already in DB): {movie_title}")

                time.sleep(5) # give some time between fetching a new page list of movies.
            self.stdout.write(self.style.SUCCESS(f"Import of movies successfully completed: {imported_count} New, {skipped_count} Skipped.\n"))
            logger.info(f"SUMMARY: {created} movies added -- {skipped_count}  skipped.")

        except Exception as e:
            # messages.error(request, "the page seem to experience some issue, please try again later")
            self.stdout.write(self.style.WARNING(f" error :{e}"))


# ------ To import a single movie ---- NOT in use.

# def import_movie(request, tmdb_id):
#     '''Import a movie in making a request to TMDB api and store it in the database'''
#     print(f"request importing a new movie")
#     try:
#         if request.method == 'GET' and request.user.is_superuser:

#             try:
#                 # check if the movie is already in our database
#                 exisiting_movie = Movie.objects.get(tmdb_id=tmdb_id)
#                 print(f"Movie already exists: movie {exisiting_movie.id}: {exisiting_movie.title}")
#                 return JsonResponse({
#                     'status': 'already exists in DB', 
#                     'tmdb_id': exisiting_movie.tmdb_id, 
#                     'movie_id': exisiting_movie.id,
#                     'title': exisiting_movie.title
#                 }, status=200)
            
#             # if the movie is not then we try to fetch it.
#             except Movie.DoesNotExist:
#                 result = add_movies_from_tmdb(tmdb_id)

#                 # Determine appropriate HTTP status code
#                 status_code = {
#                     'added': 201,
#                     'exists': 200,
#                     'error': 404
#                 }.get(result['status'], 400)

#                 return JsonResponse(result, status=status_code)

#         else:
#             print(f"Unauthorized access to 'import_movie' page.")
#             messages.error(request, "You are not authorized to import movies")
#             return redirect('main:home')
        
#     except Exception as e:
#         messages.error(request, "the page seem to experience some issue, please try again later")
#         print(f" error :{e}")
#         # return JsonResponse()
#         return JsonResponse({
#             'status': 'error',
#             'message': 'An unexpected error occurred'
#         }, status=500)


