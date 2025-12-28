from pathlib import Path
import sys

def get_single_mp4(folder: Path | str | None = None) -> Path:
    """
    Return the single .mp4 file in folder.
    Raises FileNotFoundError if none found, RuntimeError if more than one found.
    """
    folder = Path(folder) if folder is not None else Path(__file__).resolve().parent
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    mp4s = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"]

    if not mp4s:
        raise FileNotFoundError(f"No .mp4 files found in {folder}")
    if len(mp4s) > 1:
        raise RuntimeError(f"Multiple .mp4 files found in {folder}: {[p.name for p in mp4s]}")

    return mp4s[0]


import os
import hashlib
import subprocess

def format_filename_with_hash(original_filename):
    # Extract base name and extension
    base_name, extension = os.path.splitext(original_filename)

    # Replace spaces with hyphens in the base name
    modified_base_name = base_name.replace(" ", "-")

    # Calculate MD5 hash of the original full filename
    md5_hash = hashlib.md5(original_filename.encode('utf-8')).hexdigest()

    # Combine parts to form the new filename
    # Insert the hash before the file extension
    new_filename = f"{modified_base_name}-{md5_hash}"

    return new_filename

import boto3
s3 = boto3.client('s3')

def uploading_files(output_dir):
  print(f"\n--- Uploading HLS files from '{output_dir}' to S3 bucket 'ott-aashu-processed' ---")

  for root, dirs, files in os.walk(output_dir):
    for file in files:
        local_path = os.path.join(root, file)
        # Construct the S3 object key. We want to maintain the directory structure
        # within the S3 bucket, starting from 'hls_output/'.
        # os.path.relpath will give the path relative to output_dir
        s3_object_key = os.path.relpath(local_path, output_dir)
        s3_object_key = os.path.join(output_dir, s3_object_key)

        content_type = "application/octet-stream" # Default content type
        if file.endswith(".m3u8"):
            content_type = "application/vnd.apple.mpegurl"
        elif file.endswith(".ts"):
            content_type = "video/mp2t"

        try:
            print(f"Uploading {local_path} to s3://ott-aashu-processed/{s3_object_key} with ContentType: {content_type}")
            s3.upload_file(
                local_path, "ott-aashu-processed", s3_object_key, ExtraArgs={'ContentType': content_type}
            )
            print(f"Successfully uploaded {s3_object_key}")
        except Exception as e:
            print(f"Error uploading {s3_object_key}: {e}")
            sys.exit(1)

  print("--- HLS files upload complete ---")


import os
import subprocess

def generate_hls_variants(local_file_name, output_dir):
    # Create output directory based on file name
    # output_dir = os.path.splitext(local_file_name)[0]
    # os.makedirs(output_dir, exist_ok=True)

    segment_path = os.path.join(output_dir, "%v_%03d.ts")
    playlist_path = os.path.join(output_dir, "%v.m3u8")

    # FFmpeg command as a Python list
    ffmpeg_command = [
        "ffmpeg",
        "-i", local_file_name,
        "-filter_complex",
        "[0:v]split=5[v1][v2][v3][v4][v5];"
        "[v1]scale=1920:1080[v1out];"
        "[v2]scale=1280:720[v2out];"
        "[v3]scale=854:480[v3out];"
        "[v4]scale=640:360[v4out];"
        "[v5]scale=426:240[v5out]",

        "-map", "[v1out]", "-map", "0:a?", "-c:v", "h264", "-c:a", "aac", "-b:v:0", "5000k", "-b:a:0", "192k",
        "-map", "[v2out]", "-map", "0:a?", "-c:v", "h264", "-c:a", "aac", "-b:v:1", "3000k", "-b:a:1", "128k",
        "-map", "[v3out]", "-map", "0:a?", "-c:v", "h264", "-c:a", "aac", "-b:v:2", "1500k", "-b:a:2", "128k",
        "-map", "[v4out]", "-map", "0:a?", "-c:v", "h264", "-c:a", "aac", "-b:v:3", "800k",  "-b:a:3", "96k",
        "-map", "[v5out]", "-map", "0:a?", "-c:v", "h264", "-c:a", "aac", "-b:v:4", "400k",  "-b:a:4", "64k",

        "-f", "hls",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-var_stream_map", "v:0,a:0,name:1080p v:1,a:1,name:720p v:2,a:2,name:480p v:3,a:3,name:360p v:4,a:4,name:240p",
        "-master_pl_name", "master.m3u8",
        "-hls_segment_filename", segment_path,
        playlist_path
    ]

    # Run FFmpeg
    print("Generating HLS variants...\nPlease be patient...\nDon't close the tab...\nInternet should be connected....\n......")
    subprocess.run(ffmpeg_command, check=True, )

    print("Conversion completed!")

    uploading_files(output_dir)



# Example call:
# generate_hls_variants(actual_downloaded_path)


if __name__ == "__main__":
    # optional: pass folder path as first arg, otherwise use script directory
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        mp4 = get_single_mp4(folder_arg)
        print(mp4)  # path to the single .mp4 file
        formatted_filename = format_filename_with_hash(mp4.name)
        #create directory for hls output
        hls_output_dir = Path(formatted_filename)
        hls_output_dir.mkdir(exist_ok=True)
        print(f"Formatted filename: {formatted_filename}")
        generate_hls_variants(str(mp4), str(hls_output_dir))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)