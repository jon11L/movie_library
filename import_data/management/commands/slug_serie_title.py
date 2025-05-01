from django.core.management.base import BaseCommand
from serie.models import Serie
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Generate slugs for Serie models based on their titles."

    def handle(self, *args, **options):
        count= 0

        series = Serie.objects.filter(slug__isnull=True)
        updated_series = []
        total = series.count()

        self.stdout.write(f"Found {total} Series without slugs. Processing...")

        for serie in series:
            count += 1
            if serie.title:
                base_slug = slugify(serie.title)
                slug = base_slug
                counter = 1

                # make sure it's unique
                while Serie.objects.filter(slug=slug).exclude(pk=serie.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                serie.slug = slug
                updated_series.append(serie)

        if updated_series:
            Serie.objects.bulk_update(updated_series, ['slug'])
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_series)} Series slugs."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No Serie needed updating."))


                # season.save()
                # # self.stdout.write(self.style.SUCCESS(f"Slug generated for movie: {movie.title} -- ID: {movie.id} -- Slug: {movie.slug}"))
                # self.stdout.write(self.style.SUCCESS(f"Slug generated for serie: {season.title} -- ID: {season.id} -- Slug: {season.slug}"))

        print(f"Done! Populated slugs for {series.count()} Series.")

        self.stdout.write(self.style.SUCCESS(f" {count} Series have been processed for slug generation."))