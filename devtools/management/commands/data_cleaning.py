from typing import Any
import time, datetime

from django.core.management.base import BaseCommand
from movie.models import Movie
# from serie.models import Serie


class Command(BaseCommand):
    help = 'Command script to clean data, removing entries with unsufficient data.'


    def add_arguments(self, parser):
        '''
        Custom arguments alowing to tweak around the command.\n
        **--dry-run** allow to run this function without saving into the database / for testing\n
        **--batch-size INT:** llow to decide on batch size as an argument when running the script
        '''
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the command without saving changes to the database."
        )

        # allow to decide on batch size as an argument when running the script
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,   # sensible default
            help="Number of rows to process per batch (default: 1000)",
        )


    def handle(self, *args: Any, **options: Any) -> str | None:
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        self.check_media_data_sufficient(dry_run, batch_size)


    def check_media_data_sufficient(self, dry_run, batch_size):
        '''
        Loop through Movies and Series and check if they have sufficient data or remove
        '''
        count = 0
        corrupt_count = 0
        start_time = time.time()

        movies = Movie.objects.all()
        total = movies.count()
        print(f"total movie to go through: {total}\n")

        print("The following movies miss too much data")
        # loops through the movies in batches
        for start in range(0, total, batch_size):
            time.sleep(1)
            end = start + batch_size
            batch = movies[start:end]

            for movie in batch:
                movie_pk = movie.pk
                count += 1
                check, result = self.pass_movie_in_check(movie)
                if check == False:
                    corrupt_count += 1
                    print(f"-{count}: -- film: {movie}-({movie_pk}), - Score: {check} - {result}/50\n")

                    if dry_run:
                        pass
                    else:
                        movie.delete()

            if corrupt_count >= 1:
                print(f"\n\n {corrupt_count} movies does not have enough data. Deleted!!")
            else:
                print(f"\n\n {corrupt_count} movies missing too much data.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))


    def pass_movie_in_check(self, movie):
        '''
        Check which fields are missing and return True or False depending on the score
        '''
        BASE_SCORE = 50 # if missing data, point are subtracted according to the priority set
        LOW = 1 # (11 fields), 
        MEDIUM = 2 # (8 fields), 
        HIGH = 4.5 # (5)

        today = datetime.date.today()
        is_valid = True

        if movie.release_date and movie.release_date > today:
            # print(f"Movie has a future release date: {movie.release_date}. ")
            MIN_REQUIRED_SCORE = 27
        else:
            # print(f"Movie already released or no release date found: {movie.release_date}. ")
            MIN_REQUIRED_SCORE = 30

        all_datas = {
            # high priority
            "title": {
                "value": bool(movie.title),
                "priority": HIGH,
            },
            "director": {
                "value": len(movie.director) > 0,
                "priority": HIGH,
            },
            "casting": {"value": len(movie.casting) > 0, "priority": HIGH},
            "poster_images": {
                "value": len(movie.poster_images) > 0,
                "priority": HIGH,
            },
            "release_date": {
                "value": bool(movie.release_date),
                "priority": HIGH,
            },
            # medium priority
            "genre": {
                "value": len(movie.genre) > 0,
                "priority": MEDIUM,
            },
            "production": {
                "value": len(movie.production) > 0,
                "priority": MEDIUM,
            },
            "banner_images": {
                "value": len(movie.banner_images) > 0,
                "priority": MEDIUM,
            },
            "trailers": {
                "value": movie.trailers is not None and len(movie.trailers) > 0,
                "priority": MEDIUM,
            },
            "writers": {
                "value": len(movie.writer) > 0,
                "priority": MEDIUM,
            },
            "length": {
                "value": movie.length is not None
                and movie.length > 0,
                "priority": MEDIUM,
            },
            "overview": {"value": bool(movie.overview), "priority": MEDIUM},
            "imdb_id": {"value": bool(movie.imdb_id), "priority": MEDIUM},
            # low priority
            "original_title": {
                "value": bool(movie.original_title),
                "priority": LOW,
            },
            "origin_country": {
                "value": movie.origin_country is not None and len(movie.origin_country) > 0,
                "priority": LOW,
            },
            "original_language": {
                "value": bool(movie.original_language) or len(movie.origin_language) > 0,
                "priority": LOW,
            },
            "vote_average": {
                "value": movie.vote_average is not None
                and (
                    type(movie.vote_average) == int
                    if movie.release_date and movie.release_date > today
                    else movie.vote_average > 0
                ),
                "priority": LOW,
            },
            "budget": {
                "value": movie.budget is not None
                and (
                    type(movie.budget) == int
                    if movie.release_date and movie.release_date > today
                    else movie.budget > 0
                ),
                "priority": LOW,
            },
            "revenue": {
                "value": movie.revenue is not None
                and (
                    type(movie.revenue) == int
                    if movie.release_date and movie.release_date > today
                    else movie.revenue > 0
                ),
                "priority": LOW,
            },
            "status": {"value": bool(movie.status), "priority": LOW},
            "tagline": {"value": bool(movie.tagline), "priority": LOW},
            "spoken_languages": {
                "value": movie.spoken_languages is not None and len(movie.spoken_languages) > 0,
                "priority": LOW,
            },
            # "released": {"value": movie_data.get("status") == "Released", "priority": low},
            "vote_count": {
                "value": movie.vote_count is not None
                and (
                    type(movie.vote_count) == int
                    if movie.release_date and movie.release_date > today
                    else movie.vote_count > 0
                ),
                "priority": LOW,
            },
            "popularity": {
                "value": movie.popularity is not None
                and (
                    type(movie.popularity) == float
                    if movie.release_date and movie.release_date > today
                    else movie.popularity > 0
                ),
                "priority": LOW,
            },
        }

        # loop through processed fields, check how many fields are missing
        # and how much point taken out per priority
        missing_fields = [field for field, data in all_datas.items() if not data['value']]

        result = 0
        score = [data['priority'] for field, data in all_datas.items() if not data['value']]
        for s in score:
            result += s


        if BASE_SCORE - result <= MIN_REQUIRED_SCORE:
        # if BASE_SCORE - result == MIN_REQUIRED_SCORE:
            # print(f" Too many missing fields! BREAK! No import. -- score: {BASE_SCORE - result}/{BASE_SCORE}")
            is_valid = False
            print(
                f"-- missing fields: {len(missing_fields)}, {missing_fields}.\n"
                f"-- missing score: {result} -- {score}"
            )

        return is_valid, BASE_SCORE - result