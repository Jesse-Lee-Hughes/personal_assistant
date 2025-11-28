from personal_assistant.resources.google_workspace import GoogleWorkspace

if __name__ == '__main__':
    import json
    scopes = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    ws = GoogleWorkspace(scopes=scopes)

    # folders = ws.list_drive_folders()
    # for folder in folders:
    #     print(f"Name: {folder['name']}, ID: {folder['id']}")
    finances = ws.get_folder_by_name(name='Tax')
    print(finances)
    # files = ws.list_drive_files()
    # for file in files:
    #     print(json.dumps(file, indent=4))
    # print("\n")
    # print(f"Total files = {len(files)}")
    drive_files = ws.list_drive_files(folder_id = finances.get('id'))
    for file in drive_files:
        print(file)
