from django.core.management.base import BaseCommand
from serie.models import Episode
from django.utils.text import slugify

import time

class Command(BaseCommand):
    help = "Generate slugs for Episode models based on the Serie, title, E.number and Season.num"

    def handle(self, *args, **options):
        start_time = time.time()
        count= 0

        episodes = Episode.objects.filter(slug__isnull=True)
        updated_episodes = []
        total = episodes.count()

        if total == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("✅ All episodes already have slugs. No action needed.")
            self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))
            return

        self.stdout.write(f"Found {total} Episodes without slugs. Processing...")

        for episode in episodes:
            count += 1
            if episode.season and episode.title:
                base_slug = slugify(f"{episode.season.serie.slug} S{episode.season.season_number} E{episode.episode_number} {episode.title}")
                slug = base_slug
                counter = 1

                # make sure it's unique // Check both database and pending unsaved slugs
                while Episode.objects.filter(slug=slug).exclude(pk=episode.pk).exists() or \
                        any(ep.slug == slug for ep in updated_episodes):
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                episode.slug = slug
                updated_episodes.append(episode)

        if updated_episodes:
            Episode.objects.bulk_update(updated_episodes, ['slug'])
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_episodes)} Episodes slugs."))
            
        else:
            self.stdout.write(self.style.WARNING("⚠️ No Episodes needed updating."))

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"time: {elapsed_time:.2f} seconds."))
        print(f"Done! Populated slugs for {episodes.count()} Episodes.")
                
        self.stdout.write(self.style.SUCCESS(f" {count} Episodes have been processed for slug generation."))