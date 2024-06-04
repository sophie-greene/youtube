import os
import sys
import subprocess
import ffmpeg
from concurrent.futures import ThreadPoolExecutor


def extract_frames(video_path, output_folder, fps=0.1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    ffmpeg.input(video_path).output(
        f'{output_folder}/frame%04d.png', vf=f'fps={fps}').run()


def create_srt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        for i, line in enumerate(lines):
            start_time = i  # Adjust as needed
            end_time = i + 1  # Adjust as needed
            f_out.write(f"{i+1}\n")
            f_out.write(
                f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000\n")
            f_out.write(line.strip() + '\n\n')
            

def get_text(image_name):
    txt = image_name.replace('.png', '.txt')
    cmd = ['shortcuts',
           'run',
           'extract_text_and_translate',
           '-i',
           f'"{image_name}"',
           '-o',
           f'"{txt}"',

           "2>/dev/null"]
    cmd = ' '.join(cmd)
    print(cmd)
    try:
        subprocess.run(cmd, shell=True)
        return True
    except Exception:
        return False
def extract_trans(txt):
    with open(txt, encoding='utf-8') as f:
        t = f.read()
    return t
# Main function to orchestrate the entire process

def main(video_path):

    frames_folder = 'frames'
    # Extract frames from the video
    extract_frames(video_path, frames_folder, fps=0.1)
    images = [os.path.join(frames_folder, f)
              for f in os.listdir(frames_folder) if f.endswith('.png')]

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(get_text, images)
    txts = [os.path.join(frames_folder, f)
              for f in os.listdir(frames_folder) if f.endswith('.txt')]
    
    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(extract_trans, txts)

if __name__ == "__main__":
    main(sys.argv[1])
