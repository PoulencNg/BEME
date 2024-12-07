document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('audioFile');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('audioFile', file);

    // Hiển thị thông báo đang xử lý
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = 'Đang xử lý...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            resultDiv.innerHTML = `<a href="${result.download_url}">Tải Xuống Tệp Đã Dịch</a>`;
        } else {
            resultDiv.textContent = 'Có lỗi xảy ra: ' + result.message;
        }
    } catch (error) {
        console.error(error);
        resultDiv.textContent = 'Có lỗi xảy ra trong quá trình tải lên.';
    }
});
