import gdown
import os

drive_link = ""

try:
    with open("link.txt", "r") as f:
        drive_link = f.read().strip()
except FileNotFoundError:
    print("Error: 'drive_link.txt' file not found.")
    exit(1)

GOOGLE_DRIVE_FILE_ID = drive_link.split('/')[-2]

actual_downloaded_path = gdown.download(
    id=GOOGLE_DRIVE_FILE_ID,
    quiet=False
)


print(f"Downloading file from Google Drive link: {drive_link}")

print(f"\nFile '{actual_downloaded_path}' downloaded successfully.")
