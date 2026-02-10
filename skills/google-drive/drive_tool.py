#!/usr/bin/env python3
"""
Google Drive Tool for OpenClaw
Provides CLI commands to interact with Google Drive via Service Account.
Usage: python drive_tool.py <command> [args]
"""
import json
import os
import sys
import io

def get_service():
    """Authenticate and return Drive service."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Missing dependencies. Run: pip install google-auth google-api-python-client")
        sys.exit(1)

    # Method 1: Credentials file path
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Method 2: JSON content in env var (Codespaces)
    if not creds_path or not os.path.exists(creds_path or ''):
        json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if json_content:
            creds_path = '/tmp/gsa_credentials.json'
            with open(creds_path, 'w') as f:
                f.write(json_content)
        else:
            print("ERROR: No credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS.")
            sys.exit(1)

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def cmd_list(service, args):
    """List files in Drive (max 30)."""
    page_size = int(args[0]) if args else 30
    results = service.files().list(
        pageSize=page_size,
        fields="files(id, name, mimeType, modifiedTime)",
        orderBy="modifiedTime desc"
    ).execute()
    files = results.get('files', [])
    if not files:
        print("No files found.")
        return
    print(f"Found {len(files)} files:\n")
    for f in files:
        icon = "📁" if 'folder' in f['mimeType'] else "📄"
        modified = f.get('modifiedTime', '?')[:10]
        print(f"  {icon} [{modified}] {f['name']}  (ID: {f['id']})")

def cmd_search(service, args):
    """Search files by name."""
    if not args:
        print("Usage: search <query>")
        return
    query = args[0]
    results = service.files().list(
        q=f"name contains '{query}'",
        pageSize=20,
        fields="files(id, name, mimeType, modifiedTime)",
        orderBy="modifiedTime desc"
    ).execute()
    files = results.get('files', [])
    if not files:
        print(f"No files matching '{query}'.")
        return
    print(f"Found {len(files)} matching files:\n")
    for f in files:
        icon = "📁" if 'folder' in f['mimeType'] else "📄"
        print(f"  {icon} {f['name']}  (ID: {f['id']})")

def cmd_read(service, args):
    """Read content of a text file by name or ID."""
    if not args:
        print("Usage: read <filename_or_id>")
        return
    target = args[0]
    
    # Try as file name first
    results = service.files().list(
        q=f"name contains '{target}'",
        pageSize=5,
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])
    
    if not files:
        # Try as direct ID
        file_id = target
        try:
            meta = service.files().get(fileId=file_id, fields="name, mimeType").execute()
            files = [{'id': file_id, 'name': meta['name'], 'mimeType': meta['mimeType']}]
        except:
            print(f"File not found: {target}")
            return

    file_info = files[0]
    mime = file_info['mimeType']
    
    try:
        if 'google-apps.document' in mime:
            # Export Google Doc as text
            content = service.files().export(
                fileId=file_info['id'], mimeType='text/plain'
            ).execute()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            print(f"--- {file_info['name']} ---\n")
            print(content)
        elif any(ext in mime for ext in ['text', 'markdown', 'json', 'xml', 'yaml']):
            # Download text file
            from googleapiclient.http import MediaIoBaseDownload
            request = service.files().get_media(fileId=file_info['id'])
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            content = buffer.getvalue().decode('utf-8')
            print(f"--- {file_info['name']} ---\n")
            print(content)
        else:
            print(f"Cannot read binary file: {file_info['name']} ({mime})")
            print(f"File ID: {file_info['id']}")
    except Exception as e:
        print(f"Error reading file: {e}")

def cmd_upload(service, args):
    """Upload a local file to Drive."""
    if not args:
        print("Usage: upload <local_file_path> [drive_folder_name]")
        return
    
    local_path = args[0]
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        return
    
    from googleapiclient.http import MediaFileUpload
    
    # Find target folder
    folder_name = args[1] if len(args) > 1 else "Cerebro_Proyecto_Gemini"
    folder_results = service.files().list(
        q=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    folders = folder_results.get('files', [])
    
    file_metadata = {'name': os.path.basename(local_path)}
    if folders:
        file_metadata['parents'] = [folders[0]['id']]
    
    media = MediaFileUpload(local_path, resumable=True)
    file = service.files().create(
        body=file_metadata, media_body=media, fields='id, name'
    ).execute()
    
    print(f"✅ Uploaded: {file['name']} (ID: {file['id']})")

def cmd_create(service, args):
    """Create a new text file in Drive."""
    if len(args) < 2:
        print("Usage: create <filename> <content>")
        return
    
    filename = args[0]
    content = ' '.join(args[1:])
    
    from googleapiclient.http import MediaInMemoryUpload
    
    # Find Cerebro folder
    folder_results = service.files().list(
        q="name = 'Cerebro_Proyecto_Gemini' and mimeType = 'application/vnd.google-apps.folder'",
        fields="files(id)"
    ).execute()
    folders = folder_results.get('files', [])
    
    file_metadata = {'name': filename}
    if folders:
        file_metadata['parents'] = [folders[0]['id']]
    
    media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')
    file = service.files().create(
        body=file_metadata, media_body=media, fields='id, name'
    ).execute()
    
    print(f"✅ Created: {file['name']} (ID: {file['id']})")

def main():
    if len(sys.argv) < 2:
        print("Google Drive Tool for OpenClaw")
        print("Commands: list, search, read, upload, create")
        print("Usage: python drive_tool.py <command> [args]")
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        'list': cmd_list,
        'search': cmd_search,
        'read': cmd_read,
        'upload': cmd_upload,
        'create': cmd_create,
    }
    
    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")
        return
    
    service = get_service()
    commands[command](service, args)

if __name__ == "__main__":
    main()
