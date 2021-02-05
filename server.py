import discord
import datetime
import filecmp
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
import logging
from pyngrok import conf, ngrok

logging.basicConfig(filename=f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.INFO)

conf.get_default().region = "in"


def get_ip():
    tunnel = ngrok.connect(25565, "tcp")
    ip = tunnel.public_url[6:]

    return ip

def refresh():
    tunnels = ngrok.get_tunnels()

    return tunnels

def kill():

    ngrok_process = ngrok.get_ngrok_process()
    try:
        ngrok.kill()
    except:
        print("ngrok is already closed")

channel_name = "server-ip"

h = '''Start - Start the server
Refresh - Tell the IP if already started
Status - Tell the status of server (on/off)
Restart - Reboots the Server
Backup - Backup the server
execute <command> - Executes the command in the server
Stop - Stop the server'''


########
# Config
# ------
# server_type can be either 'snapshot' or 'release'
server_type = 'release'
# wait_time is the time to wait until checking for an update (in minutes)
wait_time = 120
# ram_alloc is the amount of ram (in MB) to allocate to the server
ram_alloc = 4096
# backups is whether or not you want backups
backups = True
# backup_at_wait_time is if you want a backup to be created every 'wait_time'
# Set to false by default as it could really fill your hard drive if you set
# your wait_time too low
backup_at_wait_time = True
# world_name is the name of your world, for backup purposes
world_name = 'world'
# backups_dir is the name of your backups folder
backups_dir = 'backups'
#######################

##################
# Global Variables
# ----------------
server = ''
version = ''
server_url = ''
version_updated = False
server_stopped = True
#####################

##################
# Helper Functions
# ----------------
# Send output to console
def m(message):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + message)

# Send command to server
def c(command):
    global server

    server.stdin.write((command + '\n').encode())
    server.stdin.flush()

def zipdir(path, ziph):
    for root, dirs, files in os.walk(world_name):
        for file in files:
            if file != "session.lock":
                ziph.write(os.path.join(root, file))

def get_mc_version():
    global version

    with open('versions.json') as versions_file:
        versions = json.load(versions_file)

    if server_type == 'snapshot':
        version = versions["latest"]["snapshot"]
    else:
        version = versions["latest"]["release"]

def get_mc_server_url():
    global version
    global server_url
    version_json = ''

    with open('versions.json') as versions_file:
        versions = json.load(versions_file)

    for version_entry in versions["versions"]:
        if version_entry["id"] == version and version_entry["type"] == server_type:
            version_json = version_entry["url"]
            break

    if version_json is not '':
        urllib.request.urlretrieve(version_json, 'version.json')
        with open('version.json') as version_file:
            version_json_file = json.load(version_file)
            server_url = version_json_file["downloads"]["server"]["url"]
###############################################

################
# Main Functions
# --------------
def version_check():
    global version_updated

    m('Checking to see if update is needed...')
    urllib.request.urlretrieve('https://launchermeta.mojang.com/mc/game/version_manifest.json', 'versions_new.json')
    if not os.path.exists('versions.json') or not os.path.exists('server.jar') or not filecmp.cmp('versions_new.json','versions.json'):
        update_server()
    else:
        get_mc_version() # get current version here just so we have it
        m('Server already up to date. No update needed.')

