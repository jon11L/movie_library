from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from .models import Comment
from comment.forms import CommentForm

import traceback

from movie.models import Movie
from serie.models import Serie

# Create your views here.
def delete_comment(request, pk):
    '''delete a comment from the database'''
    if request.user.is_authenticated:
        try:
            comment = Comment.objects.get(pk=pk)

            if comment.user == request.user:
                print(f"comment to delete: {comment}")

                comment.delete()
                print(f"The comment has been deleted: {comment}")
                messages.success(request, "Comment deleted successfully")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, "Error deleting comment, Comment does not exist or you are not the owner")
                return redirect("main:home")
        
        except Exception as e:
            print(f"Error in trying to delete a comment\n Error: {e}")
            messages.error(request, "The comment does not exist or you are not the owner")
            return redirect("main:home")
        



def edit_comment(request, pk):
    '''edit a comment from the database'''
    # display the Comment form if user is connected
    # Need to add a check that only current user can visit their own Like page.

    # if request.user.is_authenticated:

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
            # if request.method == "GET":

            #     print(f" User: {request.user.username} got to the Edit Comment page!")
            #     # form = CommentForm(instance=comment)
            #     context = {
            #         'form': form,
            #         'comment': comment,
            #     }
            #     return render(request, 'comment/edit.html', context)

            if request.method == "POST":
                print(f" User: {request.user.username} editing a comment!")
                if form.is_valid():
                    print("is form valid or not ?")
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
