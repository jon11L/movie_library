import time
import json

from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F

# Models import
from .models import Review
from watchlist.models import WatchList
from user.models import User, Profile

from .forms import ReviewForm
from watchlist.forms import WatchListForm

# Temporary placement for paginator design
from core.tools.paginator import page_window
from core.tools.wrappers import timer, num_queries

# Create your views here.


def toggle_review(request, object_id: int):
    '''
    When review-buttons element triggered or called  with AJAX on the front-end, 
    this function will first check if the review entry exist.\n 
    If an instance exist between user/(media).\n 
    if it does not, it will then create a new instance in the database,
    if the instance already exists, it will delete the instance.
    With AJAX implemented on the front-end, the updates on the data are made without reloading the page
    '''

    # Need to create a form instead that goes into the modal/popup
    # if watchlist does not exist. empty form - cancel / save button
    # if watchlist exit: button toogle, forms filled, with delete, edit/save button
    # -- In front end i need to place the form. and send the data in js like with createcomment

    data = {} # intialize the data to pass in the JsonResponse

    # if user is Not logged in, an error message is sent back a login required error response
    if not request.user.is_authenticated:
        message = "You must be logged in to review contents."
        return JsonResponse({
            'error': 'User not authenticated, login required.',
            'message': message
            }, status=401)

    if request.method == "GET":
        # This part is for the modal form to load the data if the content is already in the watchlist
        review = Review.objects.filter(
            user=request.user,
            media=object_id,
            ).first()

        if review:
            print(f"Review entry exist.\n")
            data = {
                'is_reviewed': True,
                'status': review.status,
                'review': review.review,
                'rewatch': review.rewatch,
                'score': review.score,
            }

        else:
            print(f"Review entry Does not exist.\n")
            data = {'is_reviewed': False}

        return JsonResponse(data)

    # user clicked the 'like' button
    if request.method == "POST":

        try:
            form = ReviewForm(request.POST or None)
            print("Reading the form from the request...")
            print(f"Form data: {form.data}") # Debug print to check form data
            for key, value in form.data.items():
                print(f"Form field: {key}, value: {value}")

            if form.is_valid():
                print(f"Form is valid.\n Cleaned data: {form.cleaned_data}")
                for key, value in form.cleaned_data.items():
                    print(f"Cleaned data field: {key}, value: {value}")

                new_review = Review(
                    user=request.user,
                    media_id = object_id,
                    status = form.cleaned_data['status'],
                    review = form.cleaned_data['review'],
                    rewatch = form.cleaned_data['rewatch'],
                    score = form.cleaned_data['score'],
                ) # create new instance that takes the form's data & the user/media_id

                new_review.save()
                print(
                    f"Form data:\n review: {new_review.review},"
                    f" status: {new_review.status}")

                message = f"*{new_review.media}* was reviewed."
                # Send the response to Ajax on front-end.
                return JsonResponse({'is_reviewed': True, 'message': message})

            else:
                print(f"Form is not valid. Errors: {form.errors}")
                # return JsonResponse({'in_watchlist': False, 'message': "Invalid form data."}, status=400)
                return JsonResponse({'error': str(form.errors)}, status=400)

        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")
            return JsonResponse(
                {
                    "is_reviewed": False,
                    "message": "An error occurred while processing your request.",
                },
                status=500,
            )

    if request.method == "PUT":
        # Review entry already exists. Will be updated with the new form's data.
        exist_review = Review.objects.filter(
            user=request.user,
            media_id=object_id,
            ).first()

        try:
            data = json.loads(request.body)
            form = ReviewForm(data)

            if form.is_valid() and exist_review:
                # Update the existing review entry with new data
                print(f"Form data: {form.cleaned_data}") # Debug print to check form data
                exist_review.status = form.cleaned_data['status']
                exist_review.review = form.cleaned_data['review']
                exist_review.rewatch = form.cleaned_data['rewatch']
                exist_review.score = form.cleaned_data['score']
                exist_review.save()

                print(
                    f"Review updated.\n"
                    f" Updated data: review: {exist_review.review},"
                    f" status: {exist_review.status}"
                    )

                message = f"*{exist_review.media}* review updated."
                # responding to Ajax on front-end.
                return JsonResponse({'is_reviewed': True, 'message': message}) 

        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")
            return JsonResponse(
                {
                    "is_reviewed": True,
                    "message": "An error occurred while processing your request.",
                },
                status=500,
            )

    # if request.method == "DELETE":
    #     try:
    #         # If the watchlist entry already exists, it will be deleted.
    #         watchlist = WatchList.objects.filter(
    #             user=request.user,
    #             media=object_id,
    #             ).first()

    #         if watchlist:
    #             watchlist.delete()
    #             title = watchlist.media
    #             print(f"*{title}* removed from watchlist\n")
    #             message = f"*{title}* removed from your watchlist."

    #             return JsonResponse({'in_watchlist': False, 'message': message}) # responding to Ajax on front-end.

    #     except Exception as e:
    #         print(f"**An error occured. Error**: \n{e}")

    #         message = "An error occurred while processing your request. Please Try again or refresh the page."

    #         return JsonResponse(
    #             {
    #                 "in_watchlist": True,
    #                 "message": message,
    #             },
    #             status=500,
    #         )






