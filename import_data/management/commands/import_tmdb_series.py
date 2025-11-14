# import requests
import logging
import datetime
import time
import random
import os

from django.core.management.base import BaseCommand

from serie.models import Serie, Episode
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

    # set on max available pages with the corresponding endpoint of the TMDB Api.
    def get_max_page(self, endpoint):
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
        updated = 0
        start_time = time.time()

        endpoints = (
            "popular", "top_rated",
            "on_the_air", "discover",
            "airing_today"
            )

        def select_endpoint(endpoint):
            '''Takes a list of endpoints and return a random one'''
            return random.choice(endpoint)

        # retry feature if the url page brings error (eg. out of range).
        while retry < MAX_RETRIES:
            try:
                endpoint = select_endpoint(endpoints)

                today = datetime.date.today()
                # To get newest content  as extra in specs days------
                if today.day in [1, 5, 10, 15, 20, 25]:
                    page = random.randint(1, 4)
                else:
                    page = random.randint(1, self.get_max_page(endpoint)) # Randomly select a page

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
                # else:
                #     save_or_update_series(serie['id'])
                #     skipped_count += 1
                #     self.stdout.write(self.style.WARNING(
                #         f"{serie['name']} already exists in DB.\n"
                #         "Skipping....\n"
                #         f"\n" + "=" * 50 + "\n\n"
                #         ))

                # ------ Temporary when using Update on this.. to remove when pushing and uncomment above block -----
                # else:
                #  already exists, skip to next serie if updated_at is less than a week old
                # existing_serie = Serie.objects.get(tmdb_id=serie['id'])
                # time_difference = datetime.datetime.now(datetime.timezone.utc) - existing_serie.updated_at

                # print("time now:", datetime.datetime.now(datetime.timezone.utc))  # debug print
                # print("existing_serie.updated_at:", existing_serie.updated_at)  # debug print
                # print(f"Serie {serie['name']} exists. Last updated {time_difference.days} days ago.")  # debug print

                # if time_difference.days < 4:
                #     self.stdout.write(self.style.WARNING(
                #         f"{serie['name']} already exists in DB and was updated less than a week ago.\n"
                #         "Skipping....\n"
                #         f"\n" + "=" * 50 + "\n\n"
                #         ))
                #     skipped_count += 1
                #     continue
                # ------------------------------------------------

                # New version with time check. in progress...
                else:
                    existing_serie = Serie.objects.get(tmdb_id=serie['id'])
                    updated_at = existing_serie.updated_at.date()
                    updated_since = datetime.datetime.now(datetime.timezone.utc).date() - updated_at 
                    
                    last_ep_out = Episode.objects.filter(
                        season__serie=existing_serie,  # ← Follow relationship backwards
                        release_date__isnull=False      # ← Only episodes with release_date
                    ).order_by('-release_date').first()  # ← Get the most recent

                    if last_ep_out:
                        print(f"last_ep_out: {last_ep_out} -- {last_ep_out.release_date}")

                    # last_release = (
                    #     existing_serie.last_air_date
                    #     if existing_serie.last_air_date
                    #     else last_ep_out.release_date
                    # )
                    
                    print("- existing_serie was updated_at:", updated_at)  # debug print
                    print(f"- Serie {serie['id']} - {serie['name']} exists. Last updated {updated_since.days} days ago.")
                    print(f"- release on: {existing_serie.last_air_date}")

                    # last_ep_out = existing_serie.seasons.last().episodes.
                    # print(f"last_ep_out: {last_ep_out} -- {last_ep_out.season_number}")


                    is_released = False
                    is_update_after_release = False
                    is_recently_released = None


                    # check if release date is in the past
                    if existing_serie.last_air_date:
                        when_release =  datetime.date.today() - existing_serie.last_air_date
                        # print(f"\nhow long was the Serie released? -- {when_release.days} days ago\n")
                        if when_release.days < 0:
                            # Series is not released yet.
                            print(f"- Serie is not supposed to be released yet... In: '{when_release.days} days'")

                        else:
                            # Serie is already released.
                            print(f"- Serie supposed to be already released...  '{when_release.days} days'")
                            is_released = True
                            is_recently_released = True if when_release.days <= 40 else False
                            # check if updated_at is after release date
                            if updated_at >= existing_serie.last_air_date and updated_at.day != existing_serie.created_at.date():
                                is_update_after_release = True
                                print(f"- Serie was updated after the release date {updated_at}")  
                            else:
                                print(f"- Serie was updated before the release date {updated_at}") 

                    # set how long before a serie get updated again depending on certain conditons
                    # eg. when was it released? was it updated after release?
                    desired_updt_days = 14 # gives a minimum of 14 days before updating again
                    print(f"is_released, is_update_after_release, is_recently_released")
                    print(f"{is_released}, {is_update_after_release}, {is_recently_released}")

                    if is_released and is_update_after_release and is_recently_released:
                        desired_updt_days = 7  # Serie rencently released and updated already
                        print(f"3 conditions reunited, 7days before update.")

                    elif is_released and is_update_after_release and not is_recently_released:
                        desired_updt_days = 10 # Serie released since a while and updated already
                        # to modify or comment this condition if Db structure and import has changed,

                    elif is_released and not is_update_after_release and is_recently_released:
                        desired_updt_days = 3 # Serie recently released but not updated since release

                    # elif not is_released and when_release.days <= -30:
                    #     desired_updt_days = 5 # Serie not release but should release soon, so more info may be added
                    # else:
                    #     pass # probably does not have a last_air_date /  will remain to the standard update delay

                    if updated_since.days <= desired_updt_days:
                        # if time_difference.days < 14:
                        self.stdout.write(self.style.WARNING(
                            f"{serie['name']} already exists in DB and was updated less than {desired_updt_days} days ago.\n"
                            "Skipping....\n"
                            f"\n" + "=" * 50 + "\n\n"
                            ))
                        skipped_count += 1
                        continue

                    else:
                        # proceed to update the serie data
                        save_or_update_series(serie['id'])
                        updated += 1
                        self.stdout.write(self.style.WARNING(
                            f"{serie['name']} already exists in DB. but due for an update\n"
                            "Updated!....\n"
                            f"\n" + "=" * 50 + "\n\n"
                            ))
                # ---------------- END --------------------------

                # give some time between fetching new series.
                time.sleep(3) 

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))

        # Log and stream end of import summary
        logger.info(
            f"SUMMARY: Series (import)"
            f" -- {imported} Created -- {updated} Updated -- {skipped_count} Skipped/Failed"
            f" -- time: {elapsed_time:.2f} seconds"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Imported list of **{endpoint}** series done!\n"
            f"SUMMARY: Series (import) -- {imported} Created. "
            f"-- {updated} Updated. -- {skipped_count} Skipped/Failed."
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
