# import requests
import logging
import datetime
import time
import random
import os

from django.core.management.base import BaseCommand

from serie.models import Serie
# from import_data.api_clients.TMDB.fetch_series import get_serie_data
from import_data.api_clients.TMDB.fetch_data import get_api_data
from import_data.services.create_series import save_or_update_series


# Configure Logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists
LOG_FILE = os.path.join(LOG_DIR, "tmdb_import.log")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Create a logger instance for this module
logger = logging.getLogger(__name__)

# Create a FileHandler and attach it to the logger
file_handler = logging.FileHandler(LOG_FILE, mode="a")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Prevent duplicate logs (avoid propagation to the root logger)
logger.propagate = False


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
        # instantiate variable to keep track of import and retry policy
        MAX_RETRIES = 3
        retry = 0
        count = 0  # Tracks how many series were imported
        skipped_count = 0  # Tracks how many series already existed
        imported = 0
        start_time = time.time()

        endpoints = (
            "popular", "top_rated",
            "on_the_air", "discover",
            "airing_today"
            )

        def select_endpoint(endpoint):
            '''Takes a list of endpoints and return a random one'''
            return random.choice(endpoint)

        # set on max available pages with the corresponding endpoint of the TMDB Api.
        def get_max_page(endpoint):
            ''' Return the max amount of pages available in the TMDB api 
            according to the endpoint selected.
            '''
            if  endpoint == "on_the_air":
                return  50
            elif  endpoint == "top_rated":
                return 100
            elif endpoint == "airing_today":
                return 12 # this endpoint pages number seem to change regularly
            else:
                return 500

        # retry feature if the url page brings error (eg. out of range).
        while retry < MAX_RETRIES:
            try:
                endpoint = select_endpoint(endpoints)

                today = datetime.date.today()
                # To get newest content  as extra in specs days------
                if today.day in [1, 5, 10, 15, 20, 25]:
                    page = random.randint(1, 4)
                else:
                    page = random.randint(1, get_max_page(endpoint)) # Randomly select a page

                self.stdout.write(
                    f"Fetching series from '{endpoint}' list, With page n: {page}"
                    ) # debug print

                list_series = get_api_data(
                    page=page,
                    endpoint=endpoint,
                    t_type='tv'
                    # update = False
                    )

                if not list_series or len(list_series['results']) <= 5:
                    raise ValueError("No series list found or too few results.")

                break # if list_series exist then break out of the Loop

            except ValueError as value_e:
                retry += 1
                self.stdout.write(
                    f"(Exception) No series list found or too few results. page={page}, endpoint={endpoint}."
                    f"Error: {value_e}"
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                    )
                time.sleep(retry*4)  # wait for 4 second *numbered attempts before retrying (2nd try 8 seconds, 3rd try 12 seconds)

            except Exception as e:
                self.stdout.write(
                    f"(Exception) Error getting updated series"
                    f"page={page}, endpoint={endpoint}. \nError: {e}\n"
                    )
                retry += 1
                self.stdout.write(self.style.WARNING(
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                    ))
                time.sleep(retry*4)  # wait for 4 second *numbered attempts before retrying (2nd try 8 seconds, 3rd try 12 seconds)

        # If all retries failed, exit early
        if retry == MAX_RETRIES:
            self.stdout.write(self.style.ERROR(
                "Max retries reached. Could not fetch imported series. -- Task ending."
                ))
            return 

        if list_series != None:
            # give some random to index to look through for the series list.
            r_index = random.randint(0, len(list_series['results']) - 5) 
            print(f"Random index for series list: {r_index}")

            self.stdout.write(f"Processing the list of series to get the individual serie's data.")
            for serie in list_series['results'][r_index:r_index+5]:
                count += 1

                # ------- temporary break here after 5 series to check feature is going well with adding episode--------
                if count > 5:
                    self.stdout.write(f"Breaking after 5 series for testing purpose.\n")
                    break

                self.stdout.write(f"-------")  # debug print
                self.stdout.write(
                    f"Importing *Serie {count} (id: {serie['id']})"
                )  # debug print

                # Check if serie exists
                if not Serie.objects.filter(tmdb_id=serie['id']).exists():
                    try:
                        new_serie, is_created = save_or_update_series(serie['id'])
                        if new_serie:
                            imported += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Imported serie: {serie['name']}\n"
                                    f"\n" + "=" * 50 + "\n\n"
                                )
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Cancel to import serie: {serie['name']}. No data returned\n"
                                    "Skipping....\n"
                                    f"\n" + "=" * 50 + "\n\n"
                                )
                            )

                    except Exception as e:
                        self.stdout.write(f"Error importing {serie['id']}- {serie['name']}: {e}")
                        skipped_count += 1
                        continue
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f"{serie['name']} already exists in DB.\n"
                        "Skipping....\n"
                        f"\n" + "=" * 50 + "\n\n"
                        ))

                # give some time between fetching new series.
                time.sleep(3) 

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))

        # Log and stream end of import summary
        logger.info(
            f"SUMMARY: Series (import)"
            f" -- {imported} Created -- 0 Updated -- {skipped_count} Skipped/Failed"
            f" -- time: {elapsed_time:.2f} seconds"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Imported list of **{endpoint}** series done!\n"
            f"SUMMARY: Series (import) -- {imported} Created. "
            f"-- 0 Updated. -- {skipped_count} Skipped/Failed."
            f"\n" + "=" * 50 + "\n\n"

            ))


# ------ To import a single serie ---- // NOT IN USE. //
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
