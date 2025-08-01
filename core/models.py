from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class BaseModel(models.Model):
    """
    Base model to be inherited by all models in the project
    Abstract Base Model for the following fields:
    - created_at
    - updated_at
    - is_active
    - slug
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_active =  models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


    def save(self, *args, **kwargs):

        now = timezone.now()
        #     now = timezone.now()
        #     if not self.id:
        #         self.created_at = now
        #     else:
        #         self.updated_at = now
        #     super().save(*args, **kwargs)

        # Generate a slug if it doesn't exist 
        if not self.slug:
            if self.__class__.__name__ == 'Episode' and hasattr(self, 'season') and hasattr(self, 'episode_number') and hasattr(self, 'title'):
                base_slug = slugify(f"{self.season.serie.slug} S{self.season.season_number} E{self.episode_number} {self.title}")

            # For Season objects 
            elif self.__class__.__name__ == 'Season' and hasattr(self, 'name') and self.name:
                base_slug = slugify(f"{self.serie.slug} {self.name}")

            # For Movie or Serie objects
            elif self.__class__.__name__ in ['Movie', 'Serie'] and hasattr(self, 'title'):
                # check if the new object has a release_date(Movie) or first_air_date(Serie) field
                if hasattr(self, 'release_date') and self.release_date is not None:
                    base_slug = slugify(f"{self.title} {self.release_date.strftime('%Y')}")
                elif hasattr(self, 'first_air_date') and self.first_air_date is not None:
                    base_slug = slugify(f"{self.title} {self.first_air_date.strftime('%Y')}")
                else:
                    # else base slug on the title only
                    base_slug = slugify(f"{self.title}")

            # fallback
            else:
                base_slug = slugify(str(now.timestamp()))  

            slug = base_slug
            counter = 1

            # Ensure the slug is unique by appending a counter if necessary
            # This will be for models that has a title field
            while type(self).objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    # def soft_delete(self):
    #     """ Instead of deleting, just deactivate the object """
    #     self.is_active = False
    #     self.save()