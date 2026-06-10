from watchlist.models import WatchList
from review.models import Review

# This file contains utility functions to get user-specific context data for the homepage and other views.
# eg. allows to check if the media displayed has been reviewed or added to watchlist by user

def get_user_watchlist(user, **kwargs) -> set[int]:
    """Returns watchlist's media IDs for an authenticated user.

    media_ids (set[int]): iterable of media_id ints used to limit the query.
    """
    
    media_ids: set[int] = kwargs.get("media_ids", ())

    return set(
        WatchList.objects.filter(user=user, media_id__in=media_ids).values_list(
            "media_id", flat=True
        )
    )


def get_user_review(user, **kwargs) -> set[int]:
    """Returns reviewed media IDs for an authenticated user.

    media_ids (list[int]): iterable of media_id ints used to limit the query.
    """

    media_ids: set[int] = kwargs.get("media_ids", ())

    return set(
        Review.objects.filter(user=user, media_id__in=media_ids).values_list("media_id", flat=True)
    )
