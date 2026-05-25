import time
import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import F

# Rest api imports
from rest_framework import generics, filters, request
# from rest_framework import renderers
from rest_framework.throttling import AnonRateThrottle
from core.throttle import AdminRateThrottle, UserBurstThrottle, UserSustainThrottle, UserDayThrottle
from core.permissions import IsAdminOrOwner

# from .serializers import WatchListSerializer

# Models import
from .models import WatchList
from review.models import Review
from user.models import User, Profile
# from user_library.models import Like

from watchlist.forms import WatchListForm
from review.forms import ReviewForm

# Temporary placement for paginator design
from core.tools.paginator import page_window
from core.tools.wrappers import timer, num_queries


# class WatchListListView(generics.ListCreateAPIView):
#     '''This serializer '''

#     serializer_class = WatchListSerializer
#     permission_classes = [IsAdminOrOwner]
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['status']
#     ordering_fields = ['created_at', "updated_at"]
#     throttle_classes = [
#         AnonRateThrottle,
#         AdminRateThrottle,
#         UserBurstThrottle,
#         UserSustainThrottle,
#         UserDayThrottle,
#     ]

#     def get_queryset(self):
#         '''
#         Overriding the queryset.\n
#         Return only Watchlist instances created by their own user.\n
#         Unless Admin or staff then full access.\n
#         '''
#         user = self.request.user
#         if not user.is_staff:
#             # Ensure if the user is not Staff or Admin, they only get what is on their watchlist
#             return WatchList.objects.filter(user=user).select_related('movie', 'serie')
#         else:
#             # return WatchList.objects.select_related('movie', 'serie')
#             return WatchList.objects.select_related('movie', 'serie')

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class WatchListDetailView(generics.RetrieveUpdateDestroyAPIView):

#     queryset = WatchList.objects.select_related('movie', 'serie').prefetch_related().order_by('id')
#     serializer_class = WatchListSerializer
#     # renderer_classes = [renderers.StaticHTMLRenderer]

#     permission_classes = [IsAdminOrOwner]
#     throttle_classes = [
#         AnonRateThrottle,
#         AdminRateThrottle,
#         UserBurstThrottle,
#         UserSustainThrottle,
#         UserDayThrottle,
#     ]

#     def get_queryset(self):
#         '''
#         Overriding the queryset.\n
#         Return only Watchlist object instance created by the user\n
#         '''
#         user = self.request.user
#         if not user.is_staff:
#             return WatchList.objects.filter(user=user).select_related('movie', 'serie')
#         else:
#             return WatchList.objects.select_related('movie', 'serie')

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)


