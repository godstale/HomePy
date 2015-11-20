//////////////////////////////////////////////////////////
// Example testing HomePy device
// Written by YoungBae Suh

// 1. Sends registration code to server at start-up and in every 30 min
// 2. Sends humidity of soil to server every 5 min
// 3. Responds at ping command from remote.
// 4. When it receives control command from server, feed water to flowerpot
//    And send response with result code
// Find details at http://www.hardcopyworld.com
//////////////////////////////////////////////////////////

#include <SoftwareSerial.h>

#define HUMI_PIN A0
#define CONTROL_PIN 5
#define LED_PIN 13

// Defind software serial
SoftwareSerial hc11(2, 3);    // write HC-11's TX, RX

// Communication (adjust as you need)
#define REGISTRATION_INTERVAL 1800000
#define SENDING_INTERVAL 600000
unsigned long prevValveTime = 0;
unsigned long prevReadTime = 0;
unsigned long prevRegistrationTime = 0;

// Outgoing commands (to remote server, do not change this!!)
#define CMD_PING_RESPONSE 0x01
#define CMD_REGISTER_DEVICE 0x11
#define CMD_UPDATE_SENSOR_VAL 0x51
#define CMD_CONTROL_RESPONSE 0x81

// Incoming commands (from remote server, do not change this!!)
#define CMD_NONE 0x00
#define CMD_PING 0x01
#define CMD_REGISTRATION_RESULT 0x11
#define CMD_REQUEST_SENSOR_VAL 0x51
#define CMD_CONTROL_SIGNAL 0x81

// Parsing
const char SEND_START1 = 0x55;    // start byte 1 : fixed
const char SEND_START2 = 0xfe;    // start byte 2 : fixed
const char SEND_CAT1 = 0x01;      // category 1 : adjust as you need
const char SEND_CAT2 = 0x15;      // category 2 : adjust as you need
const char SEND_ID = 0x64;       // ID : adjust as you need (0x8c means: room3)
const char SEND_END1 = 0xFF;      // end byte 1 : fixed

const char CHECK_START1 = 0x78;    // start byte 1
const char CHECK_START2 = 0xfe;    // start byte 2
const char CHECK_CAT1 = SEND_CAT1; // category 1
const char CHECK_CAT2 = SEND_CAT2; // category 2
const char CHECK_ID = SEND_ID;     // ID
const char CHECK_END1 = 0xFF;      // end byte 1

// Define control signal 1 type : general light emitting device
// Refer to the HomePy protocol document
#define CONTROL1_TYPE 0x0a
// Define control signal 1 data type : boolean (0: off, 1: on)
// Refer to the HomePy protocol document
#define CONTROL1_DATA_TYPE 0x01

// Received packet buffer (fixed size, do not touch this!!)
#define BUFFER_SIZE 15
static char Buffer[BUFFER_SIZE] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};

// Water pump control
#define AUTO_STOP_INTERVAL 1500
int isValveOn = 0;



