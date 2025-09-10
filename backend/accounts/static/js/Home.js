// User data will be loaded from Django template
// No need for hardcoded user data anymore

document.getElementById('userMarker').addEventListener('click', function() {
    const userDetails = document.getElementById('userDetails');
    userDetails.classList.toggle('active');
});

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Images and user data are now set by Django template
    // No need to override them with JavaScript
    console.log('Home page loaded with Django template data');
    
    // Debug: Check if elements exist
    const userName = document.getElementById('userName');
    const userDetailName = document.getElementById('userDetailName');
    const userDetailLocation = document.getElementById('userDetailLocation');
    
    console.log('userName element:', userName);
    console.log('userDetailName element:', userDetailName);
    console.log('userDetailLocation element:', userDetailLocation);
    
    if (userName) {
        console.log('userName textContent:', userName.textContent);
    }
    if (userDetailName) {
        console.log('userDetailName textContent:', userDetailName.textContent);
    }
    if (userDetailLocation) {
        console.log('userDetailLocation textContent:', userDetailLocation.textContent);
    }
});


function setRealVH() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  window.addEventListener('resize', setRealVH);
  window.addEventListener('load', setRealVH);