@timer
@num_queries
def list_view(request, user_pk: int):
    '''
        retrieve the user's watchlist from the database and display them in the template
    '''

    base_url = f"/watchlist/list/{user_pk}"
    sort_by = None
    list_media = [] # list to hold the content (movies, series)
    user_liked_movies = set()
    user_liked_series = set()
    user_watchlist = set()

    # retrieve the profile being requested
    try:
        t_user = User.objects.get(pk=user_pk)
        target_profile = t_user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, "The user or profile's Watchlist you are trying to access does not exist.")
        return redirect('main:home')

    # Need to add a check that only current user can visit their own Like page.
    if (
        request.user.is_authenticated
        and request.user.id != user_pk
        and target_profile.watchlist_private
        and not request.user.is_staff
    ):
        print(
            "\n** Unauthorised acces: user tried to access a private user's watchlist **\n"
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

            watchlist = WatchList.objects.filter(user=user_pk).select_related("media")

            list_watchlist = []
            
            is_desc_order = '-' if '-' in select_order else ''
            field_name = f'media__{select_order.strip('-')}'

            # Do the sorting of the watchlist depending on the sel_order
            if 'id' in select_order:
                list_watchlist = watchlist.order_by(select_order)

            # sort by the select_related media_field 
            elif is_desc_order:
                list_watchlist = watchlist.order_by(F(field_name).desc(nulls_last=True))
            else:
                list_watchlist = watchlist.order_by(F(field_name).asc(nulls_last=True))



            # -- paginate over the results --
            paginator = Paginator(list_watchlist, 24)
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
                    "vote_avg": item.media.render_vote_average(), 
                    "vote_count": item.media.vote_count, 
                    "popularity": item.media.popularity,
                    "poster": item.media.render_poster(),
                    "slug": item.media.slug,
                    "type": item.media.media_type,
                    })

            total_content = watchlist.count()

            # --- Get the user's watchlist content (movies, series) ---
            user_watchlist = set(
                WatchList.objects.filter(
                    user=request.user.id
                ).values_list("media_id", flat=True)
            )

            # -------- Get the user's reviewed media  ----------
            user_reviews = set(
                Review.objects.filter(user=request.user.id).values_list("media_id", flat=True)
            )

            # user_liked_series = set(
            #     Like.objects.filter(
            #         user=request.user.id, content_type="serie"
            #     ).values_list("object_id", flat=True)
            # )

            context = {
                'page_obj': page_obj,
                'sort_by': sort_by,
                'query_pagin_url': query_pagin_url,
                'query_sort_url': query_sort_url,
                'current_order': select_order,
                'base_url': base_url,
                'list_media' : list_media,
                'user': t_user.username,
                "user_watchlist": user_watchlist,
                'user_liked_movies': user_liked_movies,
                'user_liked_series': user_liked_series,
                'total_content': total_content,
                'watchlist_form': watchlist_form,
                'review_form': review_form,
                'user_reviews': user_reviews,
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

            return render(request, 'watchlist/watch_list.html', context=context)

    else:
        # user is not authenticated. No access to Watchlist, private or public. Must be registered
        messages.error(request, "You must be logged in to view watchlist .")
        return redirect('user:login')


def toggle_watchlist(request, object_id: int):
    '''
    When watchlist-buttons element triggered or called  with AJAX on the front-end, 
    this function will first check if the watchlist entry exist.\n 
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
        message = "You must be logged in to use the Watchlist"
        # messages.error(request, "You must be logged in to like contents.")
        return JsonResponse({
            'error': 'User not authenticated, login required.',
            'message': message
            }, status=401)

    if request.method == "GET":
        # This part is for the modal form to load the data if the content is already in the watchlist
        watchlist = WatchList.objects.filter(
            user=request.user,
            media=object_id,
            ).first()

        if watchlist:
            print(f"Watchlist entry exist.\n")
            data = {
                'in_watchlist': True,
                'personal_note': watchlist.personal_note,
                'status': watchlist.status,
            }

        else:
            print(f"Watchlist entry Does not exist.\n")
            data = {'in_watchlist': False}

        return JsonResponse(data)

    # user clicked the 'like' button
    if request.method == "POST":

        try:
            form = WatchListForm(request.POST or None)
            print("Reading the form from the request...")
            print(f"Form data: {form.data}") # Debug print to check form data
            for key, value in form.data.items():
                print(f"Form field: {key}, value: {value}")

            if form.is_valid():
                print(f"Form is valid.\n Cleaned data: {form.cleaned_data}")
                for key, value in form.cleaned_data.items():
                    print(f"Cleaned data field: {key}, value: {value}")

                new_watchlist = WatchList(
                    user=request.user,
                    media_id = object_id,
                    personal_note = form.cleaned_data['personal_note'],
                    status = form.cleaned_data['status'],
                ) # create new instance that takes the form's data & the user/media_id

                new_watchlist.save()
                print(
                    f"Form data:\n personal_note: {new_watchlist.personal_note},"
                    " status: {new_watchlist.status}")

                message = f"*{new_watchlist.media}* added to your watchlist."
                # Send the response to Ajax on front-end.
                return JsonResponse({'in_watchlist': True, 'message': message})

            else:
                print(f"Form is not valid. Errors: {form.errors}")
                # return JsonResponse({'in_watchlist': False, 'message': "Invalid form data."}, status=400)
                return JsonResponse({'error': str(form.errors)}, status=400)

        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")
            return JsonResponse({'in_watchlist': False, 'message': "An error occurred while processing your request."}, status=500)

    if request.method == "PUT":
        # Watchlist entry already exists. Will be updated with the new form's data.
        watchlist = WatchList.objects.filter(
            user=request.user,
            media_id=object_id,
            ).first()

        try:
            data = json.loads(request.body)
            form = WatchListForm(data)

            if form.is_valid() and watchlist:
                # Update the existing watchlist entry with new data
                print(f"Form data: {form.cleaned_data}") # Debug print to check form data
                watchlist.personal_note = form.cleaned_data['personal_note']
                watchlist.status = form.cleaned_data['status']
                watchlist.save()

                print(
                    f"Watchlist updated.\n"
                    f" Updated data: personal_note: {watchlist.personal_note},"
                    f" status: {watchlist.status}"
                    )

                message = f"*{watchlist.media}* watchlist updated."
                # responding to Ajax on front-end.
                return JsonResponse({'in_watchlist': True, 'message': message}) 

        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")
            return JsonResponse(
                {
                    "in_watchlist": True,
                    "message": "An error occurred while processing your request.",
                },
                status=500,
            )

    if request.method == "DELETE":
        try:
            # If the watchlist entry already exists, it will be deleted.
            watchlist = WatchList.objects.filter(
                user=request.user,
                media=object_id,
                ).first()

            if watchlist: 
                watchlist.delete()
                title = watchlist.media
                print(f"*{title}* removed from watchlist\n")
                message = f"*{title}* removed from your watchlist."

                return JsonResponse({'in_watchlist': False, 'message': message}) # responding to Ajax on front-end.

        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")

            message = "An error occurred while processing your request. Please Try again or refresh the page."

            return JsonResponse(
                {
                    "in_watchlist": True,
                    "message": message,
                },
                status=500,
            )
