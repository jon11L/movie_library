$(document).ready(function() {
    console.log('Script loaded!');


    // Get CSRF token for AJAX calls
    function getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val();
    }
    
    function showMessage(message, type="success") {
        const messageContainer = $('#message-container');
        messageContainer.html(
            `<div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            `
        );
        messageContainer.fadeIn();
        
        // Hide message after 3,5 seconds
        setTimeout(() => messageContainer.fadeOut(), 4000);
    }


    // ==== Listen for clicks on any element with class 'like-button' =========
    $('.like-button').click(function(e) {
        console.log('Like button clicked!');
        e.preventDefault(); // Prevent the page from reloading
        
        const button = $(this);
        const contentType = button.data('type'); // e.g., 'serie'
        const objectId = button.data('id'); // e.g., '2'
        const icon = button.find('i');

        // Construct the URL dynamically
        const url = `/library/like/${contentType}/${objectId}/`;
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
    //  ======= End of like function part ========

    // ========================== Watchlist feature, in progress ====================================
    // ------ Listen for clicks on any element with class 'watchlist-button'  -------
    // Step 1: the watchlist button is clicked, check if in_watchlist True/false, open the modal
    // Step 2: when user click confirm button in the modal, grab the form data and 
    // send it with Fetch to the server, then check the response to update the button state and show a message.
    // Step 3: if user click cancel button, just close the modal and clear forms.

    const modal = new bootstrap.Modal(document.getElementById('watchlistModal'));
    // const modalTitle = document.getElementById('WatchlistToggleModalLabel');
    const modalTitle = document.getElementById('watchlistModalTitle');
    // const cancelButton = document.getElementById('cancelWatchlistBtn');
    const confirmButton = document.getElementById('confirmWatchlistBtn');
    const removeWatchlistBtn = document.getElementById('removeWatchlistBtn');

    // allow to share the state and data of the watchlist
    let pendingWatchlistData = null;

    // User click on the watchlist button / open the modal,
    // Check if watchlist instance already exist for this content, if exist, populate the form with the existing data and show the update button, if not, show empty form and add button.
    $('.watchlist-button').click(function(e) {
        console.log('Watchlist button clicked!');
        e.preventDefault();
        
        // Check if user is authenticated before doing anything else
        console.log(`USER_IS_AUTHENTICATED: ${USER_IS_AUTHENTICATED} `)
        if (!USER_IS_AUTHENTICATED) {
            showMessage('You must be logged in to use the Watchlist.', 'warning');
            return;  // stops here, modal never opens
        }
        
        const button = $(this); 
        const contentType = button.data('type'); // e.g. Model 'serie'
        const objectId = button.data('id'); // primary key
        const icon = button.find('i');
        const isExisting  = button.data('bookmarked') === true; // check if the instance already exist

        console.log(`Getting Media type: ${contentType} and Object id: ${objectId}`);
        pendingWatchlistData = {contentType, objectId, icon, isExisting};

        if (isExisting) {
            // If already in watchlist, fetch the existing data to populate the form
            // and show the confirm button to update the watchlist instance.
            //  show the 'remove' button
            console.log(`Content already in user's watchlist, fetching existing data to populate the form.`);

            removeWatchlistBtn.style.display = 'block';
            modalTitle.innerHTML = `
                Edit  
                <span style="color: rgb(180, 160, 130); font-style: italic;">
                ${button.data('title')}
                </span>
            `;

            fetch(`/library/watchlist/${contentType}/${objectId}/`, {
                method: 'GET',
            })
            
            .then(r => r.json())
            .then(data => {
                // populateForm(data.watchlist_data);
                console.log(`Watchlist data populated in the form: ${data.personal_note}`);
                // setRemoveButtonVisible(true);
                // If data is null, we're clearing the form for a new entry
                document.getElementById('id_personal_note').value = data ? data.personal_note : '';
                document.getElementById('id_status').value = data ? data.status : '';
                confirmButton.textContent = 'Update'; // change the button text to indicate processing
            });

        } else {
            // If not in watchlist, hide the remove button in the modal
            modalTitle.innerHTML = `
                Add to Watchlist 
                <span style="color: rgb(180, 160, 130); font-style: italic;">
                ${button.data('title')}
                </span>
            `;

            confirmButton.textContent = 'Save'; // change the button text to indicate processing
            removeWatchlistBtn.style.display = 'none';
        }
        
        modal.show(); // Show the Bootstrap modal block
    });

    // Step 2: tracks confirm button and grab the form.
    // Track clicks on all conffirm buttons
    confirmButton.addEventListener('click', function (e) {
        e.preventDefault(); // preventDefault allow to not recharge the page

        if (!pendingWatchlistData) {
            console.log(`Operation stopped! No comment id provided or found.`)
            return;
        }

        //  Initialize variables for method, body, and headers to be used in the fetch request
        let method, body, headers; 

        const watchlistForm = document.getElementById('watchlistForm');    
        const formData = new FormData(watchlistForm);

        const { contentType, objectId, icon, isExisting } = pendingWatchlistData;

        console.log(`Content type: ${contentType}, Object id: ${objectId} appended to form data.`);
        console.log(`Personal note: ${formData.get('personal_note')}`);
        console.log(`Status: ${formData.get('status')}`);

        console.log(`Confirm saving watchlist instance!`);
        // select the current modal element and closes it.
        bootstrap.Modal.getInstance(document.getElementById('watchlistModal')).hide();

        // Construct the URL dynamically
        const url = `/library/watchlist/${contentType}/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging

        // Implement POST/PUT request depending on if the instance already exist or not,
        //  and set the body and headers accordingly
        if (isExisting) {
            method = 'PUT';
            body = JSON.stringify({
                personal_note: formData.get('personal_note'),
                status: formData.get('status'),
            });
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // include CSRF token
            };
        
        }   else {
            method = 'POST';
            body = formData; // for POST, we can send the FormData directly
            headers = {
                'X-CSRFToken': getCSRFToken() // include CSRF token
            };
        }

        // Step 3 send the form with fetch api, as POST/UPDATE and check the result.
        fetch(url, { method: method, body: body, headers: headers,})
        
        .then(response => {
            if (!response.ok) {  // If response is error (e.g., 400, 500), throw error
                throw new Error(`Network response was not ok. status: ${response.status}`);
            }
            return response.json();  // Parse response JSON
        })

        .then(data => {

            console.log(data)
            modal.hide()
    
            if (data.in_watchlist) {
                icon.removeClass('far fa-bookmark').addClass('fa fa-bookmark');
                const button = icon.closest('.watchlist-button');
                button.data('bookmarked', true);

                // change the button text to indicate processing
                document.getElementById('confirmWatchlistBtn').textContent = 'Update'; 
                removeWatchlistBtn.style.display = 'block';

            } else {
                icon.removeClass('fa fa-bookmark').addClass('far fa-bookmark');
                // button.attr('data-bookmarked', 'false');
                confirmButton.textContent = 'Add to Watchlist'; // change the button text to indicate processing
            }
    
            // Show success message  -- change between add and update
            showMessage(data.message, "success");
            console.log(`Successfully added to watchlist`);
            
            // Add animation effect    ----- seem to work only on the first instance of object, need to debug. ----
            icon.addClass('pulse');
            setTimeout(() => icon.removeClass('pulse'), 1000);
        })

        .catch(error => {
            console.error('Error', error);
            alert('Failed to save the watchlist, please reload the page')
        })

        .finally(() => {
            pendingWatchlistData = null
            // clear the form
            watchlistForm.reset();
        });

    });

    removeWatchlistBtn.addEventListener('click', function(e) {
        e.preventDefault();

        if (!pendingWatchlistData) {
            console.log(`Operation stopped! No content type or object id provided or found.`)
            return;
        }

        const { contentType, objectId, icon, isExisting } = pendingWatchlistData;

        // Construct the URL dynamically
        const url = `/library/watchlist/${contentType}/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging

        // select the current modal element and closes it.
        bootstrap.Modal.getInstance(document.getElementById('watchlistModal')).hide();

        // Send Ajax request with Fetch api
        fetch(url, {
            method: 'DELETE',
            headers: {
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
            if (!data.in_watchlist) {
                icon.removeClass('fa fa-bookmark').addClass('far fa-bookmark');
                const button = icon.closest('.watchlist-button');
                button.data('bookmarked', false);

                document.getElementById('confirmWatchlistBtn').textContent = 'Add to Watchlist'; // change the button text to indicate processing
                removeWatchlistBtn.style.display = 'none';

                // Show success message
                showMessage(data.message, 'success');
    
                console.log(`Successfully removed from watchlist`);
            } else {
                console.error('Error removing from watchlist:', data.message);
            }
        })
    
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to remove from watchlist, please reload the page')
        })

        .finally(() => {
            pendingWatchlistData = null;
            // clear the form
            document.getElementById('watchlistForm').reset();
        });
    });

    // Clear the form and pending data when the modal is closed (either by cancel or close X button)
    document.getElementById('watchlistModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('watchlistForm').reset();
        pendingWatchlistData = null;  // wipe post-it too
    });


});

