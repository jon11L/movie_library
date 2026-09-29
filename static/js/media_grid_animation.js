(function () {
    
    let hoverTimer = null;
    const CARD = '.media-grid .media-card';

    // true on mouse/trackpad devices, false on touch-only devices
    const canHover = window.matchMedia('(hover: hover) and (pointer: fine)');

    document.addEventListener('mouseover', (e) => {
        if (!canHover.matches) return;  // ignore emulated mouse events on touch

        const card = e.target.closest(CARD);
        if (!card || card.contains(e.relatedTarget)) return;

        clearTimeout(hoverTimer);
        card.classList.add('is-hovered');
        console.log(`mouse hover, adding attr: is-hovered`)
    });


    document.addEventListener('mouseout', (e) => {
        const card = e.target.closest(CARD);
        if (!card || card.contains(e.relatedTarget)) return;

        clearTimeout(hoverTimer);
        card.classList.remove('is-hovered', 'is-active');
        console.log(`remove cls attr: is-active & is-hovered`)
    });


    // Click: mobile support + 2nd-step focus on desktop
    document.addEventListener('click', (e) => {
        const card = e.target.closest(CARD);
        if (!card) return;

        if (card.classList.contains('is-hovered')) {
            if (card.classList.contains('is-active')) {
                console.log(`class contains: is-active cls attr -- Removing attr.`);
                card.classList.remove('is-active');
            } else {
                clearTimeout(hoverTimer);
                hoverTimer = setTimeout(() => card.classList.add('is-active'), 250);
                console.log(`adding cls attr: is-active`);
            }

        } else {
            clearTimeout(hoverTimer);
            hoverTimer = setTimeout(() => card.classList.add('is-hovered'), 250);
            console.log(`adding cls attr: is-hovered`);
        }
    });
    
})();
