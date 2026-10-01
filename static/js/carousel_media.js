(function () {

    let hoverTimer = null;

    const CARD = '.carousel-card .media-card';

    // true on mouse/trackpad devices, false on touch-only devices
    const canHover = window.matchMedia('(hover: hover) and (pointer: fine)');

    // document.querySelectorAll(CARD).forEach(card => {
        // initialize hover timer
    console.log(`All carousel cards loaded`)

    document.addEventListener('mouseover', (e) => {
        // card.addEventListener('mouseover', () => {
        if (!canHover.matches) return;  // ignore emulated mouse events on touch
        // Cancel any pending timer from a previous card
        const card = e.target.closest(CARD);
        if (!card || card.contains(e.relatedTarget)) return;

        clearTimeout(hoverTimer);

        // Set a timer befor the hovered transition/animation starts
        // hoverTimer = setTimeout(() => {
        card.classList.add('is-hovered');
        console.log(`mouse hover, adding attr: is-hovered`)

        // }, 2500);
    });


    // When mouse leave the hovered item. Reset all transition to 'normal'
    document.addEventListener('mouseout', (e) => {
        const card = e.target.closest(CARD);
        if (!card || card.contains(e.relatedTarget)) return;

        clearTimeout(hoverTimer); // cancel if moved away before 2s
        card.classList.remove('is-hovered', 'is-active');
        // card.classList.remove('is-hovered', 'is-active');
        console.log(`remove cls attr: is-active & is-hovered`)
    });



    // For mobile screen and click instead of hover 
    // Also allow cancelling transition/animation on Larger screen when clickking on the hovered card
    document.addEventListener('click', (e) => {
        const card = e.target.closest(CARD);
        if (!card) return;

        if (card.classList.contains('is-hovered')) {
            // clearTimeout(hoverTimer);
            // card.classList.remove('is-hovered');
            if (card.classList.contains('is-active')) {
                console.log(`class contains: is-active cls attr -- Removing attr.`);
                card.classList.remove('is-active');
            } else {
                clearTimeout(hoverTimer);
                hoverTimer = setTimeout(() => card.classList.add('is-active'), 250);
                console.log(`adding cls attr: is-active`);
            }

        } else {
            clearTimeout(hoverTimer); // cancel if moved away before 2s
            hoverTimer = setTimeout(() => card.classList.add('is-hovered'), 1250);
            console.log(`adding cls attr: is-hovered`);
        }
    });

}) ();