# TFTP
-네트워크 프로그래밍 기말과제-
TFTP 클라이언트를 구현한 것으로, 파일을 TFTP 프로토콜을 사용하여 서버로부터 가져오거나 서버에 전송할 수 있습니다.

-사용법 예시-
ip_address [-p port_mumber] <get|put> filename
ex) 203.250.133.88 <get|put> 1989057.txt
ip_address: TFTP 서버의 IP 주소
[-p port_mumber]: TFTP 서버의 포트 번호를 지정하지 않으면 기본 포트 69를 사용합니다.
<get|put>: 파일을 가져오기(get) 또는 파일을 서버에 전송하기(put) 작업을 선택합니다.
filename: 전송할 파일의 이름 또는 받아올 파일을 저장할 이름입니다.

-코드 구성-
OPCODE: TFTP 메시지 타입을 정의합니다.
MODE: 전송 모드를 정의합니다.
ERROR_CODE: 서버에서 받은 오류 코드에 대한 설명을 포함합니다.

send_wrq(filename, mode): 쓰기 요청(WRQ) 메시지를 서버에 보냅니다.
send_rrq(filename, mode): 읽기 요청(RRQ) 메시지를 서버에 보냅니다.
send_ack(seq_num, server): 확인 응답(ACK) 메시지를 서버에 보냅니다.

-주의사항-
파일이 없거나 액세스 권한이 없는 경우 오류 메시지가 출력됩니다.
전송 중에 타임아웃이 발생하면 "TIMEOUT" 메시지가 출력됩니다.