def backup_world():
    if not server_stopped:
        c('say Backing up world.')

    m('Creating a backup of the world...')
    try:
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
        zipf = zipfile.ZipFile(backups_dir + '/' + world_name + '_' + version + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.zip', 'w')
        zipdir(world_name + '/', zipf)
        zipf.close()
        m('Backup created.')
    except:
        m('Unable to create backup.')

def update_server():
    global version
    global server_url

    if not server_stopped:
        stop_server(False)
    m('Updating server.jar, please wait...')
    shutil.copy2('versions_new.json','versions.json')
    
    # Create a backup of the world before we go on and start the new server
    if backups:
        backup_world()

    # get the version from the new json file
    get_mc_version()

    # get the server url from the version json file
    get_mc_server_url()

    urllib.request.urlretrieve(server_url, 'server.jar')

def start_server():
    global server
    global server_stopped
    
    if server_stopped:
        m('Starting server...')
        if os.name is 'nt':
            # we are running under windows
            server = subprocess.Popen('start /I /B java -Xmx' + str(ram_alloc) + 'm -Xms' + str(ram_alloc) + 'm -jar server.jar nogui', stdin=subprocess.PIPE, shell=True)
        elif os.name is 'posix':
            # we are running under mac/linux
            server = subprocess.Popen('java -Xmx' + str(ram_alloc) + 'm -Xms' + str(ram_alloc) + 'm -jar server.jar nogui', stdin=subprocess.PIPE, shell=True)
        else:
            m('Unable to detect which OS you are running, exiting...')
            sys.exit(0)
        server_stopped = False

def stop_server(now):
    global server
    global server_stopped

    m('Server stopping...')

    if now:
        c('stop')
        time.sleep(5)
        server.kill()
        server_stopped = True
    else:
        c('say The server is going down for update in 5 minutes!')
        time.sleep(240) # wait 4 minutes
        c('say The server is going down for update in 1 minute!')
        time.sleep(5) # wait a few seconds in between messages
        c('say The server will be back up shortly.')
        time.sleep(60) # wait one minute
        c('stop')
        time.sleep(10)
        server.kill()
        server_stopped = True

##################

#####################
# Main execution loop
# -------------------
# set window title
def start():
    m('Starting exectution...')

    while True:
        try:
            version_check()
            start_server()
            m('Going to sleep for ' + str(wait_time) + ' minutes...')
            time.sleep(wait_time * 60) # wait time
            m('Waking up to check for updates...')
            if backups and backup_at_wait_time:
                backup_world()

        except KeyboardInterrupt:
            stop_server(True)
            m('Exiting...')
            sys.exit(0)

try:
    
    token = open("token.txt", "r").read()
    auth = open("auth.txt").read()
    ngrok.set_auth_token(auth)

    client = discord.Client()


    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')


    @client.event
    async def on_message(message):

        if channel_name in str(message.channel).lower():

            if str(message.content).lower() == "start":

                if server_stopped:

                    print("starting")

                    start_server()
                    address = get_ip()

                    await message.channel.send(address)

                else:

                    await message.channel.send("Server has already started type 'refresh' to see the address again")


            elif str(message.content).lower() == "refresh":

                print("refreshing")

                tunnel = refresh()
                if tunnel == []:
                    await message.channel.send("Server not started. type 'start' to start the server")

                else:

                    for i in tunnel:
                        await message.channel.send(i.public_url[6:])


            elif str(message.content).lower() == "stop":

                if not server_stopped:

                    print("stopping")

                    stop_server(True)
                    kill()

                    await message.channel.send("Stopped")

                else:

                    await message.channel.send("Server not started")

            elif str(message.content).lower() == "status":

                print("Checking status")
                if server_stopped:
                    await message.channel.send("The server off right now. type 'start' to start the server")
                else:
                    await message.channel.send("The server is currently running")

            elif str(message.content).lower()[:len("execute")] == "execute":

                exe = message.content[len("execute")+1:]
                
                if server_stopped:
                    await message.channel.send("The server off right now. type 'start' to start the server")
                else:
                    print("executing", exe)
                    c(exe)

            elif str(message.content).lower() == "restart":

                print("REBOOT")
                if server_stopped:
                    await message.channel.send("The server off right now. type 'start' to start the server")
                else:
                    stop_server(True)
                    start_server()

            elif str(message.content).lower() == "backup":

                print("backing up")
                backup_world()
                await message.channel.send("Backup Done!")

            elif str(message.content).lower() == "help":

                await message.channel.send(h)

                    

        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")


    client.run(token)

except Exception as e:

    print(e)

finally:

    if not server_stopped:
        kill()
        stop_server(True)