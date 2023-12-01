#!/usr/bin/python3
'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''
import socket
import argparse.
# import validators
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'

# TFTP 메시지 타입 및 모드 정의
OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
MODE = {'netascii': 1, 'octet': 2, 'mail': 3}

# 서버에서 받은 오류 코드 정의
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

# WRQ(쓰기 요청) 메시지를 보내는 함수
def send_wrq(filename, mode):
    format_string = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format_string, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)
    print(wrq_message)

# RRQ(읽기 요청) 메시지를 보내는 함수
def send_rrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    print(rrq_message)

# ACK(확인 응답) 메시지를 보내는 함수
def send_ack(seq_num, server):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    print(seq_num)
    print(ack_message)


# ArgumentParser 객채 생성
parser = argparse.ArgumentParser(description='TFTP client program')
# 서버의 IP 주소에 대한 위치 인수 정의
parser.add_argument(dest="host", help="Server IP address", type=str)
# 수행할 작업 get or put 에 대한 위치 인수 정의
parser.add_argument(dest="operation", help="get or put a file", type=str)
# 전송할 파일 이름에 대한 위치 인수 정의
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
# 포트번호에 대한 옵션 인수 정의
parser.add_argument("-p", "--port", dest="port", type=int)
# 명령행 인수를 구문 분석하고 결과를 args 변수에 저장
args = parser.parse_args()


# UDP 소켓 생성
server_ip = args.host # args 에서 가져온 서버 IP주소
server_port = DEFAULT_PORT # 기본 포트 번호 설정
server_address = (server_ip, server_port) # 서버 주소를 튜플로 설정 (IP 주소, 포트번호)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 소켓 모듈을 사용하여 소켓 생성

# 전송 모드 및 작업, 파일 이름 설정
mode = DEFAULT_TRANSFER_MODE # 전송 모드를 기본값 DEFAULT_TRANSFER_MODE 설정
operation = args.operation # args 에서 가져온 작업 get or put 설정
filename = args.filename # args에서 가져온 전송할 파일 이름 설정

# 동작에 따라 RRQ 또는 WRQ 메시지 전송
if operation.lower() == 'get':
    send_rrq(filename, mode)
elif operation.lower() == 'put':
    send_wrq(filename, mode)
else:
    print("잘못된 동작입니다. 'get' 또는 'put'을 사용하세요.")
    exit()

# 파일 열기: 읽기 모드(rb) 또는 쓰기 이진 모드(wb)로 설정
# 작업이 get인 경우 쓰기 이진 모드로 파일을 열어서 받아올 파일을 준비
# 작업이 put인 경우 읽기 이진 모드로 파일을 열어서 전송할 파일을 준비
file = open(filename, 'wb' if operation.lower() == 'get' else 'rb')
# 예상 블록 번호 설정
# 클라이언트가 서버로부터 받을 파일의 첫 번째 블록 번호를 1로 설정
expected_block_number = 1

while True:
    # 서버에서 데이터 수신
    data, server_new_socket = sock.recvfrom(516)
    opcode = int.from_bytes(data[:2], 'big')

    if opcode == OPCODE['DATA']:
        # 서버로부터 받은 DATA 메시지 처리
        block_number = int.from_bytes(data[2:4], 'big')
        if block_number == expected_block_number:
            # 블록 번호가 예상과 일치하면 ACK 전송
            send_ack(block_number, server_new_socket)
            file_block = data[4:]

            # get 동작인 경우 받은 데이터를 파일에 작성
            if operation.lower() == 'get':
                file.write(file_block)

            expected_block_number = expected_block_number + 1
            print(file_block.decode())
        else:
            # 순서가 맞지 않는 블록 번호에 대한 ACK 전송
            send_ack(expected_block_number - 1, server_new_socket)  # 중복된 블록에 대해 이전 ACK 재전송

    elif opcode == OPCODE['ERROR']:
    # 서버로부터 받은 ERROR 메시지 처리
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

    # 받은 블록이 마지막 블록인지 확인
    if len(file_block) < BLOCK_SIZE:
        file.close()
        print(len(file_block))
        break

# put 동작인 경우 파일을 읽고 내용을 서버에 전송
if operation.lower() == 'put':
    # 전송할 파일을 이진 읽기 모드(rb)로 열기
    with open(filename, 'rb') as file_to_send:
        # 파일 데이터를 읽고 블록 단위로 전송
        file_data = file_to_send.read(BLOCK_SIZE)
        while file_data:
            # 현재 블록 번호 및 데이터를 패킹하여 데이터 메시지 생성
            block_number = expected_block_number
            format_string = f'>hh{len(file_data)}s'
            data_message = pack(format_string, OPCODE['DATA'], block_number, file_data)

            try:
                # 소켓 타임아웃 설정 및 데이터 메시지 전송
                sock.settimeout(5)
                sock.sendto(data_message, server_new_socket)

                expected_block_number += 1
                # ACK 수신 대기
                ack_data, _ = sock.recvfrom(4)
            except socket.timeout:
                # 타임아웃 발생 시 처리
                print("TIMEOUT")
                break

            ack_opcode = int.from_bytes(ack_data[:2], 'big')
            ack_block_number = int.from_bytes(ack_data[2:], 'big')

            # ACK 수신 확인 및 로그 출력
            if ack_opcode == OPCODE['ACK'] and ack_block_number == block_number:
                print(f"블록 {block_number} 전송 완료")
            else:
                print("수신된 ACK에서 오류 발생.")
                break

            # 다음 블록을 읽기
            file_data = file_to_send.read(BLOCK_SIZE)

    # 모든 블록을 전송한 후 파일 닫기
    file_to_send.close()


