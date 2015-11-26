#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# Set language
# en: English, kr: Korean
msg_lang = 'en'

def set_msg_lang(lang_code):
    global msg_lang
    msg_lang = lang_code

def msg_welcome():
    print msg_lang
    if msg_lang == 'kr':
        return '안녕하세요!!'
    else:
        return 'Hello!!'

def msg_invalid_param():
    if msg_lang == 'kr':
        return '파리미터에 오류가 있습니다!!'
    else:
        return 'Invalid parameter!!'

def msg_devnum_error():
    if msg_lang == 'kr':
        return '장치넘버에 오류가 있습니다.'
    else:
        return 'Wrong device number'

def msg_device_not_found():
    if msg_lang == 'kr':
        return '장치를 찾을 수 없습니다.'
    else:
        return 'Cannot find device'

def msg_current_lang():
    if msg_lang == 'kr':
        return '현재언어설정'
    else:
        return 'Current language'

def msg_lang_changed():
    if msg_lang == 'kr':
        return '언어가 변경되었습니다.'
    else:
        return 'Language setting changed.'

def msg_cctv_on():
    if msg_lang == 'kr':
        return 'CCTV가 활성화 되었습니다.'
    else:
        return 'CCTV started!!'

def msg_cctv_already_on():
    if msg_lang == 'kr':
        return '이미 CCTV가 활성화 되어있습니다.'
    else:
        return 'CCTV is already active.'

def msg_cctv_off():
    if msg_lang == 'kr':
        return 'CCTV가 종료되었습니다.'
    else:
        return 'CCTV stopped.'

def msg_turnoff_cctv():
    if msg_lang == 'kr':
        return 'CCTV를 종료합니다.'
    else:
        return 'CCTV stopped.'

def msg_turnoff_cctv():
    if msg_lang == 'kr':
        return 'CCTV가 종료되었습니다.'
    else:
        return 'CCTV stopped.'

def msg_device_number():
    if msg_lang == 'kr':
        return '장치넘버'
    else:
        return 'Device number'

def msg_location():
    if msg_lang == 'kr':
        return '위치'
    else:
        return 'Located at'

def msg_category():
    if msg_lang == 'kr':
        return '분류'
    else:
        return 'Category'

def msg_devdesc_command():
    if msg_lang == 'kr':
        return '아래 명령어로 각 장치의 세부 내용을 볼 수 있습니다.\n장치 상세 (장치넘버)'
    else:
        return 'See the details with below command:\ndevice desc (device_number)'

def msg_update_time():
    if msg_lang == 'kr':
        return '등록시간'
    else:
        return 'Update time'

def msg_control_signal():
    if msg_lang == 'kr':
        return '제어신호'
    else:
        return 'Control signal'

def msg_data_type():
    if msg_lang == 'kr':
        return '데이터타입'
    else:
        return 'Data type'

def msg_ctrlsignal_desc():
    if msg_lang == 'kr':
        return '아래 명령어로 원격조종 신호를 보낼 수 있습니다.\n제어 (장치넘버) (신호1) (신호2) (신호3) (신호4)'
    else:
        return 'Control remote device with below command:\ncontrol (device_number) (signal1) (signal2) (signal3) (signal4)'

def msg_device_removed():
    if msg_lang == 'kr':
        return '장치 %d이 제거되었습니다.'
    else:
        return 'Device %d removed.'

def msg_device_remove_error():
    if msg_lang == 'kr':
        return '장치 %d 제거에 문제가 발생했습니다!!'
    else:
        return 'Failed in removing device %d!!'

def msg_every_device_removed():
    if msg_lang == 'kr':
        return '등록된 장치 정보가 모두 삭제되었습니다.'
    else:
        return 'Every device information is removed.'

def msg_every_device_remove_error():
    if msg_lang == 'kr':
        return '모든 장치정보 삭제에 문제가 발생했습니다!!'
    else:
        return 'Failed in removing every device!!'

def msg_sensordata_removed():
    if msg_lang == 'kr':
        return '장치 %d의 센서 정보가 제거되었습니다.'
    else:
        return 'Removed sensor data of device %d.'

def msg_sensordata_remove_error():
    if msg_lang == 'kr':
        return '장치 %d의 센서정보 제거에 문제가 발생했습니다!!'
    else:
        return 'Failed in removing sensor data of device %d!!'

