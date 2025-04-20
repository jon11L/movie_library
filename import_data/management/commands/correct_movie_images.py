from django.core.management.base import BaseCommand
from movie.models import Movie
import time

# Fix movies where the 'image' field banner_poster and image_poster are incorrectly stored
#  with the preffix image_poster https://image.tmdb.org/t/p/w500
#  with the preffix banner_poster https://image.tmdb.org/t/p/w1280
# remove these preffixes from the image_poster and banner_poster fields

class Command(BaseCommand):
    help = "Fix movies where the 'image' field banner_poster and image_poster are incorrectly stored."

    def handle(self, *args, **options):
        movies_image_fixed = 0
        movies_banner_fixed = 0
        movies_with_issue = Movie.objects.all()

        for movie in movies_with_issue[6000:7300]:
            if movie.image_poster != None and movie.image_poster.startswith("https://image.tmdb.org/t/p/w500"):
                # Fix: Remove the prefix from the image_poster field
                
                corrected_image_poster = movie.image_poster.replace("https://image.tmdb.org/t/p/w500", "")
                movie.image_poster = corrected_image_poster
                movie.save()
                movies_image_fixed += 1
                self.stdout.write(self.style.SUCCESS(f"Fixed movie title: {movie.title} -- movie ID ({movie.id}): image: {corrected_image_poster}"))
            elif movie.image_poster == None:
                pass

            if movie.banner_poster != None and movie.banner_poster.startswith("https://image.tmdb.org/t/p/w1280"):
                # Fix: Remove the prefix from the banner_poster field
                corrected_banner_poster = movie.banner_poster.replace("https://image.tmdb.org/t/p/w1280", "")
                movie.banner_poster = corrected_banner_poster
                movie.save()
                movies_banner_fixed += 1
                self.stdout.write(self.style.SUCCESS(f"Fixed movie title: {movie.title} -- movie ID ({movie.id}): banner: {corrected_banner_poster}"))

                time.sleep(0.5)

            elif movie.banner_poster == None:
                pass

        if movies_image_fixed > 0 or movies_banner_fixed > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ {movies_image_fixed} image poster  AND {movies_banner_fixed} banner poster fixed."))
        else:
            self.stdout.write(self.style.SUCCESS("No movies needed fixing. ✅"))
