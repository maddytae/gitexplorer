let lineContent, noLineContent, sideBySideContent;

    // Fetch and store the contents of each HTML file
    fetch('/static/diff/line.html').then(response => response.text()).then(html => lineContent = html);
    fetch('/static/diff/no_line.html').then(response => response.text()).then(html => noLineContent = html);
    fetch('/static/diff/side_by_side.html').then(response => response.text()).then(html => sideBySideContent = html);

    window.onload = function() {
        const noLineCheckbox = document.getElementById('noLineCheckbox');
        const sideBySideCheckbox = document.getElementById('sideBySideCheckbox');

        noLineCheckbox.addEventListener('change', updateContent);
        sideBySideCheckbox.addEventListener('change', updateContent);
    };

    function updateContent() {
        const noLineCheckbox = document.getElementById('noLineCheckbox');
        const sideBySideCheckbox = document.getElementById('sideBySideCheckbox');

        if (noLineCheckbox.checked) {
            document.getElementById('contentArea').innerHTML = noLineContent;
            sideBySideCheckbox.disabled = true;
        } else if (sideBySideCheckbox.checked) {
            document.getElementById('contentArea').innerHTML = sideBySideContent;
            noLineCheckbox.disabled = true;
        } else {
            // Render line.html if both checkboxes are unchecked
            document.getElementById('contentArea').innerHTML = lineContent;
            noLineCheckbox.disabled = false;
            sideBySideCheckbox.disabled = false;
        }
    }