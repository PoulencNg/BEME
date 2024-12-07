const express = require('express');
const multer = require('multer');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
require('dotenv').config();

const app = express();
const upload = multer({ 
    dest: 'uploads/',
    limits: { fileSize: 50 * 1024 * 1024 }, // Giới hạn kích thước tệp 50MB
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('Chỉ cho phép tải lên các định dạng âm thanh: MP3, WAV.'));
        }
    }
});

// Serve static files từ thư mục "public"
app.use(express.static('public'));

// Route xử lý tải lên
app.post('/upload', upload.single('audioFile'), async (req, res) => {
    try {
        const filePath = req.file.path;
        const fileName = req.file.originalname;

        // Chuẩn bị dữ liệu cho Turboscribe
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));

        // Gọi API Turboscribe để chuyển đổi speech-to-text
        const speechToTextResponse = await axios.post('https://api.turboscribe.com/speech-to-text', form, {
            headers: {
                'Authorization': `Bearer ${process.env.TURBOSCRIBE_API_KEY}`,
                ...form.getHeaders()
            }
        });

        const vietnameseText = speechToTextResponse.data.text;

        // Gọi API ChatGPT để dịch từ tiếng Việt sang tiếng Anh
        const translationResponse = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: 'gpt-4',
            messages: [
                { role: 'system', content: 'You are a helpful assistant that translates Vietnamese to English.' },
                { role: 'user', content: vietnameseText }
            ],
            max_tokens: 1000,
            temperature: 0.5
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        const englishText = translationResponse.data.choices[0].message.content;

        // Tạo tệp đã dịch
        const translatedFileName = `translated_${path.parse(fileName).name}.txt`;
        const translatedFilePath = path.join('translated', translatedFileName);

        // Đảm bảo thư mục "translated" tồn tại
        if (!fs.existsSync('translated')){
            fs.mkdirSync('translated');
        }

        fs.writeFileSync(translatedFilePath, englishText, 'utf8');

        // Xóa tệp tải lên để tiết kiệm không gian
        fs.unlinkSync(filePath);

        // Trả về đường dẫn tải xuống
        res.json({
            success: true,
            downloadUrl: `/download/${translatedFileName}`
        });
    } catch (error) {
        console.error(error);
        res.json({
            success: false,
            message: error.message || 'Có lỗi xảy ra trong quá trình xử lý.'
        });
    }
});

// Route để tải xuống tệp đã dịch
app.get('/download/:filename', (req, res) => {
    const filename = req.params.filename;
    const filePath = path.join(__dirname, 'translated', filename);
    res.download(filePath, filename, (err) => {
        if (err) {
            console.error(err);
            res.status(500).send('Không thể tải xuống tệp.');
        }
    });
});

// Xử lý lỗi Multer
app.use((err, req, res, next) => {
    if (err instanceof multer.MulterError) {
        res.status(400).json({ success: false, message: err.message });
    } else if (err) {
        res.status(400).json({ success: false, message: err.message });
    }
});

// Bắt đầu server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server đang chạy trên cổng ${PORT}`);
});
