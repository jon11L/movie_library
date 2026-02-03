import time
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

# Rest api imports
from rest_framework import generics, filters
# from rest_framework import renderers
from rest_framework.throttling import AnonRateThrottle
from core.throttle import AdminRateThrottle, UserBurstThrottle, UserSustainThrottle, UserDayThrottle
from core.permissions import IsAdminOrOwner

from .serializers import WatchListSerializer

# Models import
from .models import WatchList, Like
from user.models import User, Profile
from movie.models import Movie
from serie.models import Serie

# Temporary placement for paginator design
from core.tools.paginator import page_window
from core.tools.wrappers import timer, num_queries


class WatchListListView(generics.ListCreateAPIView):
    '''This serializer '''
    
    serializer_class = WatchListSerializer
    permission_classes = [IsAdminOrOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status'] 
    ordering_fields = ['created_at', "updated_at"]
    throttle_classes = [
        AnonRateThrottle,
        AdminRateThrottle,
        UserBurstThrottle,
        UserSustainThrottle,
        UserDayThrottle,
    ]

    def get_queryset(self):
        '''
        Overriding the queryset.\n
        Return only Watchlist instances created by their own user.\n
        Unless Admin or staff then full access.\n
        '''
        user = self.request.user
        if not user.is_staff:
            # Ensure if the user is not Staff or Admin, they only get what is on their watchlist
            return WatchList.objects.filter(user=user).select_related('movie', 'serie')
        else:
            # return WatchList.objects.select_related('movie', 'serie')
            return WatchList.objects.select_related('movie', 'serie')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchListDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = WatchList.objects.select_related('movie', 'serie').prefetch_related().order_by('id')
    serializer_class = WatchListSerializer
    # renderer_classes = [renderers.StaticHTMLRenderer]

    permission_classes = [IsAdminOrOwner]
    throttle_classes = [
        AnonRateThrottle,
        AdminRateThrottle,
        UserBurstThrottle,
        UserSustainThrottle,
        UserDayThrottle,
    ]

    def get_queryset(self):
        '''
        Overriding the queryset.\n
        Return only Watchlist object instance created by the user\n
        '''
        user = self.request.user
        if not user.is_staff:
            return WatchList.objects.filter(user=user).select_related('movie', 'serie')
        else:
            return WatchList.objects.select_related('movie', 'serie')

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# ------------- Regular template views (List) ---------
def liked_content_view(request, pk: int):
    '''
    retrieve the user's content liked from the database 
    and display them in a template page.
    '''
    # Need to add a check that only current user can visit their own Like page.
    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User_update_page *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        if request.method == "GET":

            user = User.objects.get(id=pk)
            print(f" user {user} visit their Liked media list page\n")

            likes = Like.objects.filter(user=pk)

            liked_content = [] # intialize the list of liked content 
            for like in likes:

                if like.content_type == "movie":
                    try:
                        movie = Movie.objects.get(id=like.object_id)
                        liked_content.append(
                            {
                                "content_type": like.content_type,
                                "object": movie,
                                "liked_on": like.created_at.strftime("%d %B %Y"),
                            }
                        )
                        # print(f"movie: {movie}\n") #debug print
                    except Movie.DoesNotExist:
                        continue
                elif like.content_type == "serie":
                    try:
                        serie = Serie.objects.get(id=like.object_id)
                        liked_content.append(
                            {
                                "content_type": like.content_type,
                                "object": serie,
                                "liked_on": like.created_at.strftime("%d %B %Y"),
                            }
                        )
                        # print(f"serie: {serie}\n") #debug print
                    except Serie.DoesNotExist:
                        continue

            total_like = likes.count() #count how many items has been liked

            context = {
                'liked_content': liked_content[0:40],
                'total_like': total_like,
            }

            return render(request, 'user_library/liked_content.html', context=context)

        elif request.method == "POST":
            # user clicked the 'unlike' button
            if request.POST.get('like_button_clicked') == 'true':
                print(f"like button clicked\n") # debugging
            pass

    else:
        messages.error(request, "You must be logged in to view your liked content.")
        return redirect('user:login')


def toggle_like(request, content_type: str, object_id: int):
    '''When triggered or called in pair with AJAX on the front-end, 
    this function will check in the 'Like' models data
    - if an instance of Like exist between user/content_type (movie or serie)/object_id (id of that object) exist or not 
    - if it does not, it will then create a new instance in the database,
    - if the instance already exists, it will delete the instance.
    - With AJAX implemented on the front-end, the updates on the data are made without reloading the page
    '''

    # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        # messages.error(request, "You must be logged in to like contents.")
        return JsonResponse({
            'error': 'Login required',
            'message': "You must be logged-in to like content. LINK to log here"
            }, status=401)

    # User clicked the 'like' button.
    if request.method == "POST":

            # check if the Like already exists
            like = Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=object_id
                ).first()
            print(f"\n like exist?: {like}\n") # debugging 

            if like: # If the like already exists, it will be removed.
                like.delete()
                print(f"'{like}' Unliked")
                message = f"*{content_type}-{object_id} Unliked*"
                return JsonResponse({'liked': False, 'message': message}) # responding to Ajax on front-end.
            
            else: # the Like is created with the user id, model type and the respective id of this model
                like = Like.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id
                    )
                
                print(f"**Liked**.\n{like}\n")
                # messages.success(request, f"{content_type} added to your likes.")
                message = f"*{content_type}-{object_id} Liked*"
                return JsonResponse({'liked': True, 'message': message}) # responding to Ajax on front-end.

