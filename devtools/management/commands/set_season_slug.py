from django.core.management.base import BaseCommand
from serie.models import Season
from django.utils.text import slugify
import time

class Command(BaseCommand):
    help = "Generate slugs for Seasons models based on their titles."

    # allow to run this function without saving into the database / for testing
    def add_arguments(self, parser):
        '''
        Custom arguments alowing to tweak around the command.\n
        *--dry-run* allow to run this function without saving into the database / for testing

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

        count= 0
        # seasons = Season.objects.filter(slug__isnull=True)
        seasons = Season.objects.only('id', 'season_number', 'name', 'slug').order_by("pk")
        total = seasons.count()
        
        self.stdout.write(f"Found {total} Seasons without slugs. Processing...")

        # loops through the movies in batches
        for start in range(0, total, batch_size):
            time.sleep(2)
            end = start + batch_size
            batch = seasons[start:end]
            updated_batch = []
            # to avoid overwhelming the database with too many requests at once
            self.stdout.write(f"Processing Seasons {start + 1} to {min(end, total)}...")

            used_slugs = set(Season.objects.values_list('slug', flat=True))

            for season in batch:
                if season.serie and (season.name is not None or slugify(f"{season.name}", allow_unicode=False) != ''):
                    base_slug = slugify(f"{season.serie.slug} {season.name}", allow_unicode=False)
                elif season.serie and season.name is None:
                    base_slug = slugify(f"{season.serie.slug} Season{season.season_number}", allow_unicode=False)

                slug = base_slug

                counter = 1
                while slug in used_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1 

                season.slug = slug
                updated_batch.append(season)
                used_slugs.add(slug)

            if updated_batch:
                if dry_run: # Run for test, does not save into the Database
                    self.stdout.write(self.style.SUCCESS(f"one example: {season} pk'{season.pk}' --> {season.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Seasons slugs.\n"))
                else:
                    # Save the new slugs in the dazabase
                    Season.objects.bulk_update(updated_batch, ['slug'])
                    self.stdout.write(self.style.SUCCESS(f"one example: {season} pk'{season.pk}' --> {season.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Seasons slugs.\n"))
                count += len(updated_batch)

            else:
                self.stdout.write(self.style.WARNING("⚠️ No season needed updating."))

        self.stdout.write(self.style.SUCCESS(f" {count} seasons have been processed for slug generation out of {total} seasons."))

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))