def msg_every_sensordata_removed():
    if msg_lang == 'kr':
        return '센서 정보가 모두 삭제되었습니다.'
    else:
        return 'Removed every sensor data.'

def msg_every_sensordata_remove_error():
    if msg_lang == 'kr':
        return '모든 장치정보 삭제에 문제가 발생했습니다!!'
    else:
        return 'Failed in removing every sensor data!!'

def msg_need_devnum():
    if msg_lang == 'kr':
        return '장치넘버 파라미터가 필요합니다!!'
    else:
        return 'Need device number!!'

def msg_no_matching_result():
    if msg_lang == 'kr':
        return '장치에 해당하는 정보가 없습니다.'
    else:
        return 'No matching result.'

def msg_cannot_open_graph():
    if msg_lang == 'kr':
        return '그래프 파일을 열 수 없습니다!!'
    else:
        return 'Cannot open graph file!!'

def msg_wrong_device():
    if msg_lang == 'kr':
        return '잘못된 장치를 지정하셨습니다!!'
    else:
        return 'Wrong device number!!'

def msg_wrong_param1():
    if msg_lang == 'kr':
        return '파라미터1 값이 잘못되었습니다!!'
    else:
        return 'Param1 value is missing or not valid!!'

def msg_sent_signal():
    if msg_lang == 'kr':
        return '장치 %d에 제어 신호를 보냈습니다.'
    else:
        return 'Sent control signal to %d.'

def msg_recv_ping_response():
    if msg_lang == 'kr':
        return 'Ping 응답 신호를 받았습니다.'
    else:
        return 'Received ping response.'

def msg_ctrlsignal_response():
    if msg_lang == 'kr':
        return '제어신호에 대한 응답을 받았습니다.'
    else:
        return 'Received response:'

def msg_noti():
    if msg_lang == 'kr':
        return '알림'
    else:
        return 'Notification'

def msg_no_noti():
    if msg_lang == 'kr':
        return '알림 설정이 없습니다.'
    else:
        return 'Notification setting is not exist.'

def msg_type_noti_del_param():
    if msg_lang == 'kr':
        return '알림 삭제에 필요한 파라미터에 오류가 있습니다!! 아래와 같은 명령으로 삭제할 수 있습니다.\n알림 삭제 (알림ID)\n알림 삭제 (분류1) (분류2) (장치ID)'
    else:
        return 'Invalid parameters!! Use command like below:\nnoti del (noti-ID)\nnoti del (category1) (category2) (device ID)'

def msg_noti_del_success():
    if msg_lang == 'kr':
        return '알림을 삭제 했습니다.'
    else:
        return 'Removed notifications.'

def msg_noti_del_fail():
    if msg_lang == 'kr':
        return '알림 삭제에 실패했습니다!!'
    else:
        return 'Cannot remove notification!!'

def msg_add_noti_param():
    if msg_lang == 'kr':
        return '알림 추가 파라미터에 오류가 있습니다!! 아래와 같은 명령으로 추가할 수 있습니다.\n\n알림 추가 (장치넘버) (data1비교문) (data2비교문) (data3비교문) (data4비교문)\n\n예) 알림 추가 1 data1<10 data2==12 data3>=13 data4!=0\n\ndata1, data2, data3, data4 중 하나만 입력 가능'
    else:
        return 'Invalid parameters!! Use command like below:\n\nnoti add (device ID) (data1 comparison) (data2 comparison) ... (data4 comparison)\n\nEx) noti add 1 data1<7 data2==3 data3>=12 data4!=0\n\nAt least one comparison is needed.'

def msg_add_noti_comp_error():
    if msg_lang == 'kr':
        return '데이터 비교문에 오류가 있습니다!! 아래와 같은 형식을 사용하세요.\n\n알림 추가 (장치넘버) (data1비교문) (data2비교문) (data3비교문) (data4비교문)\n\n예) 알림 추가 1 data1<10 data2==12 data3>=13 data4!=0\n\ndata1, data2, data3, data4 중 하나이상 입력 필요'
    else:
        return 'Invalid comparison format!! Use command like below:\n\nnoti add (device ID) (data1 comparison) (data2 comparison) ... (data4 comparison)\n\nEx) noti add 1 data1<7 data2==3 data3>=12 data4!=0\n\nAt least one comparison is needed.'

