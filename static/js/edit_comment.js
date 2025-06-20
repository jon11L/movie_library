function editComment() {
    // allow to edit comment without refreshing page
    // and display the edited comment
    console.log('edit comment feature loaded');

    function closeAllEdits() {
        // Prevent from opening several edit comment form, Ensure one Edit form at a time 
        document.querySelectorAll('.edit-comment-block').forEach(div => div.style.display = 'none');
        document.querySelectorAll('.comment-buttons').forEach(div => div.style.display = 'block');
        document.querySelectorAll('.comment-body').forEach(div => div.style.display = 'block');
    }
    
    function showMessage(message, type="success") {
        // this  allow to display pop up message based on the success action.
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
        setTimeout(() => messageContainer.fadeOut(), 3500);
    }
    
    const editButtons = document.querySelectorAll('.edit-comment-form-btn');
    // Click on edit button to trigger the edit form
    editButtons.forEach(editBtn => {

        // This is to prevent editbutton being reattach with an handler when a new comment is posted
        // Ensuring Only once the edit button is triggered // same for submit
        if (editBtn.dataset.bound === 'true') {
            console.log("the button is already bound.");
            return;
        } else {
            editBtn.dataset.bound = 'true';
            console.log("Adding the bound on editbutton.");
        }


        editBtn.addEventListener('click', function (){
            //  display the new edit form with the current text comment(body) 
            // and hide plain text

            // Get CSRF token for AJAX calls
            function getCSRFToken() {
                console.log('getCSRFToken function called');
                // console.log(`CSRF token: ${$('[name=csrfmiddlewaretoken]').val()}`);
                return $('[name=csrfmiddlewaretoken]').val();
            }
            
            // fetch the comment.id
            const commentId = this.dataset.commentId;
            const originalBody = this.dataset.commentBody;

            // Get the whole comment block from where the edit-btn was clicked
            const commentBlock = document.getElementById(`comment-${commentId}`);

            console.log(`edit feature for comment ${commentId} opened.`)
            console.log(`original body-text: ${originalBody}`);

            
            const createdAt = commentBlock.querySelector('.created-at')

            // Remove any other Edit and delete button while on editing mode.
            closeAllEdits();

            //  Show edit form and hide original text & buttons 
            commentBlock.querySelector('.comment-body').style.display = 'none';
            document.querySelectorAll('.comment-buttons').forEach(div => div.style.display = 'none');
            commentBlock.querySelector('.edit-comment-block').style.display = 'block';
            
            // Get the textarea and set its value to the original text of the comment
            const textarea = commentBlock.querySelector('textarea[name="body"]');
            textarea.value = originalBody;
            
            // Cancel button on edit comments / return to origin DOM.
            const cancelButton = commentBlock.querySelector('.cancel-btn');
            // cancelButtons.forEach(button => {
                // cancelButton.addEventListener('click', function() {
                cancelButton.onclick = function() {
                // button.addEventListener('click', function() {
                    closeAllEdits();
                    textarea.value = originalBody;

                    // if (editBtn.dataset.bound === 'true') {
                    //     console.log("editbutton Bound needs to be removed");
                    //     editBtn.dataset.bound = 'false';
                    //     console.log("removing the bound");
                    // }

                    console.log('User canceled the comment editing.');
                };
            // });


            const submitButton = commentBlock.querySelector('button[type="submit"]');
            // Check if submitButton was already having and listener handler. 
            // if so then pass, to avoid multiple handlers being attached to.
            if (submitButton.dataset.bound !== 'true') {
                submitButton.dataset.bound = 'true';

                // Submit button once edit comments form is opened.
                submitButton.addEventListener('click', function(e) {
                    console.log('submit button clicked!!!!!');
                    e.preventDefault(); // preventDefault allow the page to not reload on execution

                    // fetch the info from the data attribute in the button
                    const contentType = submitButton.dataset.contentType;  // 'movie' or 'serie'
                    const objectId = submitButton.dataset.objectId; // Id of the object.
                    // console.log(`Submit Button contains the following: ${formData}`);
                    console.log(`content type: ${contentType}`);
                    console.log(`object id: ${objectId}`);
                    console.log(`the comment id: ${commentId}`);

                    // get the new edited form.body that was passed from html
                    const new_body = textarea.value;
                    console.log(`form body: ${new_body}`);

                    // send the data to the server via Fetch API
                    fetch(`/comment/edit/${commentId}/`, {
                        method: 'PUT',
                        headers: {
                        'X-CSRFToken': getCSRFToken() // CSRF for Django
                        },
                        // need to figure out what to pass here..
                        body: JSON.stringify({body: new_body})
                    }) 

                    .then(response => {
                        if (!response.ok) {  // If response is error (e.g., 400, 500), throw error
                            throw new Error(`Network response was not ok. status: ${response.status}`);
                        }
                        console.log('response ok');
                        console.log(`response: ${response}`);
                        return response.json();  // Parse response JSON
                    })
                    //  if return is successful then update the DOM. 
                    .then(data => {
                        if (data.success) {
                            // Update the comment body in the DOM
                            if (commentBlock) {
                                const commentBody = commentBlock.querySelector('.comment-body');
                                commentBody.innerHTML = `<p>${new_body}</p>`; // Update the comment body
                                closeAllEdits();

                                // hide the edit button and display'edited'
                                // selectEdit.style.display = "none";
                                editBtn.style.display = "none"; // hide the current edit button that was triggered

                                createdAt.insertAdjacentHTML("afterbegin" ,`
                                <p style="margin-right: 8px;">(Edited) </p>
                                `);

                                console.log(`Comment ${commentId} edited successfully.`);
                                showMessage(data.message, 'success');
                            } else {
                                console.error(`No comment block found for ID comment-${commentId}`);
                                showMessage("Edit Failed...", "danger")
                            }
                        }
                    })

                .catch(error => {
                    console.error('Error', error);
                    // alert('Failed to edit the comment, please reload the page');
                    showMessage('Failed to edit the comment, please reload the page', 'danger')
                })

                });
            }
        });
        
    });
}

document.addEventListener("DOMContentLoaded", editComment);
