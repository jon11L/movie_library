import json

from django.shortcuts import render, redirect

# Create your views here.
from django.http import JsonResponse
from django.contrib import messages

from .models import Review
from .forms import ReviewForm

from user.models import User, Profile


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
