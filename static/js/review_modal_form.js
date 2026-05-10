function initReviewForm() {
    console.log(`Initializing review modal feature...`);
    // ========================== Review feature, in progress ====================================
    // ------ Listen for clicks on any element with class 'review-button'  -------
    // Step 1: the review-button is clicked, check if in_watchlist is True/false, 
    // open the modal and populate the form with existing data if exist, or show empty form if not exist.
    // Step 2: when user click confirm button in the modal, grab the form's data and 
    // send it with Fetch to the server, then check the response to update the button state and show a message.
    // Step 3: if user click cancel button, just close the modal and clear forms.

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


    // function clearFormAndPendingData() {
    //     // Clear the form and pending data when the modal is closed (either by cancel or close X button)
    //     document.getElementById('watchlistModal').addEventListener('hidden.bs.modal', function() {
    //         document.getElementById('watchlistForm').reset();
    //         pendingWatchlistData = null;  // wipe post-it too
    //     });
    // }


    const modal = new bootstrap.Modal(document.getElementById('reviewModal'));
    const modalTitle = document.getElementById('reviewModalTitle');
    // const cancelButton = document.getElementById('cancelWatchlistBtn');
    const confirmButton = document.getElementById('confirmReviewBtn');
    // const removeWatchlistBtn = document.getElementById('removeWatchlistBtn');
    
    let pendingReviewData = null; // allow to share the state and data of the watchlist

    // User click on the review button / open the modal,
    // Check if review instance already exist for this content, if exist, populate the form with the existing data and show the update button, if not, show empty form and add button.
    $(document).on('click', '.review-button', function(e) {
        console.log('review button clicked!');
        e.preventDefault();

        const button = $(this); 
        // const contentType = button.data('type'); // e.g. Model 'serie'
        const objectId = button.data('id'); // primary key
        const icon = button.find('i');
        const isExisting  = button.data('reviewed') === true; // check if the instance already exist
        const title = button.data('title'); // get the content title from the button data attribute to set the modal title

        // set the media title in the modal header
        // document.getElementById('watchlistModalTitle').textContent = title; 
        modalTitle.innerHTML = `
            <span style="color: rgb(180, 160, 130); font-style: italic;">
            ${title}
            </span>
        `;

        // Check if user is authenticated before doing anything else
        console.log(`USER_IS_AUTHENTICATED: ${USER_IS_AUTHENTICATED} `)
        if (!USER_IS_AUTHENTICATED) {
            // showMessage('You must be logged in to use the review system.', 'warning');
            document.getElementById('reviewGuestPanel').style.display = 'block';
            document.getElementById('reviewFormPanel').style.display  = 'none';
            modal.show();
            return;  // stops here, modal never opens
        }
        
        document.getElementById('reviewGuestPanel').style.display = 'none';
        document.getElementById('reviewFormPanel').style.display  = 'block';
        
        console.log(`Getting Media Object id: ${objectId}`);
        pendingReviewData = {objectId, icon, isExisting};

        if (isExisting) {
            // If already in watchlist, fetch the existing data to populate the form
            // and show the confirm button to update the watchlist instance.
            //  show the 'remove' button
            console.log(`Content already reviewed by user, fetching existing data to populate the form.`);

            // removeWatchlistBtn.style.display = 'block';

            fetch(`/review/toggle/${objectId}/`, {
                method: 'GET',
            })
            
            .then(r => r.json())
            .then(data => {
                // populateForm(data.review);
                console.log(
                    `Review data populated in the form.`,
                    `\n-note: ${data.review}\n-status: ${data.status}`
                );
                // setRemoveButtonVisible(true);
                // If data is null, we're clearing the form for a new entry
                document.getElementById('id_status').value = data ? data.status : '';
                document.getElementById('id_review').value = data ? data.review : '';
                document.getElementById('id_rewatch').value = data ? data.rewatch : '';
                document.getElementById('id_score').value = data ? data.score : '';
                confirmButton.textContent = 'Update'; // change the button text to indicate processing
            });

        } else {
            confirmButton.textContent = 'Save'; // change the button text to indicate processing
            // removeReviewBtn.style.display = 'none';
        }
        
        modal.show(); // Show the Bootstrap modal block
    });

    // Step 2: tracks confirm button and grab the form.
    // Track clicks on all conffirm buttons
    confirmButton.addEventListener('click', function (e) {
        e.preventDefault(); // preventDefault allow to not recharge the page

        if (!pendingReviewData) {
            // Need to check what it correspond to
            console.log(`Operation stopped! No media id provided or found.`)
            return;
        }

        //  Initialize variables for method, body, and headers to be used in the fetch request
        let method, body, headers; 

        const reviewForm = document.getElementById('reviewForm');    
        const formData = new FormData(reviewForm);

        const { contentType, objectId, icon, isExisting } = pendingReviewData;

        console.log(`Content type: ${contentType}, Object id: ${objectId} appended to form data.`);
        console.log(`Status: ${formData.get('status')}`);
        console.log(`Review: ${formData.get('review')}`);
        console.log(`Rewatch: ${formData.get('rewatch')}`);
        console.log(`Score: ${formData.get('score')}`);

        console.log(`Confirm saving review instance!`);
        // select the current modal element and closes it.
        bootstrap.Modal.getInstance(document.getElementById('reviewModal')).hide();

        // Construct the URL dynamically
        const url = `/review/toggle/${objectId}/`;
        console.log("AJAX request URL:", url); // Debugging

        // Implement POST/PUT request depending on if the instance already exist or not,
        //  and set the body and headers accordingly
        if (isExisting) {
            method = 'PUT';
            body = JSON.stringify({
                status: formData.get('status'),
                review: formData.get('review'),
                rewatch: formData.get('rewatch'),
                score: formData.get('score'),
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
    
            if (data.is_reviewed) {
                icon.removeClass('fa fa-star-o').addClass('fa fa-star');
                const button = icon.closest('.review-button');
                button.data('reviewed', true);

                // change the button text to indicate processing
                document.getElementById('confirmReviewBtn').textContent = 'Update'; 
                // removeWatchlistBtn.style.display = 'block';

            } else {
                icon.removeClass('fa fa-star').addClass('fa fa-star-o');
                // button.attr('data-bookmarked', 'false');
                confirmButton.textContent = 'Save review'; // change the button text to indicate processing
            }
    
            // Show success message  -- change between add and update
            showMessage(data.message, "success");
            console.log(`Successfully added to review`);
            
            // Add animation effect    ----- seem to work only on the first instance of object, need to debug. ----
            icon.addClass('pulse');
            setTimeout(() => icon.removeClass('pulse'), 1000);
        })

        .catch(error => {
            console.error('Error', error);
            alert('Failed to save the review, please reload the page')
        })

        .finally(() => {
            pendingReviewData = null
            // clear the form
            reviewForm.reset();
        });

    });

    // When user click the remove button, 
    // send a DELETE request to the server to remove the instance from the watchlist,
    // removeReviewBtn.addEventListener('click', function(e) {
    //     e.preventDefault();

    //     if (!pendingReviewData) {
    //         console.log(`Operation stopped! No content type or object id provided or found.`)
    //         return;
    //     }

    //     const { contentType, objectId, icon, isExisting } = pendingReviewData;

    //     // Construct the URL dynamically
    //     const url = `/review/toggle/${objectId}/`;
    //     console.log("AJAX request URL:", url); // Debugging

    //     // select the current modal element and closes it.
    //     bootstrap.Modal.getInstance(document.getElementById('reviewModal')).hide();

    //     // Send Ajax request with Fetch api
    //     fetch(url, {
    //         method: 'DELETE',
    //         headers: {
    //             'X-CSRFToken': getCSRFToken() // CSRF for Django
    //         }
    //     })
    
    //     .then(response => {
    //         if (!response.ok) {  // If response is error (e.g., 400, 500), throw error
    //             throw new Error(`Network response was not ok. status: ${response.status}`);
    //         }
    //         return response.json();  // Parse response JSON
    //     })
    
    //     .then(data => {
    //         if (!data.in_watchlist) {
    //             icon.removeClass('fa fa-bookmark').addClass('far fa-bookmark');
    //             const button = icon.closest('.watchlist-button');
    //             button.data('bookmarked', false);

    //             document.getElementById('confirmWatchlistBtn').textContent = 'Add to Watchlist'; // change the button text to indicate processing
    //             removeReviewBtn.style.display = 'none';

    //             // Show success message
    //             showMessage(data.message, 'success');
    
    //             console.log(`Successfully removed from watchlist`);
    //         } else {
    //             console.error('Error removing from watchlist:', data.message);
    //         }
    //     })
    
    //     .catch(error => {
    //         console.error('Error:', error);
    //         alert('Failed to remove from watchlist, please reload the page')
    //     })

    //     .finally(() => {
    //         pendingReviewData = null;
    //         // clear the form
    //         document.getElementById('reviewForm').reset();
    //     });
    // });

    // Clear the form and pending data when the modal is closed (either by cancel or close X button)
    document.getElementById('reviewModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('reviewForm').reset();
        pendingWatchlistData = null;  // wipe post-it too
    });

}

document.addEventListener('DOMContentLoaded', initReviewForm);