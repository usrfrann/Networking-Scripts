import logging
import os
import datetime
import argparse
import shutil

def create_wslconfig_file(name_for_bridge):
    user_profile = os.environ['USERPROFILE']
    wslconfig_path = os.path.join(user_profile, '.wslconfig')

    wsl2_section_header = "[wsl2]"
    network_mode_line = "networkingMode=bridged"
    vm_switch_line = f"vmSwitch={name_for_bridge}"

    if not os.path.exists(wslconfig_path):
        with open(wslconfig_path, "w", encoding="utf-8") as wslconfig:
            wslconfig.write(f"{wsl2_section_header}\n")
            wslconfig.write(f"{network_mode_line}\n")
            wslconfig.write(f"{vm_switch_line}\n")
        print(f"Created new {wslconfig_path} with bridging settings")
        logging.info(f"Created {wslconfig_path} with bridging settings")
        return

    with open(wslconfig_path, "r", encoding="utf-8") as wslconfig:
        lines = wslconfig.readlines()

    found_wsl2 = any(line.strip().lower() == wsl2_section_header.lower() for line in lines)
    found_network_mode = any(line.strip().startswith("networkingMode") or line.strip().startswith("networkMode") for line in lines)
    found_vm_switch_external = any(line.strip().lower() == vm_switch_line.lower() for line in lines)
    found_network_mode_set =  any(line.strip().lower() == network_mode_line.lower() for line in lines)
    #IF No NetworkMode Line -> Append bridge lines
    if not found_network_mode:
        backup_name = f".wslconfig.bak_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        shutil.copy(wslconfig_path, backup_name)
        print(f"Created {backup_name} with old settings")
        logging.info(f"Created {backup_name} with old settings")
        print("A 'wslconfig' file has been found do you want to append to it?")
        response = input("Type 'y' for yes and 'n' for no: ")
        if response.lower().startswith("y"):
            with open(wslconfig_path, "a", encoding="utf-8") as wslconfig:
                if not found_wsl2:
                    wslconfig.write(f"{wsl2_section_header}\n")
                wslconfig.write(f"{network_mode_line}\n")
                wslconfig.write(f"{vm_switch_line}\n")
            print(f"Appended {wslconfig_path} with bridging settings")
            logging.info(f"Appended {wslconfig_path} with bridging settings")
    else:
        if not found_vm_switch_external or not found_network_mode_set:
            print("You already have an existing 'wslconfig' file")
            print("In your existing wslconfig file you have a NetworkMode")
            print("Do you want the program to comment out the settings and reconfigure and create a backup of original")
            print("Danger this can be destructive if you have existing settings")
            print("Type 'yes' to overwrite your existing wslconfig file")
            backup_name = f".wslconfig.bak_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            shutil.copy(wslconfig_path, backup_name)
            print(f"Created {backup_name} with old settings")
            logging.info(f"Created {backup_name} with old settings")
            response = input("Type 'yes' for yes and 'n' for no: ")
            if response.lower() == "yes":
                new_lines = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith("networkMode") or stripped_line.startswith("vmSwitch") or stripped_line.startswith("networkingMode"):
                        new_lines.append("# " + line)
                    else:
                        new_lines.append(line)
                if not found_wsl2:
                    new_lines.append(f"{wsl2_section_header}\n")
                new_lines.append(f"{network_mode_line}\n")
                new_lines.append(f"{vm_switch_line}\n")
                with open(wslconfig_path, "w", encoding="utf-8") as wslconfig:
                    wslconfig.writelines(new_lines)
        else:
            print(f"You already have an existing 'wslconfig' file")
            print("In your existing wslconfig file you have a NetworkMode")
            print("You have the correct vmswitch settings in that file")


if __name__ == "__main__":
    create_wslconfig_file()


