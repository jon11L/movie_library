from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from uuid import uuid4


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


    def unique_slug(self, base_slug):
        '''
        Ensure the slug is unique by appending a counter if necessary\n
        This will be for models that has a title field
        
        '''
        qs = type(self).objects.filter(slug__isnull=False)
        if self.pk: # object already saved/created
            qs = qs.exclude(pk=self.pk)
        exist_slugs = qs.values_list("slug", flat=True)

        slug = base_slug
        i = 1
        # while type(self).objects.filter(slug=slug).exists():
        while slug in exist_slugs:
            slug = f"{base_slug}-{i}"
            i += 1

        return slug


    def save(self, *args, **kwargs):
        '''
        1. Create a generic structure for the slug based on their own models
        2. Check that the slugified version contains something (title-release_date)
        3. Check over in the model for slugs uniqueness excluding itself if exist
        4. add counter until slug is unique
        5. Save slug
        '''
        now = timezone.now()
        #     now = timezone.now()
        #     if not self.id:
        #         self.created_at = now
        #     else:
        #         self.updated_at = now
        #     super().save(*args, **kwargs)

        # Generate a slug if it doesn't exist 
        if not self.slug:
            base_slug = None

            if self.__class__.__name__ == 'Episode' and hasattr(self, 'season') and hasattr(self, 'episode_number') and hasattr(self, 'title'):
                base_slug = slugify(f"{self.season.serie.slug} S{self.season.season_number} E{self.episode_number} {self.title}", allow_unicode=False)

            # For Season objects 
            elif self.__class__.__name__ == 'Season' and hasattr(self, 'name'):
                if self.name is not None:
                    base_slug = slugify(f"{self.serie.slug} {self.name}", allow_unicode=False)
                elif self.name is None:
                    base_slug = slugify(f"{self.serie.slug} Season-{self.season_number}", allow_unicode=False)


            # For Movie or Serie objects
            elif self.__class__.__name__ in ['Movie', 'Serie'] and hasattr(self, 'title'):
                # check if the new object has a release_date(Movie) or first_air_date(Serie) field
                year = None

                # Movies
                if hasattr(self, 'release_date') and self.release_date is not None:
                    year = self.release_date.strftime('%Y')
                # Series
                elif hasattr(self, 'first_air_date') and self.first_air_date is not None: 
                    year = self.first_air_date.strftime('%Y')
                # fall back if no dates recorded -> empty string.
                else:
                    year = ''

                if self.title == None or slugify(self.title) == "":
                    title = 'Untitled'
                else:
                    title = self.title

                short = uuid4().hex[:6]  # will add a random id make it more unique
                base_slug = slugify(f"{title}-{year}-{short}", allow_unicode=False)
                # if title-year-uuid good also title-year-uuid{counter} very unlikely
                # if untitled-year-uuid{counter} also okay

            # fallback
            # if not base_slug:
            #     pass

            # # Ensure the return slug is unique
            self.slug = self.unique_slug(base_slug) 

        super().save(*args, **kwargs)

    # def soft_delete(self):
    #     """ Instead of deleting, just deactivate the object """
    #     self.is_active = False
    #     self.save()