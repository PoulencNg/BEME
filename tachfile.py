from pydub import AudioSegment
import os

def split_audio_in_half(input_file, output1, output2, format="mp3"):
    # Kiểm tra sự tồn tại của file đầu vào
    if not os.path.isfile(input_file):
        print(f"File {input_file} không tồn tại.")
        return

    try:
        # Tải file âm thanh
        audio = AudioSegment.from_file(input_file)
    except Exception as e:
        print(f"Lỗi khi tải file âm thanh: {e}")
        return

    # Tính độ dài của âm thanh (mili giây)
    audio_length = len(audio)
    
    # Tính thời điểm tách ở giữa
    split_time = audio_length // 2

    # Tách âm thanh thành hai phần
    first_part = audio[:split_time]
    second_part = audio[split_time:]

    try:
        # Lưu hai phần âm thanh
        first_part.export(output1, format=format)
        second_part.export(output2, format=format)
        print(f"Đã tách âm thanh thành hai phần bằng nhau:\n- {output1}\n- {output2}")
    except Exception as e:
        print(f"Lỗi khi xuất file âm thanh: {e}")

if __name__ == "__main__":
    # Đường dẫn đến file âm thanh gốc
    input_file = "truongchinh.wav"  # Thay đổi tên file theo nhu cầu

    # Định nghĩa tên file đầu ra
    output_part1 = "truongchinh_part1.mp3"
    output_part2 = "truongchinh_part2.mp3"


    # Gọi hàm để tách âm thanh
    split_audio_in_half(input_file, output_part1, output_part2, format="mp3")
