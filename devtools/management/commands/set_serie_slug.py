from django.core.management.base import BaseCommand
from serie.models import Serie
from django.utils.text import slugify
from uuid import uuid4
import time

import time
class Command(BaseCommand):
    help = "Generate slugs for Serie models based on their titles " \
    "and their first release year."

    def add_arguments(self, parser):
        '''
        Custom arguments alowing to tweak around the command.\n
        **--dry-run** allow to run this function without saving into the database / for testing\n
        **--batch-size INT:** llow to decide on batch size as an argument when running the script
        '''
        # allow to run this function without saving into the database / for testing
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

        count= 0 # tracks how many series get Slug updated.

        # series = list(Serie.objects.all())
        series = list(Serie.objects.only('id', 'title', 'first_air_date', 'slug').order_by('pk'))
        total = len(series)

        self.stdout.write(f"Found {total} Series without slugs. Processing...")
        
        # loops through the series in batches
        for start in range(0, total, batch_size):
            time.sleep(2)
            end = start + batch_size
            batch = series[start:end]
            updated_batch = []
            # to avoid overwhelming the database with too many requests at once
            self.stdout.write(f"Processing Series {start + 1} to {min(end, total)}...")

            # new_slugs = set()
            used_slugs = set(Serie.objects.values_list('slug', flat=True))
            # instead create an empty list store the new slugs as we re set them.

            # loops through each movie in the current batch
            for serie in batch:
                year = None
                slug = None
                title = None
                short = uuid4().hex[:6]  # will add a random id make it more unique

                # Generate a base slug from the title and release date if available
                if serie.first_air_date is not None:
                    year = serie.first_air_date.year
                else:
                    year = ''
                    
                if serie.title is None or slugify(serie.title, allow_unicode=False) == '':
                    title = 'untitled'
                else:
                    title = serie.title
                    
                # if year and serie.title is not None:
                base_slug = slugify(f"{title}-{year}-{short}", allow_unicode=False)
                # else:
                #     base_slug = slugify(f"{title}-{short}", allow_unicode=True)

                slug = base_slug
                # make sure it's unique, 'counter' appends to slug if slugs exist
                # while Serie.objects.filter(slug=slug).exclude(pk=serie.pk).exists():
                counter = 1 
                while slug in used_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                if serie.slug != slug:
                    serie.slug = slug
                    updated_batch.append(serie)
                    used_slugs.add(slug)

            if updated_batch:
                if dry_run: # Run for test, does not save into the Database
                    self.stdout.write(self.style.SUCCESS(f"(Dry run) one example: {serie} pk'{serie.pk}': {serie.title} --> {serie.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Series slugs in this batch.\n"))
                else:
                    Serie.objects.bulk_update(updated_batch, ['slug'])
                    self.stdout.write(self.style.SUCCESS(f"one example: {serie} pk'{serie.pk}': {serie.title} --> {serie.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Series slugs in this batch.\n"))
                count += len(updated_batch)

            else:
                self.stdout.write(self.style.WARNING("⚠️ No Serie needed updating."))

        self.stdout.write(self.style.SUCCESS(f" {count} Series have been processed for slug generation out of {total}."))

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))