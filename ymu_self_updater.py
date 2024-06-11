import os
import requests
import shutil
import sys
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep


def get_ymu_tag():
    try:
        r = requests.get('https://github.com/NiiV3AU/YMU/tags')
        soup = BeautifulSoup(r.content, 'html.parser')
        result = soup.find(class_= 'Link--primary Link')
        s = str(result)
        result = s.replace('</a>', '')
        charLength = len(result)
        latest_version = result[charLength - 6:]
        return latest_version   
    except requests.exceptions.RequestException as e:
       print(f'Failed to get the latest Github version. Check your Internet connection and try again.\nError message: {e}')


EXE_URL = f'https://github.com/NiiV3AU/YMU/releases/download/{get_ymu_tag()}/ymu.exe'
LOCAL_EXE = './ymu.exe'
REM_VER = get_ymu_tag()

def banner():
 os.system("cls")
 print("            \033[1;36;40m YMU Updater")
 print("\n")
 print("    \033[1;32;40m https://github.com/NiiV3AU/YMU")
 print("\n\n") 

def on_success():
    input(f'\n    YMU has been sucessfully updated to {REM_VER}. Press Enter to exit.')
    # run the updated version
    os.execvp('./ymu.exe', ['ymu'])
    
def update_ymu():
    banner()
    if os.path.isfile('./ymu.exe'):
        if not os.path.exists('./_backup'):
            os.makedirs('./_backup')
        try:
            shutil.copy2('./ymu.exe', './_backup')
            with requests.get(EXE_URL, stream = True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))
                downloaded_size = 0
                with open(LOCAL_EXE, "wb") as f:
                    for chunk in r.iter_content(chunk_size = 128000):  # 64 KB chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress = downloaded_size / total_size * 100
                        display_progress = int(progress)
                        print("", end = f"\r    Downloading YMU {REM_VER}:   {display_progress} %", flush = True)
            print("")
        except requests.exceptions.RequestException as e:
            print(f'    Failed to download YMU. Check your Internet connection and try again.\nError message: {e}')
            #revert changes
            shutil.copy2('./_backup/ymu.exe', './')
            sys.exit(0)
        # remove backup folder and its contents
        os.remove('./_backup/ymu.exe')
        os.removedirs('./_backup')
        on_success()
    else:
        print("    'ymu.exe' not found! Aborting operation in a few seconds...")
        sleep(3)
        sys.exit(0)

if __name__ == "__main__":
    update_ymu()