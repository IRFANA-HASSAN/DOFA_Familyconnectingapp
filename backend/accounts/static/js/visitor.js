document.addEventListener("DOMContentLoaded", function() {
    const token = localStorage.getItem('authToken'); // Check for login token
    const hasVisited = localStorage.getItem('hasVisited'); // Check for first-time visit

    const messageElement = document.getElementById('message'); // You can change this ID to wherever you want to show the message

    if (token) {
        // If logged in, show logged-in message
        messageElement.innerText = 'Welcome back, you are logged in!';
    } else if (!hasVisited) {
        // If first visit, show first-time visitor message
        localStorage.setItem('hasVisited', 'true'); // Set the hasVisited flag
        messageElement.innerText = 'Welcome! It looks like you are a first-time visitor.';
    } else {
        // For other cases (returning visitor without login)
        messageElement.innerText = 'Welcome back!';
    }
});
