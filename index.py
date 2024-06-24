import os
import shutil
from PIL import Image
import pillow_heif
import piexif
import concurrent.futures



def convert_heic_to_jpg(heic_path, output_path):
    # Read the HEIC file using pillow_heif
    heif_file = pillow_heif.read_heif(heic_path)

    # Extract metadata
    metadata = heif_file.info.get("exif", None)

    # Convert to PIL Image
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    # Save the image as JPEG
    image.save(output_path, "JPEG")

    # Insert metadata if available
    if metadata:
        exif_dict = piexif.load(metadata)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, output_path)


def copy_with_metadata(src, dst):
    shutil.copy2(src, dst)


def process_file(input_path, output_folder):
    filename = os.path.basename(input_path)
    file_extension = os.path.splitext(filename)[1].lower()
    output_path = os.path.join(output_folder, filename if file_extension !=
                               ".heic" else os.path.splitext(filename)[0] + ".jpg")

    if file_extension == ".heic":
        convert_heic_to_jpg(input_path, output_path)
        print(f"Converted {filename} to JPEG.")
    elif file_extension in [".jpg", ".mp4", ".mp3", ".png"]:
        copy_with_metadata(input_path, output_path)
        print(f"Copied {filename} to output folder.")


def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files_to_process = [os.path.join(input_folder, filename)
                        for filename in os.listdir(input_folder)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, input_path, output_folder)
                   for input_path in files_to_process]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")

# Example usage:
input_folder = 'C:\\Users\\keval\\Pictures\\uk'
output_folder = 'C:\\Users\\keval\\Pictures\\photo\\uk'
process_folder(input_folder, output_folder)
