// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // ✅ Waste Record form
    const form = document.getElementById('entryForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const data = {
                location_id: document.getElementById('location_id').value,
                plastic_type_id: document.getElementById('plastic_type_id').value,
                quantity_kg: document.getElementById('quantity_kg').value,
                date: document.getElementById('date').value,
                recorded_by: document.getElementById('recorded_by').value
            };

            fetch('/api/add-record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(result => {
                alert('Record added successfully!');
                form.reset();
            })
            .catch(err => {
                alert('Something went wrong!');
            });
        });
    }
});

// ✅ NSS Teams: Add new team
function addTeam() {
    const data = {
        team_name: document.getElementById('team_name').value,
        team_leader: document.getElementById('team_leader').value,
        location_id: document.getElementById('team_location').value
    };

    fetch('/api/add-team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    })
    .catch(err => {
        alert('Something went wrong while adding team!');
    });
}

// ✅ NSS Teams: Toggle enable/disable
function toggleTeam(id, enable) {
    fetch('/api/toggle-team/' + id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: enable })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();
    })
    .catch(err => {
        alert('Something went wrong while toggling team!');
    });
}
