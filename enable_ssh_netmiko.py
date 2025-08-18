from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass

#TODO REDO with PySerial so the script supports legacy devices 

def main():
    DEVICE_TYPE ='cisco_ios_serial'
    HOST  = '1'
    USERNAME = ''
    PASSWORD = ''
    SECRET = ''
    PORT = ''


    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--com-port", type=str, help="com_port")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    com_port = args.com_port if args.com_port else input(f'Enter COM Port: (default:{PORT})')
    if not username:
        username = USERNAME
    if not host:
        host = HOST
    if not com_port:
        com_port = PORT

    password = getpass.getpass("Enter your Password:")
    secret = getpass.getpass("Enter your Secret:")
    if not password:
        password = PASSWORD
    if not secret:
        secret = SECRET
    cisco_device = {
        'device_type': "cisco_ios_serial",
        'password': password,
        'secret': secret,
        'port': "COM9",
        'serial_settings':  {
            'baudrate': 9600,
            'parity': 'N',
            'stopbits': 1,
            'bytesize': 8,
        },

    }
    cisco_device = ConnectHandler(**cisco_device)
    cisco_device.enable()
    commands = [
        'hostname test3 '
        'ip domain-name test3.switch.us '
        'crypto key generate rsa modulus 2048  ' 
        'ip ssh version 2 '

    ]
    enable_ssh_only = [
        'line vty 0 15',
        'transport input ssh',
    ]

    output = cisco_device.send_config_set(commands)
    output_2 = cisco_device.send_config_set(enable_ssh_only)
    save_output = cisco_device.save_config()
    cisco_device.disconnect()
    print(output)
    print(save_output)

if __name__ == '__main__':
    main()