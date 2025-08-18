import logging

import serial
import argparse
import getpass
import time

from pycparser.ply.yacc import LRTable


#TODO REDO with PySerial so the script supports legacy devices

def send_command(serial_conn, command, wait=1):
    serial_conn.write(command.encode('utf-8') + b'\n')
    time.sleep(wait)
    response = serial_conn.read_all().decode('utf-8')
    logging.info(response)
    return response


def configure_ssh(baud_rate=9600):
    HOSTNAME = ""
    PORT = ""

    parser = argparse.ArgumentParser(description="Cisco Enable SSH Script")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--com-port", type=str, help="com_port")
    args = parser.parse_args()
    hostname = args.host if args.host else input(f'Enter Hostname (default: {HOSTNAME}): ')
    com_port = args.com_port if args.com_port else input(f'Enter COM Port: (default:{PORT})')
    if not hostname:
        hostname = HOSTNAME
    if not com_port:
        com_port = PORT

    try:
        with serial.Serial(port=com_port, baudrate=baud_rate, timeout=1) as ser:
            logging.info(f"Connected to {com_port} at baud rate {baud_rate}")

            ser.write(b'\r\n')
            time.sleep(1)
            ser.read_all()

            send_command(ser, 'enable')
            send_command(ser, 'configure terminal')

            send_command(ser, f'hostname {hostname}')
            send_command(ser, f'ip domain-name {hostname}')
            send_command(ser, 'crypto key generate rsa')
            send_command(ser, 'yes')
            send_command(ser, '2048')
            send_command(ser, 'ip ssh version 2')
            send_command(ser, 'line vty 0 4')
            send_command(ser, 'transport input ssh')
            send_command(ser, 'login local')
            send_command(ser, 'end')
            time.sleep(1)
            send_command(ser, 'write memory')
            send_command(ser, 'exit')

            logging.info("SSH has been enabled on the switch")
    except Exception as err:
        logging.error(err)




if __name__ == '__main__':

    configure_ssh()
