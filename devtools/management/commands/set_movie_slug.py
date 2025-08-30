from django.core.management.base import BaseCommand
from movie.models import Movie
from django.utils.text import slugify
import time
from uuid import uuid4


class Command(BaseCommand):
    help = "Generate slugs for Movies models based on their titles." \
    "and their first release year."


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


    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        start_time = time.time()

        count= 0 # tracks how many movies get Slug updated.

        movies = list(Movie.objects.all())
        # movies = list(Movie.objects.only("pk", "title", "release_date"))
        total = len(movies)

        self.stdout.write(f"Found {total} Movies. Processing...")
        
        # loops through the movies in batches
        for start in range(0, total, batch_size):
            end = start + batch_size
            batch = movies[start:end]
            updated_batch = []
            # to avoid overwhelming the database with too many requests at once
            time.sleep(2)

            used_slugs = set(Movie.objects.values_list('slug', flat=True))
            self.stdout.write(f"Processing Movies {start + 1} to {min(end, total)}...")

            # loops through each movie in the current batch
            for movie in batch:
                year = None
                title = None
                slug = None 
                short = uuid4().hex[:6]  # will add a random id make it more unique

                # Generate the base for slug with the title and release date if available
                if  movie.title is None or slugify(movie.title, allow_unicode=False) == '':
                    title = 'untitled'
                else:
                    title = movie.title
                
                if movie.release_date is not None:
                    year = movie.release_date.year
                else:
                    year= ''

                base_slug = slugify(f"{movie.title} {year} {short}", allow_unicode=False)
                slug = base_slug

                # counter loop make sure the slug is unique
                # while Movie.objects.filter(slug=slug).exclude(pk=movie.pk).exists():
                counter = 1
                while slug in used_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                if movie.slug != slug:
                    movie.slug = slug
                    updated_batch.append(movie)
                    used_slugs.add(slug)

            if updated_batch:
                if dry_run:
                    self.stdout.write(self.style.SUCCESS(f"(Dry run) one example: {movie} pk'{movie.pk}': {movie.title} --> {movie.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Series slugs in this batch.\n"))
                else:
                    Movie.objects.bulk_update(updated_batch, ['slug'])
                    self.stdout.write(self.style.SUCCESS(f"one example: {movie} pk'{movie.pk}': {movie.title} --> {movie.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Movies slugs in this batch.\n"))
                count += len(updated_batch)
            else:
                self.stdout.write(self.style.WARNING("⚠️ No Movies needed updating."))

        self.stdout.write(self.style.SUCCESS(f" {count} movies have been processed for slug generation."))

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))