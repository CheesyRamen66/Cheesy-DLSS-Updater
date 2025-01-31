import os
import requests
from bs4 import BeautifulSoup
from packaging import version
import urllib.request
import tempfile
import glob

DLSS_VERSIONS_URL = "https://www.techpowerup.com/download/nvidia-dlss-dll/"
GITHUB_DLL_URL="https://github.com/NVIDIA/DLSS/blob/main/lib/Windows_x86_64/rel/nvngx_dlss.dll"
DEFAULT_DLL_NAME="nvngx_dlss.dll"

def get_dlss_version():
    def fetch_dlss_page():
        # Fetches the HTML content of the DLSS download page.
        response = requests.get(DLSS_VERSIONS_URL)
        response.raise_for_status()
        return response.text

    html_content = fetch_dlss_page()

    soup = BeautifulSoup(html_content, 'html.parser')
    for header in soup.find_all('h3'):
        if 'NVIDIA DLSS DLL' in header.text:
            sibling_div = header.find_next_sibling('div')
            if sibling_div and sibling_div.find('span', class_='flag latest'):
                return header.text.strip()

print("We're updating to "+get_dlss_version())
with tempfile.TemporaryDirectory() as tempdirname:
    print('Created temporary directory', tempdirname)
    urllib.request.urlretrieve(GITHUB_DLL_URL, tempdirname+"/"+DEFAULT_DLL_NAME)
    print(glob.glob(tempdirname+"/*"))