# import requests
import logging
import time
import random
import os
from django.core.management.base import BaseCommand


from serie.models import Serie
from import_data.api_services.TMDB.fetch_series import get_series_list
from import_data.services import save_or_update_series

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
    help = 'Import series data from TMDB'

    def handle(self, *args, **kwargs):
        self.import_list_series()

    def import_list_series(self):
        """
        Bulk import strategy:
        1. Fetch a list of series varying upon on the selected endpoint
        2.  loop through each serie to query their data 
        3. Check if the series already exists otherwise saves it in the database.
        """

        endpoint = ("popular", "top_rated", "on_the_air")
        selected_endpoint = random.choice(endpoint)

        imported_count = 0  # Tracks how many movies were imported
        skipped_count = 0  # Tracks how many movies already existed
        serie_count = 0

        # Define the range of pages to fetch
        # set on max available with the corresponding query of TMDB
        if  selected_endpoint == "on_the_air":
            max_pages = 50
        elif  selected_endpoint == "top_rated":
            max_pages = 100
        else:
            max_pages = 500
            # logger.info(f"Fetching series from '{selected_endpoint}' endpoint")  # debug print

        # page = random.sample(range(1, max_pages + 1), 1)  # Randomly select a page
        page = random.randint(1, max_pages)  # Randomly select a page

        try:
            self.stdout.write(f"Fetching series from '{selected_endpoint}' list, With page n: {page}\n") # debug print
            list_series = get_series_list(page, selected_endpoint)

            if not list_series:
                self.stdout.write(self.style.ERROR(f"No serie page found... Check the url for possible error (or outside range)."))

            self.stdout.write("Processing the list of series to get the series datas.\n")
            for new_serie in list_series['results']:
                tmdb_id = new_serie['id']
                #------- temporary break here after 4 series to check feature is going well with adding episode--------
                if serie_count >= 5:
                    self.stdout.write(f"Breaking after 5 series for testing purpose.\n")
                    break
                serie_count += 1

                # tmdb_title = new_serie['title']
                self.stdout.write(f"-----") # debug print
                self.stdout.write(f"Importing *Serie {serie_count} of {len(list_series['results'])}* (id: {tmdb_id})") # debug print

                # Check if serie exists
                if not Serie.objects.filter(tmdb_id=tmdb_id).exists():
                    try:
                        save_or_update_series(tmdb_id)
                        imported_count += 1
                        self.stdout.write(f"Imported serie: {new_serie['name']}\n")  # not sure it is imported if already exist
                        self.stdout.write("-----------")  # not sure it is imported if already exist
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error importing {new_serie['name']}: {e}\n"))
                else:
                    self.stdout.write(self.style.WARNING(f"{new_serie['name']} already exists in DB.\n"))
                    skipped_count += 1

                # give some time between fetching a new serie.
                time.sleep(3) 

            self.stdout.write(self.style.SUCCESS(f"Imported list of **{selected_endpoint}** series done!\n"))
            logger.info(f"SUMMARY: {imported_count} series imported, {skipped_count} series skipped.")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f" error :{e}"))



# ------ To import a single serie ---- Not in use.
# def import_serie(request, tmdb_id):
#     '''Import a movie in making a request to TMDB api and store it in the database'''
#     print(f"request importing a new serie")
#     try:
#         if request.method == 'GET' and request.user.is_superuser:

#             try:
#                 # check if the movie is already in our database
#                 exisiting_serie = Serie.objects.get(tmdb_id=tmdb_id)
#                 print(f"Serie already exists: serie {exisiting_serie.id}: {exisiting_serie.title}")
#                 return JsonResponse({
#                     'status': 'already exists in DB', 
#                     'tmdb_id': exisiting_serie.tmdb_id, 
#                     'serie_id': exisiting_serie.id,
#                     'title': exisiting_serie.title
#                 }, status=200)
            
#             # if the movie is not then we try to fetch it.
#             except Serie.DoesNotExist:

#                 result = add_series_from_tmdb(tmdb_id)

#                 # Determine appropriate HTTP status code
#                 status_code = {
#                     'added': 201,
#                     'exists': 200,
#                     'error': 404
#                 }.get(result['status'], 400)

#                 return JsonResponse(result, status=status_code)
#         else:
#             print(f"Unauthorized access to 'import_serie' page.")
#             messages.error(request, "You are not authorized to import series")
#             return redirect('main:home')

#     except Exception as e:
#         messages.error(request, "the page seem to experience some issue, please try again later")
#         print(f" error :{e}")
#         return JsonResponse({
#             'status': 'error',
#             'message': 'An unexpected error occurred'
#         }, status=500)
