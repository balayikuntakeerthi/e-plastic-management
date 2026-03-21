document.addEventListener('DOMContentLoaded', function() {
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