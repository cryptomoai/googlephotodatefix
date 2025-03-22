import os
import json
import shutil
import subprocess
import datetime

# define folder paths
folder_jpgmp4 = r"folder path"  # folder with jpg and mp4 without timestamp
folder_json = r"folder path"  # folder with json files exported from Google Photos
folder_output = r"folder path"

# create the output folder if it doesn't exist
os.makedirs(folder_output, exist_ok=True)

def get_datetime_from_json(json_path):
    """read timestamp from json file"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "photoTakenTime" in data:
        return datetime.datetime.fromtimestamp(int(data["photoTakenTime"]['timestamp']))
    return None


def find_file_by_prefix(folder_path, prefix):
    """Google photo's json filename may be truncated if the original filename of jpg/mp4 is too long"""
    matching_files = [f for f in os.listdir(folder_path) if f.startswith(prefix)]

    if not matching_files:
        print(f"❌ No json file with prefix '{prefix}'")
        return None

    if len(matching_files) > 1:
        print(f"⚠️ Warning：Multiple matching json files {matching_files}")
        return None

    return matching_files[0]


def update_exif(file_path):
    """update timestamp"""
    filename = os.path.basename(file_path)
    json_filename = find_file_by_prefix(folder_json, filename)

    if json_filename is None:
        return

    json_path = os.path.join(folder_json, json_filename)
    new_datetime = get_datetime_from_json(json_path)
    if not new_datetime:
        print(f"⚠️ {json_path} has no timestamp information. Skipping this file")
        return

    # copy file without timestamp to destination folder
    new_file_path = os.path.join(folder_output, filename)
    shutil.copy2(file_path, new_file_path)

    formatted_time = new_datetime.strftime("%Y:%m:%d %H:%M:%S")

    if file_path.lower().endswith(".jpg"):  # add timestamp to JPG
        cmd = [
            "exiftool",
            f"-DateTimeOriginal={formatted_time}",
            f"-CreateDate={formatted_time}",
            "-overwrite_original",
            new_file_path
        ]
    elif file_path.lower().endswith(".mp4"):  # add timestamp to MP4
        cmd = [
            "exiftool",
            f"-CreateDate={formatted_time}",
            f"-ModifyDate={formatted_time}",
            f"-TrackCreateDate={formatted_time}",
            f"-TrackModifyDate={formatted_time}",
            f"-MediaCreateDate={formatted_time}",
            f"-MediaModifyDate={formatted_time}",
            "-overwrite_original",
            new_file_path
        ]

    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"✅ Updated {new_file_path} datetime to {formatted_time}")
        os.remove(file_path) # remove the jpg/mp4 file from the source folder if timestamp is successfully added to a new file in the destination folder
    except subprocess.CalledProcessError as e:
        print(f"❌ Error processing {filename}. Error message: {e.stderr.decode().strip()}")
        os.remove(new_file_path) # remove the file copied to destination folder if error occurs

def process_files():
    """iterate through every file in the source folder and try to create a new file with timestamp in the destination folder"""
    for filename in os.listdir(folder_jpgmp4):
        file_path = os.path.join(folder_jpgmp4, filename)

        if file_path.lower().endswith((".jpg", ".mp4")):
            update_exif(file_path)
        else:
            print(f"⚠️ Skipping {filename}, not a jpg or mp4 file.")

# start the process
process_files()
