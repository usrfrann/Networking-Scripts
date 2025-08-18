import subprocess
import logging
import ctypes
import sys
import json
import os
import argparse
from create_wslconfig import create_wslconfig_file

def main():
    try:
        current_user = os.getlogin()
        parser = argparse.ArgumentParser(description="Name for the ExternalNetworkBridge")
        parser.add_argument(
            "--external-bridge",
            "-b",
            default="ExternalLANBridge",
            help="Name of the ExternalNetworkBridge",
        )
        args = parser.parse_args()
        name_for_external_bridge = args.external_bridge
        user_input_for_external_bridge = input(
            f"Please Enter to Accept name of the ExternalNetworkBridge: {name_for_external_bridge} or type a new value")
        if user_input_for_external_bridge.strip():
            name_for_external_bridge = user_input_for_external_bridge

        create_wslconfig_file(name_for_external_bridge)

        command_get_vmswitch = "Get-VMSwitch | ConvertTo-Json"
        command_get_netadapt = '''Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.MediaType -eq "802.3" -and 
        $_.InterfaceDescription -notmatch "Virtual|Hyper-V|Loopback|TAP|vEthernet"
        } | ConvertTo-Json'''


        result = subprocess.run(["powershell", "-Command", command_get_vmswitch],
                                capture_output=True,
                                text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            #logging.info(output)
            if name_for_external_bridge in output:
                logging.info(f"{name_for_external_bridge} found in VMSwitch")
            else:
                logging.info(f"{name_for_external_bridge} not found in VMSwitch must create")
                result = subprocess.run(["powershell", "-Command", command_get_netadapt],
                                        capture_output=True,
                                        text=True)
                output = result.stdout.strip()
                data = json.loads(output)
                #This assumes you only have on physical active ethernet on you device otherwise you'd
                #Need to parse the list and find the adapter you are looking for,

                #TODO Try this when you have a few different physical interfaces, like on a desktop
                if isinstance(data, list):
                    ifdescr_list = [entry.get("InterfaceDescription") for entry in data]
                    ifalias_list = [entry.get("InterfaceAlias") for entry in data]
                else:
                    ifdescr_list = [data.get("InterfaceDescription")]
                    ifalias_list = [data.get("InterfaceAlias")]
                #PLEASE CHANGE THIS WHEN CAN BETTER TEST
                ifdescr = ifdescr_list[0]
                ifalias = ifalias_list[0]
                logging.info(ifdescr)
                logging.info(ifalias)
                command_new_vmswitch = f'New-VMSwitch -Name "{name_for_external_bridge}" -AllowManagementOS $true -NetAdapterName "{ifalias}"'
                result = subprocess.run(["powershell", "-Command", command_new_vmswitch],
                                        capture_output=True,
                                        text=True)
                output = result.stdout.strip()
                logging.info(output)
        else:
            logging.error(result.stderr)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logging.critical("This script must be run as administrator.")
        sys.exit(1)

    main()