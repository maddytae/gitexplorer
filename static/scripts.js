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


var myCodeMirror1 = CodeMirror.fromTextArea(document.getElementById('code1'), {
    lineNumbers: true,
    lineWrapping: false // Disable line wrapping
});

var myCodeMirror2 = CodeMirror.fromTextArea(document.getElementById('code2'), {
    lineNumbers: true,
    lineWrapping: false // Disable line wrapping
});

function updateFileName1() {
    var fileInput = document.getElementById('fileUpload1');
    var fileUploadStatus = document.getElementById('file-upload-status1');
    fileUploadStatus.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : '';
}

function updateFileName2() {
    var fileInput = document.getElementById('fileUpload2');
    var fileUploadStatus = document.getElementById('file-upload-status2');
    fileUploadStatus.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : '';
}
