import ffmpeg
import os

def convert_to_wav(input_path, output_dir):
    """
    Chuyển đổi file đầu vào sang định dạng .wav.

    :param input_path: Đường dẫn tới file đầu vào.
    :param output_dir: Thư mục để lưu file .wav sau khi chuyển đổi.
    :return: Đường dẫn tới file .wav đã chuyển đổi hoặc None nếu lỗi.
    """
    # Kiểm tra file đầu vào
    if not os.path.exists(input_path):
        raise FileNotFoundError("File đầu vào không tồn tại.")

    # Lấy tên file và phần mở rộng
    filename, ext = os.path.splitext(os.path.basename(input_path))
    ext = ext.lower()

    # Đặt đường dẫn file đầu ra
    output_path = os.path.join(output_dir, f"{filename}.wav")

    # Kiểm tra xem file đã là .wav chưa
    if ext == '.wav':
        print("File đã ở định dạng .wav. Không cần chuyển đổi.")
        return input_path

    # Thực hiện chuyển đổi
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='wav')
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"Chuyển đổi thành công: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        print("Lỗi trong quá trình chuyển đổi:", e.stderr.decode())
        return None

# Ví dụ sử dụng
if __name__ == "__main__":
    input_file = "DVO00009.avi"  # Thay bằng đường dẫn file của bạn
    output_directory = "C:\cong viec\Beme\python beme\daxuly"  # Thay bằng đường dẫn thư mục output

    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    converted_file = convert_to_wav(input_file, output_directory)
    if converted_file:
        print(f"File đã được chuyển đổi và lưu tại: {converted_file}")
    else:
        print("Chuyển đổi thất bại.")
