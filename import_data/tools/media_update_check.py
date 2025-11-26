import datetime

from serie.models import Episode


def check_update_since(media: object, media_type: str):
    """
    This function will allow to check when a media was last updated and if necessit an update\n
    - media: which should be either a movie or serie instance
    - media_type: is a str of the type being received "Movie" or "Serie"

    check if media is already released\n
    check if media was already updated after the release date\n

    Takes the release_date info from the Saved object in DB not the new qery.\n
    Which help Serie object, as when new episode comes out they will be stored in
    and allow for regular updates around the time of episodes being released.

    Reduces unnecessary api calls if media was recently updated in DB\n
    """

    media = media
    media_type = media_type

    last_ep_out = None
    release_date = None
    is_released = False
    is_update_after_release = False
    is_recently_released = False

    updated_at = media.updated_at.date()
    updated_since = datetime.datetime.now(datetime.timezone.utc).date() - updated_at 

    print(f"- {media_type} {media.tmdb_id} - {media.title} exists.")
    print(f"- Last updated {updated_since.days} days ago. {updated_at}")

    if media_type == "Serie":
        last_ep_out = Episode.objects.filter(
            season__serie=media,  # ← Follow relationship backwards
            release_date__isnull=False      # ← Only episodes with release_date
        ).order_by('-release_date').first()  # ← Get the most recent

    if last_ep_out:
        # only works when a serie was being sent and last season had episoeds with rels_date
        print(f"last_ep_out: {last_ep_out} -- {last_ep_out.release_date}")
        
        release_date = last_ep_out.release_date or media.last_air_date
    else:
        # Movie type being passed on
        release_date = media.release_date

    print(f"- release on: {release_date}")

    # check if release date is in the past
    if release_date:
        when_release =  datetime.date.today() - release_date
        if when_release.days < 0:
            # Movies is not released yet.
            print(f"- {media_type} is not released yet... -- In '{when_release.days} days'")

        else:
            # media is already released.
            print(f"- {media_type} already released. -- Since '{when_release.days} days'")
            is_released = True
            is_recently_released = True if when_release.days <= 40 else False

            # check if updated_at is after release date
            if updated_at >= release_date and updated_at.strftime("%d/%m/%Y") != media.created_at.date().strftime("%d/%m/%Y"):
                is_update_after_release = True
                print(f"- {media_type} was updated after the release date updt:{updated_at}")  
            else:
                print(f"- {media_type} was updated before the release date or never updated. updt:{updated_at}") 
                
    desired_updt_days = 15 # gives a minimum of 15 days before updating again
    print(f"is_released, is_recently_released, is_update_after_release, when release")
    print(f"{is_released}, {is_recently_released}, {is_update_after_release} , {when_release if release_date else None}")
    
    # set how long before a Media get updated again depending on certain conditons 
    # eg. when was it released? was it updated after release?
    if is_recently_released and is_update_after_release:
        # Media rencently released and updated already
        desired_updt_days = 7 

    elif is_recently_released and not is_update_after_release:
        # Media recently released but not updated since release, need updates
        desired_updt_days = 1

    # to modify (give low num) or comment this condition if Db structure and import has changed,
    elif is_released and not is_recently_released and is_update_after_release:
        # Media released since a while and updated already, no need to reupdate often
        desired_updt_days = 20
        
    elif release_date and not is_released and when_release.days <= -100:
        # Media not releasing soon so more info may be added or wait to get close the release
        desired_updt_days = 30

    if updated_since.days <= desired_updt_days:
        return False, desired_updt_days
    return True, desired_updt_days