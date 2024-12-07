 document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const progressDiv = document.getElementById('progress');
            const resultDiv = document.getElementById('result');
            const errorDiv = document.getElementById('error');

            progressDiv.style.display = 'block';
            resultDiv.style.display = 'none';
            errorDiv.style.display = 'none';

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (response.ok) {
                    progressDiv.style.display = 'none';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `<p>${data.message}</p>`;
                } else {
                    progressDiv.style.display = 'none';
                    errorDiv.style.display = 'block';
                    errorDiv.textContent = data.error;
                }
            } catch (error) {
                progressDiv.style.display = 'none';
                errorDiv.style.display = 'block';
                errorDiv.textContent = `Lỗi kết nối: ${error.message}`;
            }
        });