void setup() {
  // for debug
  Serial.begin(9600);
  Serial.println("HomePy flowerpot and LED control test !!");

  // initialization
  hc11.begin(9600);
  pinMode(CONTROL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Send device registration command to server 3 times
  sendRegistration();
  Serial.println("Send registration request...");
}



void loop() {
  // turn off the water pump
  if(isValveOn > 0 && millis() - prevValveTime > AUTO_STOP_INTERVAL) {
    digitalWrite(CONTROL_PIN, LOW);
    isValveOn = 0;
    Serial.println("Stop pumping...");
  }
  //------------------------------------------------------
  //----- Send registration request
  //------------------------------------------------------
  if(millis() - prevRegistrationTime > REGISTRATION_INTERVAL) {
    sendRegistration();
    prevRegistrationTime = millis();
    Serial.print("Send registration request");
    delay(100);
  }
  
  //------------------------------------------------------
  //----- Send temperature and humidity info to remote
  //------------------------------------------------------
  if(millis() - prevReadTime > SENDING_INTERVAL) {
    int humi = analogRead(HUMI_PIN);

    // send data to server
    sendSensorValue(humi, 0, 0, 0);
    prevReadTime = millis();
    Serial.print("Humidity: ");
    Serial.print(humi);
    Serial.println(" %");
  }
  
  //--------------------------------------------
  //----- Parsed received packet
  //--------------------------------------------
  int command = CMD_NONE;
  
  if (hc11.available()>0)  {
    // Get incoming byte
    char in_byte = 0;
    in_byte = hc11.read();
    command = parseCommand(in_byte);
  }  // End of if (hcSerial.available()>0)

  //--------------------------------------------
  // Process commands
  //--------------------------------------------
  if(command > CMD_NONE) {
    processCommand(command);
  }

}  // End of loop()



//--------------------------------------------
// Utilities
//--------------------------------------------
int value1 = 0;
int value2 = 0;
int value3 = 0;
int value4 = 0;
int parseCommand(char in_byte) {
  int cmd = CMD_NONE;
  Serial.print(in_byte);
  // Add received byte to buffer
  for(int i=0; i<BUFFER_SIZE-1; i++) {
    Buffer[i] = Buffer[i+1];
  }
  Buffer[BUFFER_SIZE-1] = in_byte;

  // Check condition
  if(Buffer[0] == CHECK_START1 && Buffer[1] == CHECK_START2) {
    if(Buffer[2] == CHECK_CAT1
        && Buffer[3] == CHECK_CAT2
        && Buffer[4] == CHECK_ID) {  // Check category 1, 2 and ID
      // Found command
      Serial.print("Parse command : ");
      
      if(Buffer[14] == CHECK_END1) {   // Check validity
        cmd = int(byte(Buffer[5]));    // to avoid negative value, convert into byte and int again
        value1 = (Buffer[6] << 8) | Buffer[7];
        value2 = (Buffer[8] << 8) | Buffer[9];
        value3 = (Buffer[10] << 8) | Buffer[11];
        value4 = (Buffer[12] << 8) | Buffer[13];
      }
      Serial.println(cmd);
      Serial.println("completed.");
    }
  }  // End of Check condition
  
  return cmd;
}


void processCommand(int cmd) {
  switch(cmd) {
  // Ping command
  case CMD_PING:
    Serial.println("Received ping request.");
    sendPingResponse();
    delay(100);
    break;
  // Device registration result
  case CMD_REGISTRATION_RESULT:
    Serial.println("Received registration request.");
    // Do what you want
    //if(value1 != 0) {}
    break;
  // Received update request
  case CMD_REQUEST_SENSOR_VAL:
    Serial.println("Received sensor update request.");
    // Reserve update right now
    prevReadTime = 0;
    break;
  // Control signal received
  case CMD_CONTROL_SIGNAL:
    Serial.print("Received control signal = ");
    Serial.println(value1);
    if(value1 == 1) {
      digitalWrite(CONTROL_PIN, HIGH);
      prevValveTime = millis();
      isValveOn = 1;
    } else if(value1 == 0) {
      digitalWrite(CONTROL_PIN, LOW);
      isValveOn = 0;
    }
    sendControlAccepted(value1, 0, 0, 0);
    break;
  default:
    break;
  }
  
  //Serial.print("Process command = ");
  //Serial.println(cmd);
}

void sendRegistration() {
  hc11.write(SEND_START1);    // Start byte 1
  hc11.write(SEND_START2);    // Start byte 2
  hc11.write(SEND_CAT1);      // Category 1
  hc11.write(SEND_CAT2);      // Category 2
  hc11.write(SEND_ID);       // ID
  hc11.write(CMD_REGISTER_DEVICE);  // Command
  hc11.write((byte)CONTROL1_TYPE);        // control signal 1 type
  hc11.write((byte)CONTROL1_DATA_TYPE);   // control signal 1 data type
  hc11.write((byte)0x00);    // control signal 2 type - NA
  hc11.write((byte)0x00);    // control signal 2 data type - NA
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);    // control signal 4 type - NA
  hc11.write((byte)0x00);    // control signal 4 data type - NA
  hc11.write(SEND_END1);
}

void sendSensorValue(int value1, int value2, int value3, int value4) {
  hc11.write(SEND_START1);    // Start byte 1
  hc11.write(SEND_START2);    // Start byte 2
  hc11.write(SEND_CAT1);      // Category 1
  hc11.write(SEND_CAT2);      // Category 2
  hc11.write(SEND_ID);       // ID
  hc11.write(CMD_UPDATE_SENSOR_VAL);  // Command
  hc11.write((byte)(value1 >> 8));
  hc11.write((byte)value1);
  hc11.write((byte)(value2 >> 8));
  hc11.write((byte)value2);
  hc11.write((byte)(value3 >> 8));
  hc11.write((byte)value3);
  hc11.write((byte)(value4 >> 8));
  hc11.write((byte)value4);
  hc11.write(SEND_END1);
}

void sendPingResponse() {
  hc11.write(SEND_START1);    // Start byte 1
  hc11.write(SEND_START2);    // Start byte 2
  hc11.write(SEND_CAT1);      // Category 1
  hc11.write(SEND_CAT2);      // Category 2
  hc11.write(SEND_ID);       // ID
  hc11.write(CMD_PING_RESPONSE);  // Command
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write((byte)0x00);
  hc11.write(SEND_END1);
}

void sendControlAccepted(int value1, int value2, int value3, int value4) {
  hc11.write(SEND_START1);    // Start byte 1
  hc11.write(SEND_START2);    // Start byte 2
  hc11.write(SEND_CAT1);      // Category 1
  hc11.write(SEND_CAT2);      // Category 2
  hc11.write(SEND_ID);       // ID
  hc11.write(CMD_CONTROL_RESPONSE);  // Command
  hc11.write((byte)(value1 >> 8));
  hc11.write((byte)value1);
  hc11.write((byte)(value2 >> 8));
  hc11.write((byte)value2);
  hc11.write((byte)(value3 >> 8));
  hc11.write((byte)value3);
  hc11.write((byte)(value4 >> 8));
  hc11.write((byte)value4);
  hc11.write(SEND_END1);
}

