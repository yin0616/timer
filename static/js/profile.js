document.getElementById('upload').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
      const preview = document.getElementById('avatar-preview');
      preview.src = URL.createObjectURL(file);
    }
  });