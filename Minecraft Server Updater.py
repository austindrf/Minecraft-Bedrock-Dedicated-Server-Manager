
import importlib, subprocess
required_libraries = ["requests", "urllib3", "tqdm"]
s=False
for library in required_libraries:
    try:
        importlib.import_module(library)
    except ImportError:
        print("====installing missing library:"+library+"====")
        subprocess.check_call(['pip', 'install', library])
        s=True
import requests, urllib3, logging, zipfile, shutil, tarfile, time, math
from tqdm import tqdm
from datetime import datetime
if s:
    print("====finished installing missing librarys====")


global debug
debug=False

import subprocess
import time

class BedrockServerController:
    def __init__(self, server_path):
        self.server_path = server_path
        self.server_process = None

    def start_bedrock_server(self):
        try:
            self.server_process = subprocess.Popen([self.server_path], stdin=subprocess.PIPE)
            print("Bedrock Server started successfully.")
        except Exception as e:
            print(f"Error starting Bedrock Server: {e}")

    def stop_bedrock_server(self):
        if self.server_process:
            try:
                # Send "stop" command to the server
                self.send_command("stop")
                self.server_process.communicate(timeout=10)
                print("Sent 'stop' command to the Bedrock Server.")
            except subprocess.TimeoutExpired:
                print("Timeout expired while waiting for Bedrock Server to stop.")
                self.server_process.terminate()
            except Exception as e:
                print(f"Error stopping Bedrock Server: {e}")
            finally:
                self.server_process.wait()
        else:
            print("Bedrock Server is not running.")

    def send_command(self, command):
        if self.server_process:
            try:
                # Send a command to the server
                command = command + "\n"
                self.server_process.stdin.write(command.encode())
                self.server_process.stdin.flush()
                print(f"Sent '{command.strip()}' command to the Bedrock Server.")
            except Exception as e:
                print(f"Error sending command to Bedrock Server: {e}")
        else:
            print("Bedrock Server is not running.")

# Disable SSL/TLS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
if debug:
    logging.basicConfig(level=logging.DEBUG)



            

def mc_version():#finds the current minecraft version
    try:
        # Make an HTTP GET request with a timeout of 10 seconds
        with requests.get("https://www.minecraft.net/en-us/download/server/bedrock", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False) as response:
            # Log request and response details
            if debug:
                logging.debug(f"Request URL: {response.url}")
                logging.debug(f"Request Headers: {response.request.headers}")
                logging.debug(f"Response Headers: {response.headers}")

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Print or save the HTML content
                html_content = response.text
                mc_vs=str(str(html_content.split("""href="https://minecraft.azureedge.net/bin-win/bedrock-server-""")[1]).split(".zip")[0])
                return "bedrock-server-"+mc_vs
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                return "error"
    except requests.RequestException as e:
        if debug:
            logging.error(f"Error: {e}")
        print("error finding minecraft version")
        return "error"
import os

def old_mcserver_file(vs):#finds the last minecraft server folder
    p=[]
    z=""
    ver=int(str(vs.replace("bedrock-server-", "")).replace(".", ""))
    files = os.listdir(".")
    for file in files:
        if not(file.endswith(".zip")) and file.startswith("bedrock-server-"):
            fl=file.replace("bedrock-server-", "")
            qua=int(str(fl).replace(".", ""))
            if qua<ver:
                p.append(file)
            if qua==ver:
                z=file
    if len(p)==1:
        return str(p[0])
    elif len(p)==0:
        if z=="":
            return "na"
        else:
            return z
    else:
        p.sort()
        return str(p[len(p)-1])

                

def delete_zip_files():
    directory="."
    try:
        # List all files in the specified directory
        files = os.listdir(directory)

        # Iterate over each file
        for file in files:
            # Check if the file ends with ".zip"
            if file.endswith(".zip") and file.startswith("bedrock-server"):
                file_path = os.path.join(directory, file)
                
                # Delete the file
                os.remove(file_path)
                print(f"Deleted: {file_path}")

    except Exception as e:
        print(f"Error: {e}")


