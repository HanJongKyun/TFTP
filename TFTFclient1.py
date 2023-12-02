#!/usr/bin/python3
'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''
import socket
import argparse
# import validators
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
MODE = {'netascii': 1, 'octet': 2, 'mail': 3}

ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}
def send_wrq(filename, mode):
    format_string = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format_string, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)
    print(wrq_message)

def send_rrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    print(rrq_message)

def send_ack(seq_num, server):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    print(seq_num)
    print(ack_message)


parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str)
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()


# UDP 소켓 생성
server_ip = args.host
server_port = DEFAULT_PORT
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

if operation.lower() == 'get':
    send_rrq(filename, mode)
elif operation.lower() == 'put':
    send_wrq(filename, mode)
else:
    print("잘못된 동작입니다. 'get' 또는 'put'을 사용하세요.")
    exit()

file = open(filename, 'wb' if operation.lower() == 'get' else 'rb')
expected_block_number = 1

while True:
    data, server_new_socket = sock.recvfrom(516)
    opcode = int.from_bytes(data[:2], 'big')

    if opcode == OPCODE['DATA']:
        block_number = int.from_bytes(data[2:4], 'big')
        if block_number == expected_block_number:
            send_ack(block_number, server_new_socket)
            file_block = data[4:]

            if operation.lower() == 'get':
                file.write(file_block)

            expected_block_number = expected_block_number + 1
            print(file_block.decode())
        else:
            send_ack(expected_block_number - 1, server_new_socket)

    elif opcode == OPCODE['ERROR']:
        error_code = int.from_bytes(data[2:4], byteorder='big')
        if error_code == 1:
            print(f"파일 '{filename}'을(를) 찾을 수 없습니다.")
            file.close()
            exit()
        else:
            print(ERROR_CODE[error_code])
            break

    else:
        break

    if len(file_block) < BLOCK_SIZE:
        file.close()
        print(len(file_block))
        break

if operation.lower() == 'put':
    with open(filename, 'rb') as file_to_send:
        file_data = file_to_send.read(BLOCK_SIZE)
        while file_data:
            block_number = expected_block_number
            format_string = f'>hh{len(file_data)}s'
            data_message = pack(format_string, OPCODE['DATA'], block_number, file_data)

            try:
                sock.settimeout(5)
                sock.sendto(data_message, server_new_socket)

                expected_block_number += 1
                ack_data, _ = sock.recvfrom(4)
            except socket.timeout:

                print("TIMEOUT")
                break

            ack_opcode = int.from_bytes(ack_data[:2], 'big')
            ack_block_number = int.from_bytes(ack_data[2:], 'big')

            if ack_opcode == OPCODE['ACK'] and ack_block_number == block_number:
                print(f"블록 {block_number} 전송 완료")
            else:
                print("수신된 ACK에서 오류 발생.")
                break

            file_data = file_to_send.read(BLOCK_SIZE)

    file_to_send.close()
