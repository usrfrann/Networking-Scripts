import serial
import argparse
import getpass
import time
import logging

def send_command(serial_conn, command, wait=1):
    serial_conn.write(command.encode('utf-8') + b'\n')
    time.sleep(wait)
    response = serial_conn.read_all().decode('utf-8')
    logging.info(response)
    return response

def create_user(baud_rate=9600):
    HOST = ''
    USERTOADD = ''
    PASSWORD = ''
    PORT = ""
    parser = argparse.ArgumentParser(description=" Cisco Enable User Script")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--user_to_add", type=str, help="username to add to cisco device")
    parser.add_argument("--password_to_add", type=str, help="username to add to cisco device")
    parser.add_argument("--com-port", type=str, help="com_port")
    args = parser.parse_args()
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    com_port = args.com_port if args.com_port else input(f'Enter COM Port: (default:{PORT})')
    user_to_add = args.user_to_add if args.user_to_add else input(f'Enter User to Add (default: {USERTOADD}): ')
    password_to_add = args.password_to_add if args.password_to_add else input(f'Enter Password to Add for NewUser (default: {PASSWORD}): ')
    if not host:
        host = HOST
    if not user_to_add:
        user_to_add = USERTOADD
    if not password_to_add:
        password_to_add = PASSWORD
    if not com_port:
        com_port = PORT

    try:
        with serial.Serial(port=com_port, baudrate=baud_rate, timeout=1) as ser:
            logging.info(ser)
            ser.write(b'\r\n')
            time.sleep(1)
            ser.read_all()

            send_command(ser, 'enable')
            send_command(ser, 'configure terminal')

            send_command(ser, f"username {user_to_add} privilege 15 secret {password_to_add}")
            send_command(ser, 'line vty 0 4')


            send_command(ser, 'transport input ssh')
            send_command(ser, 'exit')
            send_command(ser, 'line con 0')
            send_command(ser, 'login local')
            send_command(ser, 'end')
            time.sleep(1)
            send_command(ser, 'write memory')
            send_command(ser, 'exit')
            logging.info("SSH has been enabled using VTY password")

            output = ser.read(4096).decode('utf-8')
            print(output)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    create_user()