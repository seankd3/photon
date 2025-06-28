import os

files_to_delete = [
    r'C:\Users\smast\OneDrive\Desktop\Code Projects\Photon\pyproject.toml',
    r'C:\Users\smast\OneDrive\Desktop\Code Projects\Photon\delete_pyproject_toml.py'
]

for file_path in files_to_delete:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'Successfully deleted {file_path}')
        else:
            print(f'File not found: {file_path}')
    except Exception as e:
        print(f'Error deleting file {file_path}: {e}')
