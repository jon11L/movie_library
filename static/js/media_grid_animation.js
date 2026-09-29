let hoverTimer = null;

document.querySelectorAll('.media-grid .media-card').forEach(card => {
    // initialize hover timer

    card.addEventListener('mouseenter', () => {
        // Cancel any pending timer from a previous card
        clearTimeout(hoverTimer);

        // Set a timer befor the hovered transition/animation starts
        hoverTimer = setTimeout(() => {
            card.classList.add('is-hovered');
            console.log(`mouse hover, adding attr: is-hovered`)
        }, 0);
    });

    // When mouse leave the hovered item. Reset all transition to 'normal'
    card.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimer);
        card.classList.remove('is-hovered');
        card.classList.remove('is-active');
        console.log(`remove cls attr: is-active & is-hovered`)
    });

    // For mobile screen and click instead of hover 
    // Also allow cancelling transition/animation on Larger screen when clickking on the hovered card
    card.addEventListener("click", () => {
        if (card.classList.contains("is-hovered")) {
        // -- removing the is_active if clicked again --
            if (card.classList.contains("is-active")) {
                console.log(`class contains: is-active cls attr -- Removing attr.`);
                // adding the 2nd step focus on an image, separating is-hovered with is-active
                card.classList.remove("is-active");

            // clearTimeout(hoverTimer);
            // card.classList.remove('is-hovered');
            } else {
                clearTimeout(hoverTimer); // cancel if moved away before 2s
                hoverTimer = setTimeout(() => {
                card.classList.add("is-active");
                console.log(`adding cls attr: is-active`);
                }, 250);
            }
        } else {
            clearTimeout(hoverTimer); // cancel if moved away before 2s
            console.log(`adding cls attr: is-hovered`);
            hoverTimer = setTimeout(() => {
                card.classList.add("is-hovered");
            }, 1000);
        }
    });
});