def msg_noti_received():
    if msg_lang == 'kr':
        return '설정한 조건에 맞는 데이터가 업데이트 되었습니다!!'
    else:
        return 'HomePy received new update data that you want!!'

def msg_add_noti_success():
    if msg_lang == 'kr':
        return '알림을 추가했습니다.'
    else:
        return 'Added a new notification.'

def msg_add_noti_failed():
    if msg_lang == 'kr':
        return '알림을 DB에 추가하는 중 오류가 발생했습니다!!'
    else:
        return 'Error occured while inserting into DB!!'

def msg_invalid_noti_cmd():
    if msg_lang == 'kr':
        return '알림 커맨드에 오류가 있습니다!!'
    else:
        return 'Invalid notification command!!'

def msg_macro():
    if msg_lang == 'kr':
        return '매크로'
    else:
        return 'Macro'

def msg_no_macro():
    if msg_lang == 'kr':
        return '매크로 설정이 없습니다.'
    else:
        return 'Macro setting is not exist.'

def msg_type_macro_del_param():
    if msg_lang == 'kr':
        return '매크로 삭제에 필요한 파라미터에 오류가 있습니다!! 아래와 같은 명령으로 삭제할 수 있습니다.\n매크로 삭제 (매크로ID)\n매크로 삭제 (분류1) (분류2) (장치ID)'
    else:
        return 'Invalid parameters!! Use command like below:\nmacro del (macro-ID)\nmacro del (category1) (category2) (device ID)'

def msg_macro_del_success():
    if msg_lang == 'kr':
        return '매크로를 삭제 했습니다.'
    else:
        return 'Removed macro.'

def msg_macro_del_fail():
    if msg_lang == 'kr':
        return '매크로 삭제에 실패했습니다!!'
    else:
        return 'Cannot remove macro!!'

def msg_add_macro_param():
    if msg_lang == 'kr':
        return '매크로 추가 파라미터에 오류가 있습니다!! 아래와 같은 명령으로 추가할 수 있습니다.\n\n매크로 추가 (알림넘버) (명령문)\n\n예) 매크로 추가 1 제어 1 10'
    else:
        return 'Invalid parameters!! Use command like below:\n\nmacro add (noti ID) (command)\n\nEx) macro add 1 send 1 10'

def msg_invalid_noti_id():
    if msg_lang == 'kr':
        return '잘못된 알림 ID 입니다!!'
    else:
        return 'Invalid notification ID!!'

def msg_add_macro_success():
    if msg_lang == 'kr':
        return '매크로를 추가 했습니다.'
    else:
        return 'Added macro.'

def msg_add_macro_fail():
    if msg_lang == 'kr':
        return '매크로 추가에 실패했습니다!!'
    else:
        return 'Cannot add macro!!'



