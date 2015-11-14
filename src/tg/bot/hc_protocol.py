#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time



############################################
# Global variables
############################################

proto_lang = 'en'

# Category 1 name list
cat1_map = {
1: "Basic sensor",
2: "Basic sensor",
3: "Complex sensor",
4: "Complex sensor",
5: "Input device",
6: "Input device",
7: "Actuator",
8: "Actuator",
9: "Controller",
10: "Controller",
11: "Home appliance",
12: "Home appliance"
}
cat1_map_kr = {
1: "기본센서",
2: "기본센서",
3: "복합센서",
4: "복합센서",
5: "입력장치",
6: "입력장치",
7: "출력장치",
8: "출력장치",
9: "모터 및 제어기",
10: "모터 및 제어기",
11: "생활가전",
12: "생활가전"
}

# Below map is for category 2
# Category 1 = 0x01 : basic sensor
basic_sensor_map = {
1: "Temp/Humi sensor",
2: "Temp/Humi sensor",
3: "Humidity sensor",
4: "Thermometer",
5: "vibration sensor",
6: "Tilt sensor",
7: "Illumination sensor",
8: "IR sensor",
9: "Magnetic reed sensor",
10: "Magnetic sensor",
11: "Magnetic hall sensor",
12: "Heart beat sensor",
13: "IR thermometer",
14: "Sound sensor",
15: "Laser sensor",
16: "Flame sensor",
17: "Touch sensor",
18: "Motion sensor",
19: "Ultrawave sensor",
20: "Gas sensor",
21: "Soil moisture sensor",
22: "Water level sensor",
23: "Voltage sensor",
24: "Current sensor",
25: "Color sensor",
26: "Flex sensor",
27: "Pressure sensor",
28: "EMG sensor",
29: "Dust sensor",
30: "Water velocity meter"
}
basic_sensor_map_kr = {
1: "온습도 센서",
2: "적외선 온도 센서",
3: "습도 센서",
4: "온도 센서",
5: "진동 센서",
6: "기울기 센서",
7: "조도 센서",
8: "적외선 센서",
9: "Magnetic reed 센서",
10: "Magnetic 센서",
11: "Magnetic hall 센서",
12: "심박 센서",
13: "체온계",
14: "사운드 센서",
15: "레이저 센서",
16: "flame 센서",
17: "Touch 센서",
18: "모션감지센서",
19: "초음파센서",
20: "가스센서",
21: "토양습도센서",
22: "수위센서",
23: "전압센서",
24: "전류센서",
25: "컬러센서",
26: "Flex 센서",
27: "압력센서",
28: "근전도센서",
29: "먼지센서",
30: "유속센서"
}

# Category 1 = 0x03 : advanced sensor
advanced_sensor_map = {
1: "Accelerometer",
2: "Gyro sensor",
3: "Compass magnetometer",
4: "Altitude sensor",
5: "GPS",
6: "Finger Print sensor",
7: "Barcode reader"
}
advanced_sensor_map_kr = {
1: "가속도센서",
2: "자이로센서",
3: "지자기센서",
4: "고도(기압) 센서",
5: "GPS",
6: "지문인식센서",
7: "바코드 리더"
}

# Category 1 = 0x05 : input device
input_device_map = {
1: "Push button",
2: "Switch",
3: "Potentiometer",
4: "Rotary encoder",
5: "Keypad",
6: "Keyboard",
7: "Mouse",
8: "Joystick",
9: "Motion controller",
10: "3D input pad",
11: "timer"
}
input_device_map_kr = {
1: "푸시 버튼",
2: "스위치",
3: "포텐셔미터",
4: "Rotary encoder",
5: "키패드",
6: "키보드",
7: "마우스",
8: "조이스틱",
9: "모션컨트롤러",
10: "3D 입력 패드",
11: "타이머"
}

# Category 1 = 0x07 : display, printer, motion device
output_device_map = {
1: "buzzer",
2: "LED (1 color)",
3: "LED (RGB)",
4: "IR LED",
5: "Laser",
6: "Pan-tilt mount",
7: "Smart film",
8: "Display",
9: "Speaker",
10: "Dot matrix",
11: "7 segment",
12: "Thermal printer",
13: "Robot arm",
14: "RC car",
15: "RC plane"
}
output_device_map_kr = {
1: "buzzer",
2: "LED (1 color)",
3: "LED (RGB)",
4: "적외선 LED",
5: "레이저",
6: "pan-tilt 관절",
7: "스마트 필름",
8: "디스플레이",
9: "스피커",
10: "도트 매트릭스",
11: "7 segment",
12: "열전사 프린터",
13: "로봇팔",
14: "RC 카",
15: "비행체"
}

