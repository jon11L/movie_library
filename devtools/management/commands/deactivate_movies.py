from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Delete selected movies from the database"

    def handle(self, *args, **options):
        
        #TODO:  Add the list of movies'ID or title to delete
        # get the movie title and desription of that movie
        # then confirm the deletion or to ignore it


        black_list_ids = [
            # Add the list of movie IDs or titles you want to delete
            # using the id

        ]

        # from this list of ID, get the TMDB_ID and store them into a new file. 
        # This will be a black list of movies to not fetch anymore
        # is_active = False in the mean time
        deactivated = 0
        for id in black_list_ids:
            try:
                movie = Movie.objects.get(pk=id)
                print("-------------\n")
                print(f"Deactivating movie: {movie.title} -- ID: {movie.pk}")
                print(f"\nDescription: {movie.overview}")
                print(f"Tagline:{movie.tagline}")
                print(f"is_active:{movie.is_active}")
                
                # input_confirmation = input("\nAre you sure you want to delete this movie? (y/n): ")
                input_confirmation = input("\nAre you sure you want to deactivate this movie? (y/n): ")
                while input_confirmation.lower() not in ['y', 'n']:
                    input_confirmation = input("Please enter 'y' for yes or 'n' for no: ")

                if input_confirmation.lower() == 'y':
                    # self.stdout.write(self.style.SUCCESS(f'Deletion for movie: {movie.title}'))
                    self.stdout.write(self.style.SUCCESS(f'Deactivated movie: {movie.title}'))
                    movie.is_active = False
                    movie.save()
                    # movie.delete()
                    # self.stdout.write(self.style.WARNING(f'Successfully deleted movie: {id}'))
                    self.stdout.write(self.style.WARNING(f'Successfully deactivated movie: {id} -- active? {movie.is_active} '))
                    deactivated += 1
                elif input_confirmation.lower() == 'n':
                    self.stdout.write(self.style.SUCCESS(f'Skipping deletion for movie: {movie.title}'))


            except Movie.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Movie not found: {id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting movie {id}: {str(e)}'))

        print(f"Deactivated {deactivated} movies.")


# tmdb_id of the movies that i deleted or do not want on my database
# 1200420, 723846, 




# ID marked as inactive/blacklist, in the mean time to create a black list of sort.
# movie:
# 119, 15787, 16725, 9510, 2379, 29933, 14490, 5980, 25705, 27625,
# 25680, 15535, 31810, 18502, 31907, 15489, 32700, 33662, 33962, 34009, 
# 3414, 34144, 34233, 34048, 14372, 34479, 14735, 15807, 30069, 7324,
# 24513, 9364,  35300, 35159, 35114, 35059, 35391, 14835, 35559, 37496, 
# 37309, 24435, 36810, 36806, 37832, 37833, 11674, 11709, 15934, 30967,
# 19472, 20858, 39460, 39588, 23917, 41804, 41568, 39588, 29846, 41852,
# 6143, 6625, 21745, 28185 15894, 23800, 23599, 27473, 12545, 6658, 2378,
#  40682, 35573, 37125, 30844

# ===================
# serie id:
#  3648

