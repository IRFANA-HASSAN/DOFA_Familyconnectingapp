let selectedUserId = null;
let selectedRelation = null;

function showRelationPopup(userId) {
    selectedUserId = userId;
    document.getElementById('relationPopup').style.display = 'flex';
}

document.querySelectorAll('.relation-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        selectedRelation = this.dataset.relation;
        document.querySelectorAll('.relation-btn').forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
    });
});

document.getElementById('relateBtn').addEventListener('click', function() {
    if (!selectedRelation) {
        alert('Please select a relation type');
        return;
    }

    fetch('/api/send-relation-request/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            receiver_id: selectedUserId,
            relation_type: selectedRelation
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Request sent successfully');
            document.getElementById('relationPopup').style.display = 'none';
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error sending request');
    });
});

document.getElementById('closePopupBtn').addEventListener('click', function() {
    document.getElementById('relationPopup').style.display = 'none';
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}