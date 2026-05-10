function createComment() {
    console.log('Add Comment feature loaded');

    // const postComment = this.querySelector('.comment-post-section');
    const postComment = this.querySelector('.comment-list-section');
    const commentForm = this.getElementById('comment-form');

    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            e.preventDefault(); // preventDefault allow to not recharge the page
            
            // get the form data object
            const formData = new FormData(commentForm);            
            // fetch the info from the data attribute in the button
            const submitButton = commentForm.querySelector('button[type="submit"]');
            const mediaId = submitButton.dataset.mediaId; // Id of the object.

            console.log(`Submit Button contains the following: ${formData}`);
            // get the form.body that was passed from html
            const formBodyValue = formData.get('body');
            console.log(`form body: ${formBodyValue}`);
            
            console.log(`commend made on media: ${mediaId}`);
            formData.append('media', mediaId);
            
            console.log(`datas stored in 'formData' sending the request by POST`);
            // send Ajax request with Fetch api
            fetch('/comment/create', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')  // CSRF for Django
                },
                body: formData
            })

            .then(response => {
                if (!response.ok) {  // If response is error (e.g., 400, 500), throw error
                    console.log(`Network response was not ok. status: ${response.status}`)
                    throw new Error(`Network response was not ok. status: ${response.status}`);
                }
                return response.json();  // Parse response JSON
            })

            // Data from the response.json
            .then(data => {
                if (data.success) {
                    // insert the new comment into the comment section
                    postComment.insertAdjacentHTML('afterbegin', data.comment_html);
                    
                    // call the editComment();
                    if (typeof editComment === 'function') {
                        editComment();
                    }
                    if (typeof deleteComment === 'function') {
                        deleteComment();
                    }

                    // Show success message
                    const messageContainer = document.getElementById('comment-form');
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success alert-dismissible fade show';
                    alert.style = 'width: fit-content; margin: auto;';
                    alert.innerHTML = `
                        Comment posted!
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
                        </button>
                    `;
                    // messageContainer.appendChild(alert);
                    messageContainer.insertAdjacentElement('beforeend', alert);

                    // Auto dismiss after 3.5 seconds (like in your base.html)
                    setTimeout(() => {
                        let bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                        bsAlert.close();
                    }, 3500);
                    console.log(`*New comment posted* - ${formBodyValue}`);
                }
            })
        .catch(error => {
            console.error('Error', error);
            alert('Failed to post the comment, please reload the page')
        })
        .finally(() => {
            commentForm.reset(); // Clear the comment form after submission
        });

        });

    };

}


document.addEventListener("DOMContentLoaded", createComment);