# Category 1 = 0x09 : controller
controller_map = {
1: "DC motor",
2: "Servo motor",
3: "Stepper motor",
4: "Solenoid valve",
5: "Lock",
6: "MOSFET",
7: "Transistor",
8: "Relay"
}

controller_map_kr = {
1: "DC 모터",
2: "서보모터",
3: "스텝모터",
4: "솔레노이드 밸브",
5: "자물쇠",
6: "MOSFET",
7: "트랜지스터",
8: "릴레이" 
}

# Category 1 = 0x11 : electronics
electronics_map = {
1: "Light",
2: "Switch",
3: "Humidifier",
4: "Air purifier",
5: "RC toy",
6: "Camera",
7: "Drone",
8: "Remote controller",
9: "Radiator"
}
electronics_map_kr = {
1: "조명",
2: "스위치",
3: "가습기",
4: "공기청정기",
5: "RC 장난감",
6: "카메라",
7: "드론",
8: "리모컨",
9: "Radiator"
}

# Command name
command_map = {
0: "NA",
1: "Buzzer", 
2: "Volume", 
3: "Speaker", 
4: "Color(RED)", 
5: "Color(GREEN)", 
6: "Color(BLUE)", 
7: "Light level", 
8: "Button", 
9: "Switch", 
10: "Solenoid valve", 
11: "Power switch", 
12: "Power level", 
13: "DC motor(dir)", 
14: "DC motor(speed)", 
15: "Servo(angle)", 
16: "Stepper motor(dir)", 
17: "Stepper motor(step)", 
18: "Stepper(speed)", 
19: "Rolling(X axis)", 
20: "Pitching(Y axis)", 
21: "Yawing(Z axis)", 
22: "2D loc(X)", 
23: "2D loc(Y)", 
24: "3D loc(X)", 
25: "3D loc(Y)", 
26: "3D loc(Z)", 
27: "Motion code", 
28: "Geo loc(Latitude)", 
29: "Geo loc(Longitude)", 
30: "Compass dir", 
31: "Altitude", 
32: "Temperature", 
33: "Humidity", 
34: "Air quality", 
35: "Water level", 
36: "Speed", 
37: "Pressure", 
38: "Voltage", 
39: "Current", 
40: "Heart beat", 
41: "EMG", 
42: "7 segment", 
43: "Transparency", 
44: "Display code", 
45: "Print code", 
46: "Key code", 
47: "Motion code", 
48: "ID number"
}
command_map_kr = {
0: "NA",
1: "버저", 
2: "볼륨", 
3: "스피커(코드)", 
4: "색상(RED)", 
5: "색상(GREEN)", 
6: "색상(BLUE)", 
7: "일반 광출력", 
8: "버튼(on-off)", 
9: "스위치(on-off)", 
10: "솔레노이드 밸브", 
11: "전원 제어(on-off)", 
12: "전원 제어(단계별)", 
13: "DC 모터(방향)", 
14: "DC 모터(속도)", 
15: "서보모터(회전각)", 
16: "스텝모터(방향)", 
17: "스텝모터(회전 스텝)", 
18: "스텝모터(속도)", 
19: "기울기(X축)", 
20: "기울기(Y축)", 
21: "기울기(Z축)", 
22: "2차원 위치(X축)", 
23: "2차원 위치(Y축)", 
24: "3차원 위치(X축)", 
25: "3차원 위치(Y축)", 
26: "3차원 위치(Z축)", 
27: "3차원 위치(Grip)", 
28: "지리적위치(Latitude)", 
29: "지리적위치(Longitude)", 
30: "방위", 
31: "고도", 
32: "온도", 
33: "습도", 
34: "공기상태", 
35: "수위", 
36: "속도", 
37: "압력", 
38: "전압", 
39: "전류", 
40: "심박", 
41: "근전도", 
42: "7 segment(숫자)", 
43: "스마트 필름(투명도)", 
44: "디스플레이(코드)", 
45: "프린터(코드)", 
46: "키코드", 
47: "모션 코드", 
48: "인식 코드"
}

# Command type name
command_type_map = {
0: "NA",
1: "boolean", 
2: "7 segment int (0~9)", 
3: "90 angle unsigned int (0~90)", 
4: "90 angle signed int (-90~90)", 
5: "180 angle unsigned int (0~180)", 
6: "180 angle signed int (-180~180)", 
7: "360 angle unsigned int (0~360)", 
8: "signed int (-127~127)", 
9: "unsigned int (0~255)", 
10: "unsigned int 10 (0~1023)", 
11: "signed int 16 (0~65535)", 
12: "unsigned int 16 bit", 
13: "signed long 32 bit", 
14: "unsigned long 32 bit", 
15: "float 32 bit"
}

