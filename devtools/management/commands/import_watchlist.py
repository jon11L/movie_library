from django.core.management.base import BaseCommand
import json
from watchlist.models import WatchList 
from media_library.models import Media  
from review.models import Review 


class Command(BaseCommand):
    help = "Reimport watchlist/ or Review from JSON file"

    # -- import watchlist items
    def handle(self, *args, **options):
        with open("watchlist_rescue.json") as f:
            entries = json.load(f)

        created, skipped, missing = 0, 0, []

        for e in entries[0:]:  # limit for testing
            try:
                
                media = Media.objects.get(slug=e["slug"])
                obj, was_created = WatchList.objects.get_or_create(
                    user_id=e["user_id"],
                    media=media,
                    defaults={
                        "status": e["status"],
                        "personal_note": e.get("personal_note"),
                    }
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
            except Media.DoesNotExist:
                missing.append(e)

        self.stdout.write(self.style.SUCCESS(f"Created: {created}, Skipped: {skipped}, Missing: {len(missing)}"))
        if missing:
            with open("missing_media.json", "w") as f:
                json.dump(missing, f, indent=2)
            self.stdout.write(self.style.WARNING(f"Missing media written to missing_media.json"))



    # -- import Review instances

    # def handle(self, *args, **options):
    #     with open("review_rescue.json") as f:
    #         entries = json.load(f)

    #     created, skipped, missing = 0, 0, []

    #     for e in entries[10:]:
    #         try:

    #             print(f'\n-- {e['title']}')
    #             media = Media.objects.get(slug=e["slug"])
    #             score = float(input('type a score to rate this media. 1 to 10: '))

    #             obj, was_created = Review.objects.get_or_create(
    #                 user_id=e["user_id"],
    #                 media=media,
    #                 defaults={
    #                     "score": score,
    #                     "status": "completed",
    #                 }
    #             )
    #             if was_created:
    #                 created += 1
    #             else:
    #                 skipped += 1
    #         except Media.DoesNotExist:
    #             missing.append(e)

    #     self.stdout.write(self.style.SUCCESS(f"Created: {created}, Skipped: {skipped}, Missing: {len(missing)}"))
    #     if missing:
    #         with open("missing_media.json", "w") as f:
    #             json.dump(missing, f, indent=2)
    #         self.stdout.write(self.style.WARNING(f"Missing media written to missing_media.json"))


