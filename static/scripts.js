document.addEventListener('DOMContentLoaded', function() {
    var checkboxes = document.querySelectorAll('.form-check-input');
    var diffFrame = document.getElementById('diffFrame');

    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // Uncheck all checkboxes except the one that triggered the event
                checkboxes.forEach(function(otherCheckbox) {
                    if (otherCheckbox !== checkbox) {
                        otherCheckbox.checked = false;
                    }
                });

                // Set the iframe source and display it
                diffFrame.src = this.getAttribute('data-url');
                diffFrame.style.display = 'block';
            } else {
                // If the checkbox was unchecked, hide the iframe
                diffFrame.style.display = 'none';
            }
        });
    });
});
