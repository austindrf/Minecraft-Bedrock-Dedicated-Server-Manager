# Minecraft-Bedrock-Dedicated-Server-Manager
Downloads and auto-updates Minecraft Dedicated Server from "https://www.minecraft.net/en-us/download/server/bedrock"
To use this install Python (if it's not already installed) 
then run the program in the folder where you want the dedicated server to download/update to

this program automatically copies your server.properties file, worlds folder, valid_known_packs.json, permissions.json,
and allowlist.json over to the new server folder

the way the server.properties file is copied allows for new features to be added to it but only 
configured settings from the old server.properties file will be changed

Also, this program will delete any zip folders where the name 
starts with bedrock-server (only in the current directory)

You can use 'pyinstaller' to make this program easier to use 
pyinstaller --onefile '.\Minecraft Server Updater.py'

Folder should look like this:
any folder/
            bedrock-server-version/
            Minecraft Server Updater.py
            Server_Updater_Settings.txt

server updater settings allow for archives of old servers to be saved 
under ./archives/bedrock-server-version-archive.tar.gz
also to remove old server folders automatically 
