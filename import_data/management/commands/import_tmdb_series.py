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
from import_data.tools.media_update_check import check_update_since
from import_data.tools.build_endpoint_import import get_page


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
        2. loop through each serie to query their data 
        3. call: loop through each movie from the TMDB Id provided to query their data
        4. Check if the series already exists otherwise saves it in the database.
        5. Log result for created, updated and skipped.
        """
        # instantiate variable to keep track of import and retry policy
        MAX_RETRIES = 3
        retry = 0
        start_time = time.time()

        imported = {
            'count' : 0,
            'created' : 0,
            'skipped' : 0,
            'updated' : 0,
            'runtime': 0.0
        }

        endpoints = (
            "popular", "top_rated",
            "on_the_air", "discover",
            "airing_today"
            )

        # retry feature if the url page brings error (eg. out of range).
        while retry < MAX_RETRIES:
            endpoint = random.choice(endpoints)

            page = get_page(endpoint)

            self.stdout.write(
                f"Fetching series from '{endpoint}' list, With page n: {page}"
                ) # debug print
            
            try:
                list_series = get_api_data(
                    page=page,
                    endpoint=endpoint,
                    t_type='tv'
                    # update = False
                    )

                if not list_series or len(list_series['results']) <= 5:
                    raise ValueError("No series list found or too few results.")

                self.stdout.write(
                    f"Processing the list of series."
                    f"\n" + "=" * 50 + "\n\n"
                )

                batch = self.process_serie_list(list_series, imported, start_time)
                imported = batch
                break # if list_series exist then break out of the Loop

            except ValueError as value_e:
                retry += 1
                self.stdout.write(
                    f"(ValueError Exception) No series list found or too few results. "
                    f"page={page}, endpoint={endpoint}."
                    f"\nError: {value_e}"
                    )
                time.sleep(retry*4)  # wait for 4 second*num attempts before retrying

            except Exception as e:
                retry += 1
                self.stdout.write(
                    f"(Exception) Error getting series"
                    f"page={page}, endpoint={endpoint}. \nError: {e}\n"
                    )
                self.stdout.write(self.style.WARNING(
                    f"Retrying... Attempt {retry}/{MAX_RETRIES} in {retry*4}seconds"
                    ))
                time.sleep(retry*4)

        # If all retries failed, exit early
        if retry == MAX_RETRIES:
            self.stdout.write(self.style.ERROR(
                "Max retries reached. Could not fetch imported series. -- Task ending."
                ))
            return 

        end_time = time.time()
        elapsed_time = end_time - start_time

        imported['runtime'] = round(elapsed_time, 2)

        log_import = (            
            f"SUMMARY: Series (import)"
            f" -- {imported['created']} Created"
            f" -- {imported['updated']} updated"
            f" -- {imported['skipped']}  Skipped/Failed"
            f" -- runtime: {imported['runtime']} seconds"
            )

        # saved log in file report import.
        logger.info(log_import)
        self.stdout.write(self.style.SUCCESS(log_import))


    def process_serie_list(self, list_series, imported: dict, start_time):
        '''
        Process a batch of series from TMDB api response.\n
        return the count of imported/saved and skipped items
        - count, created, updated, skipped
        '''
        imported = imported

        for serie in list_series['results']:
            # ------- break here after 4 series so the Task does not run too long. --------
            # test check with timing. If over 15sec
            check_time = time.time()
            elapsed_time =  check_time - start_time

            if elapsed_time > 12.0:
                self.stdout.write(f"Breaking after {imported['count']} series.\n")
                break

            imported["count"] += 1

            self.stdout.write(f"-------")  # debug print
            self.stdout.write(
                f"Importing *Serie {imported["count"]} (id: {serie['id']})"
            )  # debug print

            # Check if serie exists
            if not Serie.objects.filter(tmdb_id=serie['id']).exists():
                time.sleep(0.5)

                try:
                    new_serie, is_created = save_or_update_series(serie['id'])
                    if new_serie:
                        imported['created'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Imported serie: {serie['name']}\n"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )
                    else:
                        imported['skipped'] += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Cancel to import serie: {serie['name']}. No data returned\n"
                                "Skipping....\n"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        f"Error importing {serie['id']} "
                        f"- {serie['name']}: {e}"
                    )
                    imported["skipped"] += 1
                    continue

            else:
                # if the serie already exist, check when it was released and updated
                # and if it necessit a new update
                # Reduces unnecessary api calls if serie was recently updated in DB
                exist_serie = Serie.objects.get(tmdb_id=serie['id'])
                need_update, desired_updt_days = check_update_since(exist_serie, "Serie")

                if need_update == False:
                    # if time_difference.days < 14:
                    self.stdout.write(self.style.WARNING(
                        f"{serie['name']} already exists in DB "
                        f"and was updated less than {desired_updt_days} days ago.\n"
                        "-- Skipping....\n"
                        f"\n" + "=" * 50 + "\n\n"
                        ))
                    imported['skipped'] += 1
                    continue

                else:
                    # proceed to update the serie's object data
                    time.sleep(0.5)
                    self.stdout.write(
                        self.style.WARNING(
                            f"'{serie['name']}' already exists in DB. "
                            f"-- Min-delay update of {desired_updt_days} days passed. "
                            f"-- Updating!\n"
                        )
                    )
                    new_serie, is_created = save_or_update_series(serie['id'])

                    if new_serie and not is_created:
                        imported['updated'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated  serie: **{new_serie}**"
                                f"\n" + "=" * 50 + "\n\n"
                            ))

                    elif not new_serie:
                        imported['skipped'] += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"**Cancel to save in DB. "
                                f"No serie or no sufficient data. Probably deleted. **"
                                f"\n" + "=" * 50 + "\n\n"
                            )
                        )

        return imported


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
