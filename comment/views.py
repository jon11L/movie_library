from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from .models import Comment




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
                return redirect(request.META.get('HTTP_REFERER', 'movie:movie_overview'))
            else:
                messages.error(request, "Error deleting comment, Comment does not exist or you are not the owner")
                return redirect("main:home")
        
        except Exception as e:
            print(f"Error in trying to delete a comment\n Error: {e}")
            messages.error(request, "The comment does not exist or you are not the owner")
            return redirect("main:home")