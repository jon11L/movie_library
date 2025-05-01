from django.core.management.base import BaseCommand
from movie.models import Movie
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Generate slugs for Movies models based on their titles."

    def handle(self, *args, **options):
        count= 0

        movies = Movie.objects.filter(slug__isnull=True)
        updated_movies = []
        total = movies.count()

        self.stdout.write(f"Found {total} Movies without slugs. Processing...")

        for movie in movies:
            count += 1
            if movie.title:
                base_slug = slugify(movie.title)
                slug = base_slug
                counter = 1

                # make sure it's unique
                while Movie.objects.filter(slug=slug).exclude(pk=movie.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                movie.slug = slug
                updated_movies.append(movie)

        if updated_movies:
            Movie.objects.bulk_update(updated_movies, ['slug'])
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(updated_movies)} Movies slugs."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No Movies needed updating."))

                # season.save()
                # # self.stdout.write(self.style.SUCCESS(f"Slug generated for movie: {movie.title} -- ID: {movie.id} -- Slug: {movie.slug}"))
                # self.stdout.write(self.style.SUCCESS(f"Slug generated for serie: {season.title} -- ID: {season.id} -- Slug: {season.slug}"))

        print(f"Done! Populated slugs for {movies.count()} movies.")

        self.stdout.write(self.style.SUCCESS(f" {count} movies have been processed for slug generation."))