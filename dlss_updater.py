import os
import shutil
import urllib.request
import tempfile
import glob
import json
import requests
import zipfile

DLSS_TAGS_URL = "https://api.github.com/repos/NVIDIA/DLSS/tags"
DLSS_DLL_URL="https://raw.githubusercontent.com/NVIDIA/DLSS/main/lib/Windows_x86_64/rel/nvngx_dlss.dll"
DEFAULT_DLL_NAME="nvngx_dlss.dll"
NEXUS_MOD_DOMAIN="site"
NEXUS_MOD_ID=550
NEXUS_FILE_URL=f'https://api.nexusmods.com/v1/games/{NEXUS_MOD_DOMAIN}/mods/{NEXUS_MOD_ID}/files'

def fetch_latest_dlss_tag():
    # Fetches the latest DLSS tag from the NVIDIA DLSS GitHub repository.
    response = requests.get(DLSS_TAGS_URL)
    if response.status_code == 200:
        tags = response.json()
        if tags:
            latest_version = tags[0]["name"]
            print(f"Latest NVIDIA DLSS Tag: {latest_version}")
        else:
            print("No tags found.")
    else:
        print(f"Failed to fetch tags: {response.status_code}, {response.text}")

temp_dir = tempfile.TemporaryDirectory()
print('Created temporary directory', temp_dir)

if os.path.exists(DEFAULT_DLL_NAME):
    shutil.copy(DEFAULT_DLL_NAME, temp_dir.name)
else:
    fetch_latest_dlss_tag()
    urllib.request.urlretrieve(DLSS_DLL_URL, temp_dir.name+"/"+DEFAULT_DLL_NAME)

tweaks_folders = glob.glob("DLSSTweaks*/")
if tweaks_folders:
    tweaks_folders.sort()
    shutil.copytree(tweaks_folders[-1], temp_dir.name+"/DLSSTweaks")

else:
    tweaks_zips = glob.glob("DLSSTweaks*.zip")
    if tweaks_zips:
        tweaks_zips.sort()
        with zipfile.ZipFile(tweaks_zips[-1], 'r') as zip_ref:
            zip_ref.extractall(temp_dir.name+"/DLSSTweaks")

    else:
        with open('credentials.json', 'r') as credentials_file:
            NEXUS_API_KEY = json.load(credentials_file)['nexus_api_key']
            nexus_headers = {
                'apikey': NEXUS_API_KEY
            }
            response = requests.get(NEXUS_FILE_URL+f'.json', headers=nexus_headers)
            response.raise_for_status()
            file_id = response.json()['files'][-1]['id'][0]
            response = requests.get(NEXUS_FILE_URL+f'/{file_id}/download_link.json', headers=nexus_headers)
            response.raise_for_status()
            tweaks_download_link = response.json()[0]['URI']
            urllib.request.urlretrieve(tweaks_download_link, temp_dir.name+"/DLSSTweaks.zip")
            with zipfile.ZipFile(temp_dir.name+"/DLSSTweaks.zip", 'r') as zip_ref:
                zip_ref.extractall(temp_dir.name+"/DLSSTweaks")

print(os.listdir(temp_dir.name))
