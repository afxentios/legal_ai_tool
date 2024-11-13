import os
import re
from typing import Generator, Optional, Dict

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from PyPDF2 import PdfReader

# Retrieve AWS credentials from environment variables
# aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_access_key_id = 'AKIA4XMRGAHME5DAGKEW';
aws_secret_access_key = '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'
print(aws_access_key_id)
print(aws_secret_access_key)

if not aws_access_key_id or not aws_secret_access_key:
    raise EnvironmentError("AWS credentials are not set in environment variables.")

# Initialize S3 client with environment credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Source and destination bucket names
SOURCE_BUCKET = 'hackathon-team2-eur-lex'
DESTINATION_BUCKET = 'hackathon-team2-eur-lex-opinions'
SEARCH_TEXT = '5*AB'


def count_pdf_objects(bucket_name: str) -> int:
    """
    Counts all PDF objects in the specified S3 bucket.

    Args:
        bucket_name (str): Name of the S3 bucket.

    Returns:
        int: Number of PDF objects in the bucket.
    """
    pdf_count = 0
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                if obj['Key'].lower().endswith('.pdf'):
                    pdf_count += 1
    except ClientError as e:
        print(f"Error accessing bucket {bucket_name}: {e}")
    return pdf_count


def list_pdf_objects(bucket_name: str) -> Generator[Dict, None, None]:
    """
    Generator to list all PDF objects in the specified S3 bucket whose filenames contain the pattern '5*AB'.

    Args:
        bucket_name (str): Name of the S3 bucket.

    Yields:
        dict: S3 object metadata.
    """
    # Define the regex pattern to match filenames containing '5', followed by any characters, and then 'AB'
    pattern = re.compile(r'5.*AB.*\.pdf$', re.IGNORECASE)

    paginator = s3_client.get_paginator('list_objects_v2')
    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                key = obj['Key']
                filename = os.path.basename(key)
                if pattern.search(filename):
                    yield obj
    except ClientError as e:
        print(f"Error accessing bucket {bucket_name}: {e}")


def download_pdf(bucket_name: str, key: str, download_dir: str) -> Optional[str]:
    """
    Downloads a PDF file from S3 to a local directory, preserving the S3 folder structure.

    Args:
        bucket_name (str): Name of the S3 bucket.
        key (str): S3 object key.
        download_dir (str): Local base directory to save the downloaded file.

    Returns:
        Optional[str]: Path to the downloaded file, or None if download fails.
    """
    try:
        # Construct the local path by combining the download directory with the S3 key
        local_path = os.path.join(download_dir, key)
        # Ensure the directory exists; create if it doesn't
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # Download the file from S3 to the constructed local path
        s3_client.download_file(bucket_name, key, local_path)
        return local_path
    except ClientError as e:
        print(f"Error downloading {key}: {e}")
        return None


def pdf_contains_text(file_path: str, search_text: str) -> bool:
    """
    Checks if the PDF file contains the specified search text.

    Args:
        file_path (str): Path to the PDF file.
        search_text (str): Text to search for.

    Returns:
        bool: True if text is found, False otherwise.
    """
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text and search_text in text:
                return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return False


def copy_pdf_to_destination(source_bucket: str, key: str, dest_bucket: str):
    """
    Copies the PDF file from the source bucket to the destination bucket.

    Args:
        source_bucket (str): Source S3 bucket name.
        key (str): S3 object key.
        dest_bucket (str): Destination S3 bucket name.
    """
    try:
        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3_client.copy(copy_source, dest_bucket, key)
        print(f"Copied {key} to {dest_bucket}")
    except ClientError as e:
        print(f"Error copying {key}: {e}")


def main():
    try:
        pdf_count = count_pdf_objects(SOURCE_BUCKET)
        print(f"Number of PDF files in '{SOURCE_BUCKET}': {pdf_count}")
        for obj in list_pdf_objects(SOURCE_BUCKET):
            key = obj['Key']
            print(f"Processing {key}...")
            local_pdf = download_pdf(SOURCE_BUCKET, key, '/Users/afxentios/Desktop/BedrockPDF')
            print(local_pdf)
            copy_pdf_to_destination(SOURCE_BUCKET, key, DESTINATION_BUCKET)
            if local_pdf:
                os.remove(local_pdf)
    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")


if __name__ == "__main__":
    main()
