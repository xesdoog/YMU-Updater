import atexit
import logging
import os
import requests
import shutil
import sys
from bs4  import BeautifulSoup
from time import sleep



logfile = open("./ymu/ymu.log", "a")
logfile.write("---Initializing YMU-Self Updater...\n\n")
logfile.close()
log = logging.getLogger("YMU-SU")
logging.basicConfig(filename = './ymu/ymu.log',
                    encoding = 'utf-8',
                    level    = logging.DEBUG,
                    format   = '%(asctime)s %(levelname)s %(name)s %(message)s',
                    datefmt  = '%H:%M:%S'
                    )


def get_ymu_tag():
    try:
        r = requests.get('https://github.com/NiiV3AU/YMU/tags')
        soup = BeautifulSoup(r.content, 'html.parser')
        result = soup.find(class_= 'Link--primary Link')
        s = str(result)
        result = s.replace('</a>', '')
        charLength = len(result)
        latest_version = result[charLength - 6:]
        log.info(f'Latest YMU version: {latest_version}')
        return latest_version   
    except requests.exceptions.RequestException as e:
       print(f'Failed to get the latest Github version. Check your Internet connection and try again.\nError message: {e}')
       log.exception(f'Failed to get the latest Github version. Check your Internet connection and try again. Traceback: {e}')


REM_VER = get_ymu_tag()
EXE_URL = f'https://github.com/NiiV3AU/YMU/releases/download/{REM_VER}/ymu.exe'
LOCAL_EXE = './ymu.exe'


def banner():
 os.system("cls")
 print("            \033[1;36;40m YMU Updater")
 print("    \033[1;32;40m https://github.com/NiiV3AU/YMU\033[0m")
 print("\n\n") 


def on_success():
    log.info('Download finished.')
    input(f'\n    YMU has been sucessfully updated to {REM_VER}. Press Enter to exit.')
    # run the updated version
    log.info(f'YMU has been sucessfully updated! Closing self updater and starting YMU {REM_VER}...\n\nFarewell!\n')
    os.execvp('./ymu.exe', ['ymu'])


def on_interrupt():
    if os.path.exists('./_backup'):
        if os.path.isfile('./_backup/ymu.exe'):
            shutil.copy2('./_backup/ymu.exe', './')
            os.remove('./_backup/ymu.exe')
        os.removedirs('./_backup')
    print('\n   \033[93mOperation canceled by the user. Reverting changes if any...\033[0m')
    log.warning('Operation canceled by the user. Reverting changes if any...\n')



def on_exit():
    log.info('Farewell!\n')


def update_ymu():
    banner()
    try:
        if os.path.isfile('./ymu.exe'):
            log.info('Found YMU executable')
            if not os.path.exists('./_backup'):
                os.makedirs('./_backup')
                log.info('Creating backup folder...')
            try:
                shutil.copy2('./ymu.exe', './_backup')
                log.info('Moving old YMU version into backup folder...')
                with requests.get(EXE_URL, stream = True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get("content-length", 0))
                    log.info(f'Starting download...')
                    log.info(f'Total size: {"{:.2f}".format(total_size/1048576)}MB')
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
                print(f'    \033[91mFailed to download YMU. Check your Internet connection and try again.\nError message: {e}\033[0m')
                #revert changes
                shutil.copy2('./_backup/ymu.exe', './')
                sys.exit(0)
            # remove backup folder and its contents
            os.remove('./_backup/ymu.exe')
            os.removedirs('./_backup')
            on_success()
        else:
            print("    \033[91m'ymu.exe' not found! Aborting operation in a few seconds...\033[0m")
            log.error("'ymu.exe' not found! Aborting operation in a few seconds...")
            sleep(3)
            sys.exit(0)
    except KeyboardInterrupt:
        on_interrupt()


atexit.register(on_exit)

if __name__ == "__main__":
    update_ymu()
