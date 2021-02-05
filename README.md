# Minecraft-Home-Bot
A discord minecraft bot that enables you to play minecraft with your friends without port forwarding
This bot uses pyngrok and discord.py.

# Requirements
  - Good Internet connection
  - It is recommended that your PC has atleast 8 GB Ram
  - JRE installed and in the path

# Installation
  - First of all clone into this github repository
  - then open cmd and do ```pip install -r requirements.txt```
  - Go to https://ngrok.com/ and make an account for yourself then copy the authtoken and paste it in the [auth.txt](./auth.txt) file
  - Go to https://discord.com/developers/applications/ and make a new application. take note of the CLIENT ID and CLIENT SECRET
    - Then add a new bot.
    - Make a server on discord if you haven't already, then open the link
      - https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions=68608
      - while replacing {CLIENT_ID} with your client id
      - and then add the bot to your server
      - Then copy your CLIENT SECRET to [token.txt](./token.txt)
  - If you want to run your server on a specific version of minecraft then download and copy the server.jar for that specific version of minecraft and place it in the directory else the program will automatically download the latest version of minecraft as server.jar
  - Atlast run your server.
  
# Automation of server on user login
  - You can automate running the script on user login by using task scheduler
  
# Config
  - You can change the amount of ram allocated to the server by opening [server.py](./server.py) then changing the ram_alloc variable (in MBs)