# Location name list
location_name_list = [
"Hall",  # 100 ~
"Bedroom",  # 110 ~
"Room 1",
"Room 2",
"Room 3",
"Room 4",
"Bathroom",
"Kitchen",
"Study room",  # 180 ~
"Door",  
"Balcony",# 200 ~
"Store room",
"Outdoor"   # 220 ~
]
location_name_list_kr = [
"거실",  # 100 ~
"침실",  # 110 ~
"방1",
"방2",
"방3",
"방4",
"욕실",
"주방",
"서재",  # 180 ~
"현관",  
"베란다",# 200 ~
"창고",
"야외"   # 220 ~
]



############################################
# Protocol utilities
############################################

def set_proto_lang(lang_code):
    global proto_lang
    proto_lang = lang_code

def get_cat1_name(cat1):
    if cat1 == 0:
        if proto_lang == 'kr':
            return '미지정'
        else:
            return 'undefined'
    if proto_lang == 'kr':
        return cat1_map_kr.get(cat1, '사용자정의')
    else:
        return cat1_map.get(cat1, 'User defined')

def get_device_name(cat1, cat2):
    if cat1 == 0:
        if proto_lang == 'kr':
            return '미지정'
        else:
            return 'Undefined'
    elif cat1 == 0x01 or cat1 == 0x02:
        if proto_lang == 'kr':
            return basic_sensor_map_kr.get(cat2, '사용자정의')
        else:
            return basic_sensor_map.get(cat2, 'User defined')
    elif cat1 == 0x03 or cat1 == 0x04:
        if proto_lang == 'kr':
            return advanced_sensor_map_kr.get(cat2, '사용자정의')
        else:
            return advanced_sensor_map.get(cat2, 'User defined')
    elif cat1 == 0x05 or cat1 == 0x06:
        if proto_lang == 'kr':
            return input_device_map_kr.get(cat2, '사용자정의')
        else:
            return input_device_map.get(cat2, 'User defined')
    elif cat1 == 0x07 or cat1 == 0x08:
        if proto_lang == 'kr':
            return output_device_map_kr.get(cat2, '사용자정의')
        else:
            return output_device_map.get(cat2, 'User defined')
    elif cat1 == 0x09 or cat1 == 0x10:
        if proto_lang == 'kr':
            return controller_map_kr.get(cat2, '사용자정의')
        else:
            return controller_map.get(cat2, 'User defined')
    elif cat1 == 0x11 or cat1 == 0x12:
        if proto_lang == 'kr':
            return electronics_map_kr.get(cat2, '사용자정의')
        else:
            return electronics_map.get(cat2, 'User defined')

    if proto_lang == 'kr':
        return '사용자정의'
    else:
        return 'User defined'

def get_cmd_name(code):
    if code == 0:
        if proto_lang == 'kr':
            return '사용불가'
        else:
            return 'Not available'
    if proto_lang == 'kr':
        return command_map_kr.get(code, '사용자정의')
    else:
        return command_map.get(code, 'User defined')

def get_cmd_type_name(code):
    if code == 0:
        if proto_lang == 'kr':
            return '미지정'
        else:
            return 'Undefined'
    if proto_lang == 'kr':
        return command_type_map.get(code, '사용자정의')
    else:
        return command_type_map.get(code, 'User defined')

def get_location_name(code):
    if code == 0:
        if proto_lang == 'kr':
            return '미지정'
        else:
            return 'Undefined'
    if code < 100:
        if proto_lang == 'kr':
            return '사용자정의'
        else:
            return 'User defined'
    elif code < 110:
        if proto_lang == 'kr':
            return '거실'
        else:
            return 'Hall/Living room'
    elif code < 120:
        if proto_lang == 'kr':
            return '침실'
        else:
            return 'Bedroom'
    elif code < 130:
        if proto_lang == 'kr':
            return '방1'
        else:
            return 'Room 1'
    elif code < 140:
        if proto_lang == 'kr':
            return '방2'
        else:
            return 'Room 2'
    elif code < 150:
        if proto_lang == 'kr':
            return '방3'
        else:
            return 'Room 3'
    elif code < 160:
        if proto_lang == 'kr':
            return '방4'
        else:
            return 'Room 4'
    elif code < 170:
        if proto_lang == 'kr':
            return '욕실'
        else:
            return 'Bathroom'
    elif code < 180:
        if proto_lang == 'kr':
            return '주방'
        else:
            return 'Kitchen'
    elif code < 190:
        if proto_lang == 'kr':
            return '서재'
        else:
            return 'Study room'
    elif code < 200:
        if proto_lang == 'kr':
            return '현관'
        else:
            return 'Door'
    elif code < 210:
        if proto_lang == 'kr':
            return '베란다'
        else:
            return 'Balcony'
    elif code < 220:
        if proto_lang == 'kr':
            return '창고'
        else:
            return 'Store room'
    elif code < 230:
        if proto_lang == 'kr':
            return '옥외'
        else:
            return 'Outdoor'

