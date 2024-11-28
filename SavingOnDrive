from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta


class SavingOnDrive:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service = None

    def authenticate(self):
        creds = Credentials.from_service_account_file(
            self.credentials_file, scopes=self.scopes)
        self.service = build('drive', 'v3', credentials=creds)

    def create_folder(self, folder_name, parent_folder_id=None):
        # Create a folder with the given name inside the parent folder (if provided)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def upload_file(self, file_name, folder_id):
        # Upload a file to the specified folder
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_name, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def save_files(self, files):
        # Set the parent folder ID to the specific folder ("Property Scraper Uploads")
        parent_folder_id = '14CPVWBqYe5B0sK8sdB0cvcmtJGHoOQyu'  # ID of "Property Scraper Uploads"

        # Create a folder with yesterday's date inside the target folder
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        folder_id = self.create_folder(yesterday, parent_folder_id)

        # Upload each file to the newly created folder
        for file_name in files:
            self.upload_file(file_name, folder_id)
        print(f"Files uploaded successfully to folder '{yesterday}' on Google Drive.")
