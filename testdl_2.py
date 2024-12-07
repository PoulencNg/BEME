import os
import subprocess

def split_video(input_path, max_size_mb=25):
    try:
        # Kiểm tra kích thước tệp video
        file_size_in_bytes = os.path.getsize(input_path)
        file_size_in_mb = file_size_in_bytes / (1024 * 1024)

        if file_size_in_mb <= max_size_mb:
            print("Tệp video đã có kích thước hợp lệ (không cần chia nhỏ).")
            return [input_path]

        # Sử dụng ffmpeg để lấy thời gian video
        duration_command = [
            'ffmpeg', '-i', input_path, '-t', '00:00:01', '-f', 'null', '-'
        ]
        
        result = subprocess.run(duration_command, stderr=subprocess.PIPE, text=True)
        
        # Lấy thông tin thời gian video từ stderr của FFmpeg
        video_duration_str = [line for line in result.stderr.splitlines() if "Duration" in line]
        
        if not video_duration_str:
            raise Exception("Không thể xác định độ dài video.")
        
        # Đảm bảo xử lý đúng thời gian từ FFmpeg
        video_duration = video_duration_str[0].split()[1]  # Ví dụ: "00:12:47.47"
        video_duration = video_duration.strip(',')
        
        # Tách thời gian thành giờ, phút, giây
        hours, minutes, seconds = video_duration.split(':')
        
        # Nếu giây có phần thập phân (ví dụ 12.47 giây), loại bỏ phần thập phân
        seconds = float(seconds.split(',')[0])  # Loại bỏ phần thập phân nếu có
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        
        print(f"Tổng thời gian video: {total_seconds} giây.")

        # Xác định số phần cần chia
        chunk_duration = (max_size_mb * 1024 * 1024) / (file_size_in_bytes / total_seconds)
        print(f"Mỗi phần video sẽ có độ dài: {chunk_duration:.2f} giây.")

        # Tạo thư mục cha với tên giống file gốc
        output_dir = os.path.splitext(input_path)[0]
        os.makedirs(output_dir, exist_ok=True)

        # Chia video thành các phần nhỏ
        output_files = []
        part_num = 1
        for i in range(0, total_seconds, int(chunk_duration)):
            # Tạo tên file cho mỗi phần video
            output_filename = os.path.join(output_dir, f"{os.path.basename(input_path).split('.')[0]}_{part_num}{os.path.splitext(input_path)[1]}")
            output_files.append(output_filename)
            part_num += 1
            command = [
                'ffmpeg', '-i', input_path, '-ss', str(i), '-t', str(chunk_duration),
                '-c', 'copy', output_filename
            ]
            subprocess.run(command, check=True)

        print(f"Tệp video đã được chia thành {len(output_files)} phần.")
        return output_files

    except Exception as e:
        print(f"Error during video split: {e}")
        return None

# Ví dụ sử dụng
input_path = 'bannhaquan11.mp4'
split_files = split_video(input_path, max_size_mb=25)

if split_files:
    print("Các tệp video đã được chia nhỏ:")
    for split_file in split_files:
        print(split_file)
