$(document).ready(function() {
    console.log('Script loaded!');

    // Get CSRF token for AJAX calls
    function getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val();
    }
    

    function showMessage(message, type="success") {
        const messageContainer = $('#message-container');
        messageContainer.html(`<div class="alert alert-${type}">${message}</div>`);
        messageContainer.fadeIn();
        
        // Hide message after 3 seconds
        setTimeout(() => messageContainer.fadeOut(), 3000);
    }


    // Listen for clicks on any element with class 'like-button'
    $('.like-button').click(function(e) {
        console.log('Like button clicked!');
        e.preventDefault();
        
        const button = $(this);
        const contentType = button.data('type'); // e.g., 'serie'
        const objectId = button.data('id'); // e.g., '2'

        // Construct the URL dynamically
        const url = `/user_library/like/${contentType}/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging


        $.ajax({
            url: url,
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken() // include CSRF token
            },

            success: function(response) {
                console.log('Server responded:', response); // debug console

                // Toggle button text and icon when the server responds successfully
                const likeText = button.find('.like-text');
                const icon = button.find('i');
                
                if (response.liked) {
                    likeText.text('Unlike');
                    icon.addClass('liked');
                } else {
                    likeText.text('Like');
                    icon.removeClass('liked');
                }

                // Show success message
                showMessage(response.message, "success");
                
                // Add animation effect
                button.addClass('pulse');
                setTimeout(() => button.removeClass('fa-spin-pulse'), 1500);
            },

            // Handle errors messages
            error: function(xhr) {
                console.error('Error:', xhr.responseText);
            
                // Default error message
                let errorMessage = "An error occurred.";
                let errorType = "danger";  // Default to red alert
            
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
            
                    // If the error is "Login required / user not authenticated", show a warning instead of danger
                    if (xhr.status === 401) {
                        errorType = "warning";  // Yellow alert for login required
                    }
                }
            
                // Show error message with the correct type
                showMessage(errorMessage, errorType);

                // Hide message after 3 seconds
                setTimeout(() => messageContainer.fadeOut(), 3000);
            }


        });
    });
});