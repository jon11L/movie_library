from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
import traceback
import json
from django.utils import timezone

from comment.forms import CommentForm
from .models import Comment
from movie.models import Movie
from serie.models import Serie


def create_comment(request):
    '''
    Views to create/post a new comment.\n
    This will be handle with Fetch api from Js between the front and back-end
    to display the new post without page reload.
    '''
        # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        print(f"\n* Unauthorised acces: User {request.user} tried to access the comment creation page *\n")
        return JsonResponse({
            'success': False,
            'error': 'Login required',
            'message': "You must be logged to use the Watchlist feature."
            }, status=401)

    print("Reaching the create_comment() function...")
    if request.method == 'POST':
        try:
            form = CommentForm(request.POST or None)
            print("reached here after req.method=POST, before checking form isvalid.")
            if form.is_valid():
                comment = form.save(commit=False)

                comment.content_type = request.POST.get('content_type')
                comment.object_id = int(request.POST.get('object_id'))

                if not comment.content_type or not comment.object_id:
                    return JsonResponse({'success': False, 'error': 'Missing data'})

                comment.body = form.cleaned_data['body']
                comment.user = request.user
                print(f"form contains:")
                print(f"{comment.body}\n-contentType: '{comment.content_type}' -- objectId: '{comment.object_id}''")
                comment.save() # save the comment to the database

                context = {
                    'comment': comment,
                }
                # Render the comment block to be returned as HTML to be insterted with Js/AJAX on the current page
                # This will be used to display the new comment without reloading the page
                comment_html = render_to_string('comment/block_comment.html',
                                                context=context, request=request
                                                )
                
                # message = f"Comment posted successfully!"
                print(f"comment: {comment.body} was suscessfully posted by {request.user}!")
                return JsonResponse({
                    'success': True,
                    # 'message': message,
                    'comment_html': comment_html,
                })

            else:
                # When an error occured, dispaly the error message.
                # message = f"Invalid form submitted!"
                return JsonResponse({'success': False,
                                    'error': 'Form submitted Invalid!'
                                    })
            
        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")

    else:
        return JsonResponse({'success': False, 'error': 'invalid request!'}, status=400)


# Create your views here.
def delete_comment(request, pk):
    '''delete a comment from the database'''
    try:
        comment = Comment.objects.get(pk=pk)

    except Comment.DoesNotExist:
        print(f"Comment with id {pk} does not exist.")
        return JsonResponse({'success': False, 'message': f'Comment with id {pk} does not exist.'}, status=404)


    if request.user.is_authenticated and comment.user == request.user:
        try:
            if request.method == "DELETE":
                print(f"request.user: {request.user}")
                print(f"request.method: {request.method}")
                # print(f"request.POST: {request}")
                
                print(f"comment to delete: {comment}")
                comment.delete()
                # messages.success(request, "Comment deleted successfully")
                return JsonResponse({'success': True, 'message': f'Comment of {request.user} was deleted.'}, status=200)

        except Exception as e:
            print(f"Error in trying to delete a comment\n Error: {e}")
            # messages.error(request, "The comment does not exist or you are not the owner")
            return JsonResponse({'success': False, 'message': f'Comment of {request.user} could not be deleted.'}, status=404)



def edit_comment(request, pk):
    '''edit a comment from the database
    ### display the Comment form if user is authenticated and the comment belongs to them
     -  The user can only edit their comment once, the edit button will not longer be displayed if the comment was already edited.
     - Aswell as a (Edited) tag will be displayed next to the comment creation date.
    '''
    try:
        # comment = Comment.objects.get(pk=pk)
        comment = get_object_or_404(Comment.objects, pk=pk)

    except Comment.DoesNotExist:
        print(f"Comment with id {pk} does not exist.")
        return JsonResponse({'success': False, 'message': f'Comment with id {pk} does not exist.'}, status=404)

    # print(f"request.user: {request.user}")
    print(f"comment to edit: {comment}")

    if not request.user.is_authenticated or request.user.is_authenticated and comment.user != request.user:
        print(f"\n* Unauthorised acces: User {request.user} tried to access the editing  Comment belonging to another user *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='main:home')
    
    # if user somehow tries to edit a comment that was already edited, redirect to the detail page of the movie or serie that the comment belongs to
    elif request.user.is_authenticated and comment.user == request.user and comment.created_at.strftime("%d/%m/%Y, %H:%M:%S") != comment.updated_at.strftime("%d/%m/%Y, %H:%M:%S"):
        print(f"\n* Unauthorised acces: User {request.user} tried to edit a  Comment more than once. Forbidden *\n")
        messages.error(request, ("You are not authorized to acces this page. This comment was already edited."))
        if comment.content_type == "movie":
            movie = Movie.objects.get(pk=comment.object_id)
            slug = movie.slug
            return redirect('movie:detail', slug=slug)
        elif comment.content_type == "serie":
            serie = Serie.objects.get(pk=comment.object_id)
            slug = serie.slug
            return redirect('serie:detail', slug=slug)

    elif request.user.is_authenticated and comment.user == request.user and comment.created_at.strftime("%d/%m/%Y, %H:%M:%S") == comment.updated_at.strftime("%d/%m/%Y, %H:%M:%S"):
        try:
            print(f"comment to edit: {comment}")
            # create a comment form  with the existing comment body instance
            # form = CommentForm(request.POST or None, instance=comment)

            #  -----TRIAL/ Updating the function to use Fetch API
            if request.method == "PUT":
                print(f"request.user: {request.user}, request.method: {request.method}")
                print(f"request.POST: {request}")
                # print(f"request.body: {request.body}")
                try:
                    print(f"request.body: {request.body}")
                    data = json.loads(request.body)
                    print(f"data: {data}")

                    new_body = data.get('body')
                    print(f"new_body: {new_body}")
                    if new_body:
                        # comment.save(commit=False)
                        comment.body = new_body
                        comment.updated_at = timezone.now()
                        comment.save()

                    print(f"The comment has been edited: {comment}")
                    return JsonResponse({'success': True, 'message': 'Comment was updated successfully!'}, status=200)
                    
                    # else:
                    #     print(f"form is not valid")
                    #     print(f"form.errors: {form.errors}") 
                    #     return JsonResponse({'success': False, 'error': 'Form submitted Invalid!'})


                except Exception as e:
                    print(f"Error in trying to edit a comment\n Error: {e}")
                    return JsonResponse({'success': False, 'message': f'Comment of {request.user} could not be edited.'}, status=404)

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error in trying to edit a comment\n Error: {e}")
            messages.error(request, "The comment either does not exist, you are not the owner or an internal error occurred")
            if comment.content_type == "movie":
                movie = Movie.objects.get(pk=comment.object_id)
                slug = movie.slug
                return redirect('movie:detail', slug=slug)
            elif comment.content_type == "serie":
                serie = Serie.objects.get(pk=comment.object_id)
                slug = serie.slug
                return redirect('serie:detail', slug=slug)