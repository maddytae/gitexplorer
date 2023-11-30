document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.getElementById('showFolderCheckbox');
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            var diffFrame = document.getElementById('diffFrame');
            if (diffFrame) {
                diffFrame.style.display = checkbox.checked ? 'block' : 'none';
            }
        });
    }
});