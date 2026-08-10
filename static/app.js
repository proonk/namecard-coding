(() => {
  const form = document.getElementById('impose-form');
  const generateBtn = document.getElementById('generate-btn');
  const errorMsg = document.getElementById('error-msg');
  const resultStub = document.getElementById('result-stub');
  const stubDownload = document.getElementById('stub-download');
  const stubReset = document.getElementById('stub-reset');
  const specCount = document.getElementById('spec-count');
  const bleedToggle = document.getElementById('bleed-toggle');
  const bleedState = document.getElementById('bleed-state');

  const sides = ['front', 'back'];
  const files = { front: null, back: null };

  // ---- dropzone wiring -------------------------------------------------
  sides.forEach((side) => {
    const zone = document.getElementById(`dropzone-${side}`);
    const input = document.getElementById(`file-${side}`);
    const preview = zone.querySelector('.dz-preview');
    const empty = zone.querySelector('.dz-empty');
    const img = document.getElementById(`preview-${side}`);
    const filenameEl = document.getElementById(`filename-${side}`);
    const clearBtn = zone.querySelector('.dz-clear');

    const setFile = (file) => {
      if (!file || !file.type.startsWith('image/')) return;
      files[side] = file;
      zone.classList.add('has-file');
      img.src = URL.createObjectURL(file);
      filenameEl.textContent = file.name;
      empty.hidden = true;
      preview.hidden = false;
      updateSubmitState();
    };

    const clearFile = () => {
      files[side] = null;
      input.value = '';
      zone.classList.remove('has-file');
      empty.hidden = false;
      preview.hidden = true;
      updateSubmitState();
    };

    zone.addEventListener('click', (e) => {
      if (e.target.closest('.dz-clear')) return;
      input.click();
    });

    zone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        input.click();
      }
    });

    input.addEventListener('change', () => setFile(input.files[0]));

    ['dragenter', 'dragover'].forEach((evt) =>
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.add('is-dragover');
      })
    );

    ['dragleave', 'dragend'].forEach((evt) =>
      zone.addEventListener(evt, () => zone.classList.remove('is-dragover'))
    );

    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('is-dragover');
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      setFile(file);
    });

    clearBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearFile();
    });
  });

  function updateSubmitState() {
    generateBtn.disabled = !(files.front && files.back);
  }

  // ---- spec ticket -------------------------------------------------
  form.querySelectorAll('input[name="paper_choice"]').forEach((radio) => {
    radio.addEventListener('change', () => {
      specCount.textContent = radio.value === '1' ? '20 张 / 页' : '10 张 / 页';
    });
  });

  bleedToggle.addEventListener('change', () => {
    bleedState.textContent = bleedToggle.checked ? '1.5 mm 出血' : '无出血';
  });

  // ---- submit -------------------------------------------------
  stubReset.addEventListener('click', () => {
    resultStub.hidden = true;
    form.hidden = false;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!files.front || !files.back) return;

    errorMsg.hidden = true;
    generateBtn.classList.add('is-loading');
    generateBtn.disabled = true;

    const paperChoice = form.querySelector('input[name="paper_choice"]:checked').value;
    const fd = new FormData();
    fd.append('paper_choice', paperChoice);
    if (bleedToggle.checked) fd.append('use_bleed', 'true');
    fd.append('front', files.front);
    fd.append('back', files.back);

    try {
      const res = await fetch('/imposition', { method: 'POST', body: fd });

      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(text || `生成失败（状态码 ${res.status}）`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const filename = paperChoice === '1'
        ? 'Business_Cards_A3.pdf'
        : 'Business_Cards_A4.pdf';

      stubDownload.href = url;
      stubDownload.download = filename;

      form.hidden = true;
      resultStub.hidden = false;

      // trigger the download automatically, same click also works manually
      stubDownload.click();
    } catch (err) {
      errorMsg.textContent = err.message || '生成失败，请重试。';
      errorMsg.hidden = false;
    } finally {
      generateBtn.classList.remove('is-loading');
      generateBtn.disabled = !(files.front && files.back);
    }
  });
})();