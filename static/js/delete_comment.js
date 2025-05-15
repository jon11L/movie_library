// document.addEventListener("DOMContentLoaded", function () {

function deleteComment() {

    const deleteButtons = document.querySelectorAll('.delete-comment-btn');
    console.log('Del Comment js feature loading');

    // Get CSRF token for AJAX calls
    function getCSRFToken() {
        console.log('getCSRFToken function called');
        console.log(`CSRF token: ${$('[name=csrfmiddlewaretoken]').val()}`);
        // CSRF token is usually stored in a hidden input field in the form... is it ?
        return $('[name=csrfmiddlewaretoken]').val();
    }

    function showMessage(message, type="success") {
        const messageContainer = $('#message-container');
        messageContainer.html(
            `<div class="alert alert-${type}">${message}</div>
            `
        );
        messageContainer.fadeIn();
        
        // Hide message after 3,5 seconds
        setTimeout(() => messageContainer.fadeOut(), 3500);
    }

    // On click: delete
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // preventDefault allow to not recharge the page
            const commentId = this.dataset.commentId;
            console.log(`comment id: ${commentId}`);
            
            // Send Ajax request with Fetch api
            fetch(`/comment/delete_comment/${commentId}/`, {
                method: 'DELETE',
                headers: {
                    // place the CSRF token in the header
                    // 'X-CSRFToken': button.dataset.csrfToken  // CSRF for Django
                    'X-CSRFToken': getCSRFToken() // CSRF for Django
                }
            })
            .then(response => {
                if (!response.ok) {  // If response is error (e.g., 400, 500), throw error
                    throw new Error(`Network response was not ok. status: ${response.status}`);
                }
                return response.json();  // Parse response JSON
            })
            .then(data => {
                if (data.success) {
                    // Remove the comment from the DOM
                    const commentBlock = document.getElementById(`comment-${commentId}`);
                    if (commentBlock) {
                        commentBlock.remove();
                    }
                    // Optionally, you can show a success message
                    showMessage(data.message, 'success');

                    console.log(`Comment ${commentId} deleted successfully.`);
                } else {
                    console.error('Error deleting comment:', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

document.addEventListener("DOMContentLoaded", deleteComment);