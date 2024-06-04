import ffmpeg
from PIL import Image
import pytesseract
from googletrans import Translator
from langdetect import detect
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Function to extract frames from the video at a specified fps


def extract_frames(video_path, output_folder, fps=0.2):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    ffmpeg.input(video_path).output(
        f'{output_folder}/frame%04d.png', vf=f'fps={fps}').run()

# Function to detect the language of the text


def detect_language(text):
    try:
        return detect(text)
    except:
        return None

# Function to perform OCR on a single image frame


def ocr_frame(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    lang = detect_language(text)
    return text if lang in ['zh-cn', 'zh-tw'] else None

# Function to perform OCR on all frames in parallel and write the results to a file


def ocr_frames_parallel(input_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as f_out:
        image_files = [os.path.join(input_folder, img) for img in sorted(
            os.listdir(input_folder)) if img.endswith('.png')]

        with ThreadPoolExecutor(max_workers=12) as executor:
            results = executor.map(ocr_frame, image_files)

        for result in results:
            if result:
                f_out.write(result + '\n')

# Function to translate the extracted text


def translate_text(input_file, output_file):
    translator = Translator()
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            translated = translator.translate(line, src='zh-CN', dest='en')
            f_out.write(translated.text + '\n')

# Function to create an SRT subtitle file from the translated text


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

# Main function to orchestrate the entire process


def main(video_path):
    
    frames_folder = 'frames'
    extracted_text_file = 'extracted_text.txt'
    translated_text_file = 'translated_text.txt'
    subtitles_file = 'subtitles.srt'

    # Extract frames from the video
    extract_frames(video_path, frames_folder, fps=0.2)

    # Perform OCR on extracted frames in parallel
    ocr_frames_parallel(frames_folder, extracted_text_file)

    # Translate the extracted text
    translate_text(extracted_text_file, translated_text_file)

    # Create an SRT subtitle file from the translated text
    create_srt(translated_text_file, subtitles_file)


if __name__ == "__main__":
    main(sys.argv[1])
