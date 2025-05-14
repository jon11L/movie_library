$(document).ready(function() {
    console.log('Script loaded!');

    // Get CSRF token for AJAX calls
    function getCSRFToken() {
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


    // Listen for clicks on any element with class 'like-button'
    $('.like-button').click(function(e) {
        console.log('Like button clicked!');
        e.preventDefault(); // Prevent the page from reloading
        
        const button = $(this);
        const contentType = button.data('type'); // e.g., 'serie'
        const objectId = button.data('id'); // e.g., '2'
        const icon = button.find('i');

        // Construct the URL dynamically
        const url = `/user_library/like/${contentType}/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging

        // Disable button during request to prevent double-clicks
        button.prop('disabled', true);


        $.ajax({
            url: url,
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken() // include CSRF token
            },

            success: function(response) {
                console.log('Server responded:', response); // debug console
                
                
                // Toggle button text and icon when the server responds successfully
                if (response.liked) {
                    icon.removeClass('far fa-heart')
                        .addClass('fa fa-heart liked');
                        button.attr('data-liked', 'true');
                    } else {
                        icon.removeClass('fa fa-heart liked')
                            .addClass('far fa-heart');
                        button.attr('data-liked', 'false');
                }

                // Show success message
                showMessage(response.message, "success");
                
                // Add animation effect    ----- does not seem to work, need to debug. ----
                icon.addClass('pulse');
                setTimeout(() => button.removeClass('pulse'), 1000);
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
            },
            
            complete: function() {
                // Re-enable button after request completes
                button.prop('disabled', false);
                
            }

        });
    });


    //-------------- Watchlist feature, in progress -------------------

    // Listen for clicks on any element with class 'watchlist-button'
    $('.watchlist-button').click(function(e) {
        console.log('Watchlist button clicked!');
        e.preventDefault();
        
        const button = $(this);
        const contentType = button.data('type'); // e.g., 'serie'
        const objectId = button.data('id'); // e.g., '2'
        const icon = button.find('i');

        // Construct the URL dynamically
        const url = `/user_library/watchlist/${contentType}/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging

        // Disable button during request to prevent double-clicks
        button.prop('disabled', true);

        $.ajax({
            url: url,
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken() // include CSRF token
            },
            
            success: function(response) {
                console.log('Server responded:', response); // debug console
                
                // Toggle button text and icon when the server responds successfully
            if (response.in_watchlist) {
                icon.removeClass('far fa-bookmark')
                    .addClass('fa fa-bookmark');
                    // button.attr('data-bookmarked', 'true');
                } else {
                    icon.removeClass('fa fa-bookmark')
                    .addClass('far fa-bookmark');
                    // button.attr('data-bookmarked', 'false');
                }
                
                // Show success message
                showMessage(response.message, "success");
                
                // Add animation effect    ----- seem to work only on the first instance of object, need to debug. ----
                icon.addClass('pulse');
                setTimeout(() => button.removeClass('pulse'), 1000);
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
            },
            
            complete: function() {
                // Re-enable button after request completes
                button.prop('disabled', false);
                
            }
            
    //------------------- end of TRial for watchlist-------------------------
        });
    });


});

