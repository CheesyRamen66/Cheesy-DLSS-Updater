import os
import re
import shutil
import tempfile
from bs4 import BeautifulSoup
import requests
import zipfile

TECHPOWERUP_URL="https://www.techpowerup.com/download/"
DEFAULT_DLL_NAMES=["nvngx_dlss.dll", "nvngx_dlssg.dll", "nvngx_dlssd.dll"]
GAME_DIRECTORIES=["/"]
DLL_BLACKLIST=["/usr/lib/nvidia", ".local/share/Trash/files", "/tmp/", "/Cheesy DLSS Updater/", "/steamapps/downloading/", "/.Trash-"]

temp_dir = tempfile.TemporaryDirectory()
print('Created temporary directory', temp_dir)

def fetch_dlss_info(DLSS_URL):
    response = requests.get(DLSS_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    latest_version_element = soup.find('div', class_='versions').find('div', class_='version', recursive=False).find('div', class_='flags').find('span', class_='flag latest').parent.parent
    latest_version=latest_version_element.find('h3', class_='title').get_text().strip()
    print(latest_version)
    file_id=latest_version_element.find('ul', class_='files').find('li', class_='file clearfix expanded').find('form', class_='download-version-form').find('input', {'name': 'id'})['value']
    print(file_id)
    return latest_version, file_id

def fetch_mirror_id(DLSS_URL, file_id):
    data={
        'id': file_id
    }
    response = requests.post(DLSS_URL, data=data)
    response.raise_for_status()
    mirrors = BeautifulSoup(response.text, 'html.parser').find('div', class_='mirrorlist')
    best_mirror_id = mirrors.find('button', attrs={"name": "server_id"})['value']
    return best_mirror_id

def fetch_dlss_dll(DLL_NAME, DLSS_URL):
    if os.path.exists(DLL_NAME):
        shutil.copy(DLL_NAME, temp_dir.name)
    else:
        dlss_version, file_id=fetch_dlss_info(DLSS_URL)
        mirror_id=fetch_mirror_id(DLSS_URL, file_id)
        data={
            'id': file_id,
            'server_id': mirror_id
        }
        response = requests.post(DLSS_URL, data=data, stream=True)
        response.raise_for_status()
        
        with open(f"{temp_dir.name}/{DLL_NAME}.zip", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            with zipfile.ZipFile(f"{temp_dir.name}/{DLL_NAME}.zip", 'r') as zip_ref:
                zip_ref.extractall(temp_dir.name)

fetch_dlss_dll(DEFAULT_DLL_NAMES[0], TECHPOWERUP_URL+"nvidia-dlss-dll/")
fetch_dlss_dll(DEFAULT_DLL_NAMES[1], TECHPOWERUP_URL+"nvidia-dlss-3-frame-generation-dll/")
fetch_dlss_dll(DEFAULT_DLL_NAMES[2], TECHPOWERUP_URL+"nvidia-dlss-3-ray-reconstruction-dll/")

print(os.listdir(temp_dir.name))

# Recursively replace all copies of nvngx_dlss.dll, nvngx_dlssg.dll, and nvngx_dlssd.dll in STEAM_DIR with the copy in temp_dir.
for game_directory in GAME_DIRECTORIES:
    for root, dirs, files in os.walk(game_directory):
        for file in files:
            if file in DEFAULT_DLL_NAMES:
                source_path = os.path.join(temp_dir.name, file)
                destination_path = os.path.join(root, file)
                if not any([re.search(path, destination_path) for path in DLL_BLACKLIST]):
                    shutil.copy2(source_path, destination_path)
                    print(f"Replaced {destination_path} with {source_path}")