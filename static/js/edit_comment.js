    // ------------- Edit comment form directly into the current post --------------
    // document.addEventListener("DOMContentLoaded", function () {
    function editComment() {

        const editButtons = document.querySelectorAll('.edit-comment-btn');
        console.log('edit comment loaded');
        // const cancelButtons = document.querySelectorAll('.cancel-btn');

        // Prevent from opening several edit comment form, Ensure one Edit form at a time 
        function closeAllEdits() {
            document.querySelectorAll('.edit-comment-form').forEach(div => div.style.display = 'none');
            document.querySelectorAll('.comment-buttons').forEach(div => div.style.display = 'block');
            document.querySelectorAll('.comment-body').forEach(div => div.style.display = 'block');
        }
        
        // On click edit
        editButtons.forEach(button => {
            button.addEventListener('click', function (){
                // fetch the comment.id
                const commentId = this.dataset.commentId;
                const originalBody = this.dataset.commentBody;
                // console.log(`comment id: ${commentId}`);
                console.log(`original new comment body: ${originalBody}`);
                
                // Close possible other edit
                closeAllEdits();
                
                //  display the new edit form with the current comment.b and hide plain text
                const commentBlock = document.getElementById(`comment-${commentId}`);
        
                // Check if the commentBlock exists
                if (!commentBlock) {
                    console.error(`No comment block found for ID comment-${commentId}`);
                    return;
                } else {
                    console.log(`comment block found for ID comment-${commentId}`);
                }

                commentBlock.querySelector('.comment-body').style.display = 'none';
                document.querySelectorAll('.comment-buttons').forEach(div => div.style.display = 'none');
                commentBlock.querySelector('.edit-comment-form').style.display = 'block';
                
                const textarea = commentBlock.querySelector('textarea[name="body"]');
                textarea.value = originalBody;
                
                // Cancel button on edit comments.
                const cancelButtons = document.querySelectorAll('.cancel-btn');
                cancelButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        closeAllEdits();
                        textarea.value = originalBody;

                    });
                });

            });
        });
    }


document.addEventListener("DOMContentLoaded", editComment);
