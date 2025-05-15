from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
import traceback

from .models import Comment
from comment.forms import CommentForm
from movie.models import Movie
from serie.models import Serie


def create_comment(request):
    '''
    Views to create/post a new comment.
    This will be handle with Ajax between the front and backend
    to display the new post without page reload.
    '''
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

                # print(f"form contains: {form}") # the whole comment <div>
                print(f"form contains:")
                print(f"{comment.body}, -contentT: {comment.content_type} objectId: {comment.object_id} is type of {type(comment.object_id)}")
                
                comment.save() # save the comment to the database

                # print(f"\nform contains all: {form.data}")
                context = {
                    'comment': comment,
                }
                comment_html = render_to_string('comment/block_comment.html', context=context, request=request )
                # message = f"Comment posted successfully!"

                return JsonResponse({
                    'success': True,
                    # 'message': message,
                    'comment_html': comment_html,
                })

            else:
                # When an error occured, dispaly the error message.
                # message = f"Invalid form submitted!"
                return JsonResponse({'success': False, 'error': 'Form submitted Invalid!'})
            
        except Exception as e:
            print(f"**An error occured. Error**: \n{e}")

    else:
        return JsonResponse({'success': False, 'error': 'invalid request!'}, status=400)



# Create your views here.
def delete_comment(request, pk):
    '''delete a comment from the database'''
    comment = Comment.objects.get(pk=pk)
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

            # return redirect("main:home")
            # if comment.content_type == "movie":
            #     movie = Movie.objects.get(pk=comment.object_id)
            #     slug = movie.slug
            #     return redirect('movie:detail', slug=slug)
            # elif comment.content_type == "serie":
            #     serie = Serie.objects.get(pk=comment.object_id)
            #     slug = serie.slug
            #     return redirect('serie:detail', slug=slug)





def edit_comment(request, pk):
    '''edit a comment from the database'''
    # display the Comment form if user is connected
    # Need to add a check that only current user can visit their own Like page.
    comment = Comment.objects.get(pk=pk)

    print(f"request.user: {request.user}")

    if not request.user.is_authenticated or request.user.is_authenticated and comment.user != request.user:
        print(f"\n* Unauthorised acces: User {request.user} tried to access the editing  Comment belonging to another user *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='main:home')
    
    # if user somehow tries to edit a comment that was already edited, redirect to the detail page of the movie or serie that the comment belongs to
    elif request.user.is_authenticated and comment.user == request.user and comment.created_at != comment.updated_at:
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


    elif request.user.is_authenticated and comment.user == request.user and comment.created_at == comment.updated_at:
        try:
            print(f"comment to edit: {comment}")
            # create a comment form  with the existing comment body instance
            form = CommentForm(request.POST or None, instance=comment)

            if request.method == "POST":
                print(f" User: {request.user.username} editing a comment!")
                if form.is_valid():
                    form.save(commit=False)
                    form.instance.body = form.cleaned_data['body']
                    form.save(commit=True)
                    print(f"The comment has been edited: {comment}")
                    messages.success(request, "Comment edited successfully")
                    if comment.content_type == "movie":
                        movie = Movie.objects.get(pk=comment.object_id)
                        slug = movie.slug
                        return redirect('movie:detail', slug=slug)
                    elif comment.content_type == "serie":
                        serie = Serie.objects.get(pk=comment.object_id)
                        slug = serie.slug
                        return redirect('serie:detail', slug=slug)
                    else:
                        # in case of error/form invalid
                        messages.error(request, "Invalid comment form submitted.")
                        return redirect(request.META.get('HTTP_REFERER'))

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