def msg_help_text():
    if msg_lang == 'kr':
        msg = """hello
홈파이 서버가 응답 가능한지 확인.

ping (장치넘버)
지정한 장치에 ping 신호를 보내 응답이 오는지 확인. 장치가 동작중인지 확인.

lang (en, kr)
언어 설정을 변경. 영어(en), 한글(kr)만 지원

weather
소스상에 설정된 지역의 날씨를 출력

cctv (on, off)
카메라를 동작시키고 JPG 스트리밍을 on/off. CCTV를 볼 수 있는 URL을 전달

pic
사진을 촬영해서 이미지 파일을 전송해줌. 기존에 cctv가 동작중인 경우 cctv 동작이 중단됨

dev
현재까지 감지되었던 장치들의 리스트를 보여줌. 동작이 중단된 장치가 있을 수 있음. 각 장치는 장치넘버를 가짐

dev desc (장치넘버)
해당하는 장치의 상세 정보를 보여줌. 각 장치가 처리할 수 있는 제어신호(control signal) 정보도 함께 출력.

dev del (장치넘버)
지정한 장치를 삭제. 장치가 보내준 센서 데이터도 모두 삭제됨

dev delall
등록된 장치들을 모두 삭제, 모든 센서 데이터도 삭제됨

sensor (장치넘버) [갯수]
지정한 장치가 보내준 센서 데이터를 [갯수] 만큼 출력. 최대 100개까지 출력. [갯수]가 생략된 경우 최신 데이터 1개만 출력

sensor del (장치넘버) [시간]
지정한 장치의 센서 데이터를 [시간] 단위로 삭제. 해당 장치의 지정한 시간 이전의 데이터는 모두 삭제됨. [시간] 항목을 생략하면 해당 장치의 센서 데이터 모두를 삭제

sensor delall [시간]
모든 센서 데이터를 [시간] 단위로 삭제. 지정한 시간 이전의 데이터는 모두 삭제됨. [시간] 항목을 생략하면 센서 데이터 모두를 삭제

graph (장치넘버) [갯수]
지정한 장치의 센서 데이터를 [갯수]만큼 추출해서 그래프로 그린 뒤 이미지 파일로 전송해줌. 최대 100개까지 출력. [갯수]가 생략된 경우 최신 데이터 10개를 사용.

send (장치넘버) (제어신호1) [제어신호2] ... [제어신호4]
지정한 장치로 제어신호를 전송. 제어신호1 은 필수이면 2, 3, 4는 생략가능. 반드시 제어신호는 순서대로 기재해야 함. 사용가능한 제어신호의 정수값은 "장치 상세 (장치넘버)" 명령으로 확인가능.

noti
사용자가 설정한 알림 설정을 모두 보여줌. 각각의 알림 설정은 알림 ID를 가짐.

noti add (장치넘버) (조건식1) [조건식2] ... [조건식4]
지정한 장치에서 조건식에 맞는 센서 데이터를 보낼 경우 메시지로 알려주도록 설정함. 조건식 한 개는 필수. 반드시 조건식은 data1, data2, data3, data4 로 센서 데이터를 구분해야 하며 공백없이 기재.
data1>=1 data2<=99 data3!=0 data4==1

noti del (알림ID)
지정한 알림ID 에 해당하는 설정을 삭제. 알림ID 대신 분류1, 분류2, 장치ID 를 사용할 경우 해당 장치의 알림 모두를 삭제. 알림 삭제시 연결된 매크로도 모두 삭제.

macro
현재 설정된 매크로를 모두 보여줌.

macro add (알림ID) (명령어)
특정 알림이 실행될 때 챗을 보내는대신 명령어를 실행.\n예) macro add 1 pic => 알림 1 조건에 맞는 센서값이 들어오면 사진 촬영 후 전송

macro del (매크로ID)
지정한 매크로 삭제
"""
        return msg
    else:
        msg = """hello
: Check if HomePy is available

ping (device_number)
: Check if specified device is active or not

lang (en, kr)
: Change language setting

weather
: Print current weather

cctv (on, off)
: Turn on cctv. Also sends streaming URL message.

pic
: Take a picture and sends image file. This command stops cctv if its running.

dev
: Show registered devices. Every device has its own device number

dev desc (device_number)
: Show details of specified device. Also prints (control signal) info.

dev del (device_number)
: Remove selected device. This command removes sensor data also.

dev delall
: Remove every device.

sensor (device_number) [count]
: Print sensor data from specified device. Max 100, shows most recent 1 if count is missing.

sensor del (device_number) [hour_unit]
: Remove device's sensor data which is older than [hour_unit]. If [hour_unit] is missing, delete all data of the device.

sensor delall [hour_unit]
: Remove all sensor data which is older than [hour_unit].

graph (device_number) [count]
: Draw graph with sensor data and send it as image file. Max 100, use 10 if count is missing.

send (device_number) (control1) [control2] ... [control4]
: Send control signal to specified device. Control1 value is mandatory and others are optional. Check available control value with "dev desc (device_number)" command.

noti
: Show every notification settings.

noti add (device_number) (comp_str1) [comp_str1] ... [comp_str1]
: Add a new notification setting. If HomePy receives sensor data which is matching with noti setting, HomePy alerts you with a message. Check comp_str format:
data1>=1 data2<=99 data3!=0 data4==1

noti del (noti_ID)
: Remove notification setting.

macro
Show every macro.

macro add (noti_ID) (command)
Add a macro.\nex) macro add 1 pic => Take a picture when HomePy enables noti 1.

macro del (macro_ID)
delete a macro.
"""
        return msg







