console.log('Navigation script loaded');

function handlePageTransition(event) {
    event.preventDefault();
    console.log('Transition triggered');
    const nextPage = event.target.closest('a').href;
    
    const mainElement = document.querySelector('main');
    console.log('Before adding class:', mainElement.classList.toString());
    mainElement.classList.add('page-transition-active');
    console.log('After adding class:', mainElement.classList.toString());
    
    // Force a reflow to ensure the animation triggers
    void mainElement.offsetHeight;
    
    setTimeout(() => {
        window.location.href = nextPage;
    }, 2000); // Increased to 2 seconds for testing
}

// Handle scroll events
function handleScroll(event) {
    // Your scroll handling code here
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Adding event listeners');
    
    // Navigation links
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', handlePageTransition, { passive: false });
    });
    
    // Scroll events
    window.addEventListener('scroll', handleScroll, { passive: true });
    document.addEventListener('touchmove', handleScroll, { passive: true });
}); 