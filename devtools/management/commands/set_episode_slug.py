from django.core.management.base import BaseCommand
from serie.models import Episode
from django.utils.text import slugify

import time

class Command(BaseCommand):
    help = "Generate slugs for Episode models based on the Serie slug, title, E.number and Season.num"

    def add_arguments(self, parser):
        
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
        start_time = time.time()
        count= 0
        batch_size = options["batch_size"]

        # episodes = Episode.objects.filter(slug__isnull=True)
        episodes = Episode.objects.only('id', 'title', 'episode_number').order_by('pk')

        updated_batch = []
        total = episodes.count()

        if total == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("✅ All episodes already have slugs. No action needed.")
            self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))
            return

        self.stdout.write(f"Found {total} Episodes without slugs. Processing...")

        for start in range(0, total, batch_size):
            end = start + batch_size
            batch = episodes[start:end]
            updated_batch = []

            used_slugs = set(Episode.objects.values_list('slug', flat=True))
            self.stdout.write(f"Processing episode {start + 1} to {min(end, total)}...")

            for ep in batch:
                # count += 1
                if ep.season and ep.title:
                    base_slug = slugify(
                        f"{ep.season.serie.slug} S{ep.season.season_number}E{ep.episode_number} {ep.title}",
                        allow_unicode=False
                        )
                slug = base_slug
                # make sure it's unique // Check both database and pending unsaved slugs

                counter = 1
                while slug in used_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                if ep.slug != slug:
                    ep.slug = slug
                    updated_batch.append(ep)
                    used_slugs.add(slug)

            if updated_batch:
                
                if dry_run: # Run for test, does not save into the Database
                    self.stdout.write(self.style.SUCCESS(f"(Dry run)  one example: {ep.season.serie} {ep.season}-E{ep}: {ep.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Episodes slugs.\n"))

                else:
                    Episode.objects.bulk_update(updated_batch, ['slug'])
                    self.stdout.write(self.style.SUCCESS(f"one new slug example: {ep.season.serie} {ep.season}-E{ep}: {ep.slug}."))
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_batch)} Episodes slugs.\n"))
                count += len(updated_batch)
            
            else:
                self.stdout.write(self.style.WARNING("⚠️ No Episodes needed updating."))

        self.stdout.write(self.style.SUCCESS(f"Operation finished! {count} Episodes have been processed for slug generation out of {total} episodes."))
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))