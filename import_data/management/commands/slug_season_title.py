from django.core.management.base import BaseCommand
from serie.models import Season
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Generate slugs for Seasons models based on their titles."

    def handle(self, *args, **options):
        count= 0

        seasons = Season.objects.filter(slug__isnull=True)
        updated_seasons = []
        total = seasons.count()
        
        self.stdout.write(f"Found {total} Seasons without slugs. Processing...")

        for season in seasons:
            print(season.serie.title, season.name)
            count += 1
            # if season.title:
            if season.serie and season.name:
                base_slug = slugify(f"{season.serie.title} {season.name}")
                slug = base_slug
                counter = 1

                # make sure it's unique
                while Season.objects.filter(slug=slug).exclude(pk=season.pk).exists() or \
                        any(s.slug == slug for s in updated_seasons):
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                season.slug = slug
                updated_seasons.append(season)

        if updated_seasons:
            Season.objects.bulk_update(updated_seasons, ['slug'])
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_seasons)} Seasons slugs."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No season needed updating."))

        print(f"Done! Populated slugs for {seasons.count()} seasons.")
        self.stdout.write(self.style.SUCCESS(f" {count} seasons have been processed for slug generation."))