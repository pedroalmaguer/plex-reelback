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

function loadContent(endpoint, title) {
    console.log(`Fetching content from ${endpoint}`); // Debug log
    fetch(endpoint, { method: 'POST' })
        .then(response => {
            console.log(`Response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            console.log("Content loaded successfully");
            document.querySelector('.stats-content').innerHTML = html;
        })
        .catch(error => {
            console.error(`Error loading content from ${endpoint}:`, error);
            document.querySelector('.stats-content').innerHTML = 
                `<div class="error">Failed to load content. Please try refreshing.</div>`;
        });
}