@timer
@num_queries
def list_view(request, user_pk: int):
    '''
        retrieve the user's watchlist from the database and display them in the template
    '''

    base_url = f"/review/list/{user_pk}"
    sort_by = None
    list_media = [] # list to hold the content (movies, series)

    user_watchlist = set()

    # retrieve the profile being requested
    try:
        t_user = User.objects.get(pk=user_pk)
        target_profile = t_user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, "The user or profile's reviews you are trying to access does not exist.")
        return redirect('main:home')

    # Need to add a check that only current user can visit their own Like page.
    if (
        request.user.is_authenticated
        and request.user.id != user_pk
        and target_profile.watchlist_private
        and not request.user.is_staff
    ):
        print(
            "\n** Unauthorised acces: user tried to access a private user's reviews page **\n"
        )
        messages.error(request, ("Private access, Page not accessible."))
        return redirect(to='user:profile_page', pk=request.user.id)

    # user is authenticated & is either the watchlist's owner or watchlist is set public or user is staff/admin
    elif request.user.is_staff or (
        request.user.is_authenticated and
        (request.user.id == user_pk or not target_profile.watchlist_private)
    ):

        if request.method == "GET":
            # present the watchlist form in the modal When user click 
            watchlist_form = WatchListForm() 
            review_form = ReviewForm()

            # ========== setting values for sorting-by feature ==========================
            sort_by = (
                # ('display name', 'django field')
                ('first added', 'id'),
                ('last added', '-id'),
                ('A-z title', 'title'), 
                ('Z-a title', '-title'),
                ('newest first', '-release_date'), # Release_date & filter_date variable name issue
                ('oldest first', 'release_date'),
                ('least popular', 'popularity'),
                ('most popular', '-popularity'),
                ('least voted', 'vote_count'),
                ('most voted', '-vote_count'),
                ('lowest rating', 'vote_average'),
                ('highest rating', '-vote_average'),
            )

            query_params = request.GET.copy()
            print(f"-- Query params: {query_params}\n")  # Debug print

            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')
            query_pagin_url = query_params.urlencode()

            # query_string_url = query_params.urlencode()
            select_order = '-id' # default selection order / first reach of the list page
            if 'order_by' in query_params:
                # need to grab the Media attribute for sorting-by
                select_order = query_params.get('order_by')

            print(f"selected order: {select_order}")
            query_sort_url = query_params.urlencode()

            reviews = Review.objects.filter(user=user_pk).select_related("media")

            list_review = []
            
            is_desc_order = '-' if '-' in select_order else ''
            # Need to specify the field name for sorting 
            # when select_order is not based on the Review model's field but on the related Media model's field.
            field_name = f'media__{select_order.strip('-')}'

            # Do the sorting of the watchlist depending on the sel_order
            if 'id' in select_order:
                list_review = reviews.order_by(select_order)

            # sort by the select_related media_field 
            elif is_desc_order:
                list_review = reviews.order_by(F(field_name).desc(nulls_last=True))
            else:
                list_review = reviews.order_by(F(field_name).asc(nulls_last=True))

            # -- paginate over the results --
            paginator = Paginator(list_review, 24)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(f"List content: {page_obj}")

            # create a standardized data stack to pass in templates.
            # Avoiding any extra hidden queries on the frontend
            for item in page_obj:
                # try:
                list_media.append({
                    "id": item.media.pk, 
                    "title": item.media.title, 
                    "genre": item.media.render_genre(), 
                    "release_date": item.media.release_date,
                    "render_vote_average": item.media.render_vote_average(), 
                    "vote_count": item.media.vote_count, 
                    "popularity": item.media.popularity,
                    "render_poster": item.media.render_poster(),
                    "slug": item.media.slug,
                    "type": item.media.media_type,
                    })

            total_content = reviews.count()

            # --- Get the user's watchlist content (movies, series) ---
            user_reviews = set(
                Review.objects.filter(
                    user=request.user.id
                ).values_list("media_id", flat=True)
            )

            # -------- Get the user's reviewed media  ----------
            user_watchlist = set(
                WatchList.objects.filter(user=request.user.id).values_list("media_id", flat=True)
            )

            context = {
                'page_obj': page_obj,
                'sort_by': sort_by,
                'query_pagin_url': query_pagin_url,
                'query_sort_url': query_sort_url,
                'current_order': select_order,
                'base_url': base_url,
                'list_media' : list_media,
                'user': t_user.username,
                'total_content': total_content,
                "user_watchlist": user_watchlist,
                'user_reviews': user_reviews,
                # 'user_liked_movies': user_liked_movies,
                # 'user_liked_series': user_liked_series,
                'watchlist_form': watchlist_form,
                'review_form': review_form,
            }

            # Temporary placement for paginator design
            context["desktop_pages"] = page_window(
                page_obj.number, # current page number
                page_obj.paginator.num_pages, # total amount of pages
                size=5 # amount of buttons to display around current page
            )

            context["mobile_pages"] = page_window(
                page_obj.number,
                page_obj.paginator.num_pages,
                size=2
            )

            # If user select a sort-by or page parameter, create a request with HTMX
            if request.headers.get('HX-request'):
                print("\n -- HTMX request detected - returning partial list --")
                return render(request, 'partials/media_grid.html', context=context)

            return render(request, 'review/reviews_list.html', context=context)

    else:
        # user is not authenticated. No access to Watchlist, private or public. Must be registered
        messages.error(request, "You must be logged in to view watchlist .")
        return redirect('user:login')