@timer
@num_queries
def watch_list_view(request, pk: int):
    '''
        retrieve the user's watchlist from the database and display them in the template
    '''
    sort_by = None
    base_url = f"/library/{pk}/watch_list/"
    list_media = [] # list to hold the content (movies, series)
    user_liked_movies = set()
    user_watchlist_movies = set()
    user_liked_series = set()
    user_watchlist_series = set()

    # retrieve the profile being requested
    try:
        t_user = User.objects.get(pk=pk)
        target_profile = t_user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, "The user or profile's Watchlist you are trying to access does not exist.")
        return redirect('main:home')

    # Need to add a check that only current user can visit their own Like page.
    if request.user.is_authenticated and request.user.id != pk and target_profile.watchlist_private and not request.user.is_staff:
        print("\n** Unauthorised acces: user tried to access a private user's watchlist **\n")
        messages.error(request, ("Page not accessible, private."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_staff or (
        request.user.is_authenticated and
        (request.user.id == pk or not target_profile.watchlist_private)
    ):  # or request.user == t_user

        if request.method == "GET":

            # ========== setting values for sorting-by feature ==========================
            sort_by = (
                # ('display name', 'django field')
                # ('newest first', '-release_date'), 
                # ('oldest first', 'release_date'),
                # (''),
                ('least popular', 'popularity'),
                ('most popular', '-popularity'),
                ('lowest vote', 'vote_count'),
                ('highest vote', '-vote_count'),
                ('A-z title', 'title'), 
                ('Z-a title', '-title'),
                ('first added', 'id'),
                ('last added', '-id'),
            )

            query_params = request.GET.copy()
            print(f"-- Query params: {query_params}\n")  # Debug print

            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')
            query_pagin_url = query_params.urlencode()

            # query_string_url = query_params.urlencode()

            sel_order = '-id' # default selection order / first reach of the list page
            if 'order_by' in query_params:
                sel_order = query_params.get('order_by')
                # need to grab the movie/serie attribute for sorting-by


            print(f"selected order: {sel_order}")
            query_sort_url = query_params.urlencode()

            watchlist = WatchList.objects.filter(user=pk).select_related(
                "movie", "serie"
            )

            sorting_field = sel_order.strip('-')
            list_watchlist = []
            # Do the sorting of the watchlist depending on the sel_order
            if 'id' in sel_order:
                list_watchlist = watchlist.order_by(sel_order)

            else:
                list_watchlist = sorted(
                    watchlist,
                    key=lambda x: getattr(x.content_object, sorting_field),
                    reverse= True if '-' in sel_order else False,
                )

            # Get the user's watchlist content (movies, series)
            user_watchlist_movies = set(
                WatchList.objects.filter(
                    user=request.user.id, movie__isnull=False
                ).values_list("movie_id", flat=True)
            )

            user_watchlist_series = set(
                WatchList.objects.filter(
                    user=request.user.id, serie__isnull=False
                ).values_list("serie_id", flat=True)
            )

            # ----- Get the user's like content (movies, series)  ------
            user_liked_movies = set(
                Like.objects.filter(
                    user=request.user.id, content_type="movie"
                ).values_list("object_id", flat=True)
            )

            user_liked_series = set(
                Like.objects.filter(
                    user=request.user.id, content_type="serie"
                ).values_list("object_id", flat=True)
            )

            # -- paginate over the results --
            paginator = Paginator(list_watchlist, 24)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(f"List content: {page_obj}")

            # create a standardized data stack to pass in templates.
            # Avoiding any extra hidden queries on the frontend
            for item in page_obj:
                try:
                    media_obj = item.movie if item.movie else item.serie
                    if isinstance(media_obj, Movie):
                        list_media.append({
                            "id": item.movie.pk, 
                            "title": item.movie.title, 
                            "genre": item.movie.render_genre(), 
                            # "release_date": item.release_date
                            "vote_avg": item.movie.render_vote_average(), 
                            "vote_count": item.movie.vote_count, 
                            "popularity": item.movie.popularity,
                            "poster": item.movie.render_poster(),
                            "slug": item.movie.slug,
                            "type": "movie",
                            })

                    elif isinstance(media_obj, Serie):
                        list_media.append({
                            "id": item.serie.pk, 
                            "title": item.serie.title, 
                            "genre": item.serie.render_genre(), 
                            "vote_avg": item.serie.render_vote_average(), 
                            "vote_count": item.serie.vote_count, 
                            "popularity": item.serie.popularity,
                            "poster": item.serie.render_poster(),
                            "slug": item.serie.slug,
                            "type": "serie",
                            })

                except (Movie.DoesNotExist, Serie.DoesNotExist):
                    print(f"Item with id {item} does not exist in the database.\n")
                    continue

            total_content = watchlist.count()

            context = {
                'page_obj': page_obj,
                'sort_by': sort_by,
                'query_pagin_url': query_pagin_url,
                'query_sort_url': query_sort_url,
                'current_order': sel_order,
                'base_url': base_url,
                'list_media' : list_media,
                'user': t_user,
                "user_watchlist_movies": user_watchlist_movies,
                "user_watchlist_series": user_watchlist_series,
                'user_liked_movies': user_liked_movies,
                'user_liked_series': user_liked_series,
                'total_content': total_content,
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
                return render(request, 'partials/media_list.html', context=context)

            return render(request, 'user_library/watch_list.html', context=context)

    else:
        # user is not authenticated. No access to Watchlist, private or public. Must be registered
        messages.error(request, "You must be logged in to view watchlist .")
        return redirect('user:login')


def toggle_watchlist(request, content_type: str, object_id: int):
    '''
    When triggered or called in pair with AJAX on the front-end, 
    this function will trigger the model 'watchlist'\n 
    if an instance exist between user/(movie or serie) exist or not.\n 
    if it does not, it will then create a new instance in the database,
    if the instance already exists, it will delete the instance.
    With AJAX implemented on the front-end, the updates on the data are made without reloading the page
    '''
    # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        message = "You must be logged to use the Watchlist"
        # messages.error(request, "You must be logged in to like contents.")
        return JsonResponse({
            'error': 'Login required',
            'message': message
            }, status=401)

    # user clicked the 'like' button
    if request.method == "POST":
            # check if the object already exists in the watchlist
            watchlist = WatchList.objects.filter(
                user=request.user,
                movie=Movie.objects.get(id=object_id) if content_type == 'movie' else None,
                serie=Serie.objects.get(id=object_id) if content_type == 'serie' else None
                ).first()
            
            print(f"Content in watchlist: '{watchlist}' \n") # debugging 

            # If the watchlist entry already exists, it will be deleted.
            if watchlist: 
                watchlist.delete()
                print(f"*{watchlist.movie if content_type == 'movie' else watchlist.serie}* removed from watchlist\n")
                message = f"*{watchlist.movie if content_type == 'movie' else watchlist.serie}* removed from your watchlist."
                return JsonResponse({'in_watchlist': False, 'message': message}) # responding to Ajax on front-end.
            
            else: 
                # the Watchlist instance is created with the user id,
                # model type and the respective id of this model instance to construct the foreign key
                watchlist = WatchList.objects.create(
                    user=request.user,
                    movie=Movie.objects.get(id=object_id) if content_type == 'movie' else None,
                    serie=Serie.objects.get(id=object_id) if content_type == 'serie' else None
                    )
                #------
                # Here help pass a form to the frontend for the personal_note and Status.
                # -----
                
                print(f"*{watchlist.movie if content_type == 'movie' else watchlist.serie}* added to watchlist.\n")
                # messages.success(request, f"{content_type} added to your likes.")
                message = f"*{watchlist.movie if content_type == 'movie' else watchlist.serie}* added to watchlist."
                return JsonResponse({'in_watchlist': True, 'message': message}) # responding to Ajax on front-end.
