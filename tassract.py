import ffmpeg
from PIL import Image
import pytesseract
from googletrans import Translator
import os
import sys

def extract_frames(video_path, output_folder):
    ffmpeg.input(video_path).output(f'{output_folder}/frame%04d.png', vf='fps=1').run()

def ocr_frames(input_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for image_file in sorted(os.listdir(input_folder)):
            if image_file.endswith('.png'):
                img_path = os.path.join(input_folder, image_file)
                text = pytesseract.image_to_string(Image.open(img_path), lang='chi_sim')
                f.write(text + '\n')

def translate_text(input_file, output_file):
    translator = Translator()
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            translated = translator.translate(line, src='zh-CN', dest='en')
            f_out.write(translated.text + '\n')

def create_srt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        for i, line in enumerate(lines):
            start_time = i  # Adjust as needed
            end_time = i + 1  # Adjust as needed
            f_out.write(f"{i+1}\n")
            f_out.write(f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000\n")
            f_out.write(line.strip() + '\n\n')

def main(video_path):
    
    frames_folder = 'frames'
    os.mkdir(frames_folder)
    extracted_text_file = 'extracted_text.txt'
    translated_text_file = 'translated_text.txt'
    subtitles_file = 'subtitles.srt'

    # Extract frames
    extract_frames(video_path, frames_folder)

    # Perform OCR on frames
    ocr_frames(frames_folder, extracted_text_file)

    # Translate extracted text
    translate_text(extracted_text_file, translated_text_file)

    # Create subtitle file
    create_srt(translated_text_file, subtitles_file)

if __name__ == "__main__":
    main(sys.argv[1])