def archive_folder(oldvs):
    try:
        # Ensure that the archive folder exists
        archive_folder_path = "./archive/"
        os.makedirs(archive_folder_path, exist_ok=True)
        # Create a tar.gz (gzip) archive
        print("Archiving " + oldvs)
        archive_path = "./archive/" + oldvs + "-archive.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            # Walk through the source folder and add each file to the archive
            source_folder = "./" + oldvs + "/"
            files_to_archive = [os.path.join(root, file) for root, dirs, files in os.walk(source_folder) for file in files]
            
            for file_path in tqdm(files_to_archive, desc="Creating Archive", unit="file"):
                arcname = os.path.relpath(file_path, source_folder)
                tar.add(file_path, arcname=arcname)

        print(f"Folder '{oldvs}' compressed to '{archive_path}'")
        return True
    except FileNotFoundError:
        print(f"Error: Source folder '{oldvs}' not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
# Call the function with the current directory


def download_server(vs):
    # Replace this URL with the actual URL of the file you want to download
    file_url = "https://minecraft.azureedge.net/bin-win/" + vs + ".zip"
    # Replace this with the desired local file name
    local_file_name = vs + ".zip"

    try:
        # Make an HTTP GET request to the file URL with streaming
        print("Downloading '" + local_file_name + "'")
        with requests.get(file_url, stream=True) as response:
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Get the total file size from the Content-Length header
                file_size = int(response.headers.get("Content-Length", 0))

                # Use tqdm to create a progress bar for the download
                with open(local_file_name, "wb") as file, tqdm(
                    desc="Downloading",
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        file.write(data)
                        bar.update(len(data))

                print(f"File '{local_file_name}' downloaded successfully.")
                return True
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")
                return False
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False


def extract_zip(vs):
    try:
        zip_file_path = vs + ".zip"
        output_folder = vs

        print("Extracting: " + zip_file_path)
        
        # Check if the zip file exists
        if not os.path.exists(zip_file_path):
            print(f"Error: Zip file '{zip_file_path}' not found.")
            return False

        # Check if the output folder exists, create it if not
        os.makedirs(output_folder, exist_ok=True)

        # Get the total number of entries in the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            total_entries = len(zip_ref.infolist())

        # Use tqdm to create a progress bar for the extraction
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref, \
                tqdm(total=total_entries, desc="Extracting", unit="file") as pbar:
            for file_info in zip_ref.infolist():
                zip_ref.extract(file_info, output_folder)
                pbar.update(1)

        print(f"Extraction complete. Files extracted to: '{output_folder}'")
        return True
    except zipfile.BadZipFile as e:
        print(f"Error: '{zip_file_path}' is not a valid zip file.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
def delete_unneeded_files(vs):
    del_list=[
        "allowlist.json",
        "bedrock_server_how_to.html",
        "permissions.json"]
    
    for filename in del_list:      
        # Delete the file
        os.remove("./"+vs+"/"+filename)
        print(f"Deleted: ./"+vs+"/"+filename)
def delete_folder(oldvs):
    print("deleting folder: "+oldvs)
    try:
        shutil.rmtree(oldvs)
        print("successfully deleted folder: "+oldvs)
        return True
    except Exception as e:
        print("Failed to delete folder: "+oldvs)
        print(e)
        return False
def parse_server_propertys(vs, oldversion):
    srvpropset=[]    
    oldsrv=open(oldversion+"/server.properties", "r", encoding="utf-8")
    for z in oldsrv.readlines():
        if not(z.startswith("#") or z.startswith("\n")):
            srvpropset.append(str(z.replace("\n", "")).split("="))
    oldsrv.close()
    #print(srvpropset)
    newsrv=open(vs+"/server.properties", "r", encoding="utf-8")
    n=[]
    for i in newsrv.readlines():
        n.append(i)
    newsrv.close()
    #print(n)
    for i in n:
        if not(str(i).startswith("\n") or str(i).startswith("#")):
            for z in srvpropset:
                if i.split("=")[0]==z[0]:
                    n[n.index(i)]=z[0]+"="+z[1]+"\n"
                    #print("match")
    #print(n)
    newsrv=open(vs+"/server.properties", "w", encoding="utf-8")
    newsrv.write("")
    newsrv.close()   
    newsrv=open(vs+"/server.properties", "a", encoding="utf-8")
    for i in n:
        newsrv.write(i)
    newsrv.close() 

def copy_worlds(vs, oldversion):
    try:
        source_folder = os.path.join(oldversion, "worlds")
        destination_folder = os.path.join(vs, "worlds")

        print("Copying worlds folder ...")

        # Calculate the total size of the source folder
        total_size = get_folder_size(source_folder)

        # Use tqdm to create a progress bar for the copy
        with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as pbar:
            shutil.copytree(source_folder, destination_folder, copy_function=progress_bar_copy(pbar))

        print(f"Folder copied from '{source_folder}' to '{destination_folder}'")
        return True
    except FileExistsError:
        print(f"Error: Destination folder '{destination_folder}' already exists.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def progress_bar_copy(pbar):
    def inner_copy(src, dst, *args, **kwargs):
        shutil.copy2(src, dst, *args, **kwargs)
        pbar.update(os.path.getsize(src))

    return inner_copy
def get_folder_size(folder):
    total_size = 0
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_folder_size(entry.path)
    return total_size

def copy_other(vs, oldversion):
    
    
    fi=["valid_known_packs.json", "permissions.json", "allowlist.json"]
    for f in fi:
        try:
            # Copy the file to the destination folder
            shutil.copy2(oldversion+"/"+f, vs+"/")

            print(f"File '{oldversion}/{f} copied to '"+vs+"/'")

        except FileNotFoundError:
            print(f"Error: Source file '{oldversion}/{f} not found.")
        except IsADirectoryError:
            print(f"Error: '{oldversion}/{f} is a directory, not a file.")
        except Exception as e:
            print(f"Error: {e}")



def get_ts():#returns the current time in seconds
    now = datetime.now()
    timestamp = time.mktime(now.timetuple())
    return int(timestamp)

def seconds_since_last_update_search(tm):
    return int(math.fabs(float(get_ts())-float(tm)))
def sp(i, val):
    if str(i).__contains__(val):
        return str(str(i.replace(val, "")).split("\n")[0])
    else:
        return "?"

def Read_Settings_file():
    servset=[]
    run=True
    while run:
        try:
            f=open("Server_Updater_Settings.txt", "r")
            for i in f.readlines():
                servset.append(i)
            f.close()
            run=False
        except:
            f=open("Server_Updater_Settings.txt", "w")
            settings="""Last_Update_Search_Time:0
Current_Server_Version=="""+old_mcserver_file("999999999999").replace("bedrock-server-", "")+"""

Check_For_Updates(Frequncy-seconds-int)==86400

Archive_Old_folder(bool)==True

Delete_Old_Server_Folder(Bool)==True

Archive_before_deleting_old(Bool)==True
"""
            f.write(settings)
            f.close()
            input("Press enter after editing settings file")
    settings=[
        ["Last_Update_Search_Time:",""],
        ["Current_Server_Version==",""],
        ["Check_For_Updates(Frequncy-seconds-int)==",""],
        ["Archive_Old_folder(bool)==",""],
        ["Delete_Old_Server_Folder(Bool)==", ""],
        ["Archive_before_deleting_old(Bool)==", ""]]
    for i in servset:
        for st in settings:
            s=sp(i, st[0])
            if not(s=="?"):
                settings[settings.index((st))][1]=s
    lastupsearch=settings[0][1]
    servervrs=settings[1][1]
    freq=settings[2][1]
    archive_old=settings[3][1]
    del_old=settings[4][1]
    ar_be_dl_ol=settings[5][1]
    return (str(lastupsearch), servervrs, freq, archive_old, del_old, ar_be_dl_ol)
def file_update_time(lastup):
    f=open("Server_Updater_Settings.txt", "r")
    q=f.read().replace("Last_Update_Search_Time:"+str(lastup), "Last_Update_Search_Time:"+str(get_ts()))
    f.close()
    f=open("Server_Updater_Settings.txt", "w")
    f.write(q)
    f.close()

def file_update_version(last_vs, vs):
    f=open("Server_Updater_Settings.txt", "r")
    q=f.read().replace("Current_Server_Version=="+str(last_vs.replace("bedrock-server-", "")), "Current_Server_Version=="+str(vs.replace("bedrock-server-", "")))
    f.close()
    f=open("Server_Updater_Settings.txt", "w")
    f.write(q)
    f.close()

def start_server():
    global controller
    global server_path
    server_path = "./"+old_mcserver_file("999999999")+"/bedrock_server.exe"
    controller = BedrockServerController(server_path)
    print("starting server V"+old_mcserver_file("999999999"))
    controller.start_bedrock_server()
   
def stop_server(oldvs, vs):
    for t in range(1, 6):#title that appears on players screen saying that the server is about to shut down
        controller.send_command("title @a title Shuting down to update")
        controller.send_command("title @a subtitle "+oldvs+" to "+vs+" in "+str(6-t))
        time.sleep(1)
    controller.stop_bedrock_server()
    print("stoping server")

global controller
global server_path
server_path = "./"+old_mcserver_file("999999999")+"/bedrock_server.exe"
controller = BedrockServerController(server_path)# used to run the server as a child process so python can interact with it (safely shutdown or automate server commands)
settings=Read_Settings_file()
run=True
oldvs=old_mcserver_file("999999999")#setting this to a number higher than the current minecraft version makes it find the newest minecaft server folder
if oldvs=="na":
    print("No server folder found - downloading and extracting") 
    vs=mc_version()
    ds=download_server(vs)
    if ds:
        ez=extract_zip(vs)
        if ez:
            file_update_time(settings[0])
            file_update_version("na", vs)
            delete_zip_files()
    input("configure server.properties then press enter")
try:
    start_server()
except:
    print("failed to find server")

if __name__ == "__main__":
    try:
        while run:
            settings=Read_Settings_file()
            if int(settings[2])<=0 and run:
                run=False
                print("Update Freqency set to 0 - runing program once")
            if seconds_since_last_update_search(settings[0])>int(settings[2])and not(oldvs=="na"):
                file_update_time(settings[0])
                vs=mc_version()
                oldvs=old_mcserver_file(vs)
                print("\rold:"+oldvs)
                print("new:"+vs)
                if not(oldvs=="na"):
                    if not(vs=="error") and int(str(vs.replace("bedrock-server-", "")).replace(".", ""))>int(str(old_mcserver_file("999999999").replace("bedrock-server-", "")).replace(".", "")):
                        file_update_version(old_mcserver_file("999999999"), vs)
                        print("New server update avalible")
                        ds=download_server(vs)
                        if ds:
                            ez=extract_zip(vs)
                            if ez:
                                stop_server(oldvs, vs)
                                print("waiting for server to stop")
                                controller.server_process.wait()
                                print("server stopped")
                                delete_zip_files()
                                delete_unneeded_files(vs)
                                parse_server_propertys(vs, oldvs)
                                copy_other(vs, oldvs)
                                lg=copy_worlds(vs, oldvs)
                                if lg:
                                    print("the server is ready to start")
                                    start_server()
                                    file_update_time(settings[1])
                                    if settings[5]=="True":
                                        if settings[3]=="True":
                                            print("this one")
                                            af=archive_folder(oldvs)
                                            if af and settings[4]=="True":
                                                shutil.rmtree(oldvs)
                                    else:
                                        if settings[3]=="True":
                                            af=archive_folder(oldvs)
                                        if settings[4]=="True":
                                            shutil.rmtree(oldvs)
                            else:
                                print("Zip Extraction Failed")
                        else:
                            print("Download Failed")
                    elif (vs=="error"):
                        print("Failed to get current version")
                    else:
                        print("Current version matches most recent version")
                else:
                    print("No server folder found - downloading and extracting")   
                    ds=download_server(vs)
                    if ds:
                        ez=extract_zip(vs)
                        if ez:
                            file_update_time(settings[0])
                            file_update_version("na", vs)
                            delete_zip_files()
                            run = False
                        
            else:
                print("\rTime Since Last Search: "+str(seconds_since_last_update_search(settings[0]))+"    next search in "+str(int(settings[2])-seconds_since_last_update_search(settings[0])), end="", flush=True)
            try:
                time.sleep(1)
            except:
                run = False
                nul=""
            if (controller.server_process is None or controller.server_process.poll() is not None) and run:#restarts the server if it crashes
                print("Bedrock Server process is not running. Starting the server...")
                controller.start_bedrock_server()
            if not(run) and not(oldvs=="na"):
                controller.stop_bedrock_server()
                controller.server_process.wait()
                print("safely stoped server")
    except Exception as e:
        stop_server("", e)
        controller.server_process.wait()

input("press enter to close program")