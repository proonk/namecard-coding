document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload('front', 'dropZoneFront', 'frontFileInfo');
    setupFileUpload('back', 'dropZoneBack', 'backFileInfo');

    const form = document.getElementById('impositionForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');

    // This is a plain HTML form submit (action="/imposition"), so the
    // browser handles the POST + PDF download itself — this listener only
    // toggles the button's visual state while that's in flight.
    form.addEventListener('submit', () => {
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        submitBtn.disabled = true;
    });
});

function setupFileUpload(inputId, zoneId, statusId) {
    const input = document.getElementById(inputId);
    const zone = document.getElementById(zoneId);
    const status = document.getElementById(statusId);

    const showFile = (file) => {
        if (!file) return;
        status.textContent = file.name;
        status.classList.add('is-set');
        zone.classList.add('has-file');
    };

    input.addEventListener('change', () => {
        if (input.files && input.files[0]) showFile(input.files[0]);
    });

    ['dragenter', 'dragover'].forEach((name) => {
        zone.addEventListener(name, (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });
    });

    ['dragleave', 'dragend'].forEach((name) => {
        zone.addEventListener(name, () => zone.classList.remove('dragover'));
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (!file) return;
        // keep the native file input in sync so the form actually submits it
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        showFile(file);
    });
}