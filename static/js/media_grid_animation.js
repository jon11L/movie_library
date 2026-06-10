document.querySelectorAll('.media-grid .media-card').forEach(card => {
    // initialize hover timer
    let hoverTimer = null;

    card.addEventListener('mouseenter', () => {
        // Cancel any pending timer from a previous card
        clearTimeout(hoverTimer);

        // console.log('card being hovered')

        // Set a timer befor the hovered transition/animation starts
        hoverTimer = setTimeout(() => {
            card.classList.add('is-hovered');
        }, 2500);
    });

    // When mouse leave the hovered item. Reset all transition to 'normal'
    card.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimer); // cancel if moved away before 2s
        card.classList.remove('is-hovered');
    });

    // For mobile screen and click instead of hover 
    // Also allow cancelling transition/animation on Larger screen when clickking on the hovered card
    card.addEventListener('click', () => {
        if (card.classList.contains('is-hovered')) {
            clearTimeout(hoverTimer);
            card.classList.remove('is-hovered');
        }
            else {
                hoverTimer = setTimeout(() => {
                    card.classList.add('is-hovered');
                }, 1250);

            }
    });

});