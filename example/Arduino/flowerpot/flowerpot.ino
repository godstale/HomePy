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


#define HUMI_PIN A0
#define CONTROL_PIN 5
#define LED_PIN 13

// Humidity check
unsigned long prevReadTime = 0;

// Water pump control
#define CHECK_INTERVAL 300000
#define AUTO_STOP_INTERVAL 1500
#define HUMIDITY_THRESHOLD 250
int isValveOn = 0;
unsigned long prevValveTime = 0;


void setup() {
  // for debug
  Serial.begin(9600);
  Serial.println("Smart flowerpot");

  // initialization
  pinMode(CONTROL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(CONTROL_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
}



void loop() {
  // turn off the water pump
  if(isValveOn > 0 && millis() - prevValveTime > AUTO_STOP_INTERVAL) {
    digitalWrite(CONTROL_PIN, LOW);
    isValveOn = 0;
    Serial.println("Stop pumping...");
  }
  
  //------------------------------------------------------
  //----- Check humidity info
  //------------------------------------------------------
  if(millis() - prevReadTime > CHECK_INTERVAL) {
    int humi = analogRead(HUMI_PIN);
    prevReadTime = millis();
    Serial.print("Humidity: ");
    Serial.print(humi);
    Serial.println(" %");

    // send data to server
    if(humi < HUMIDITY_THRESHOLD) {
      digitalWrite(CONTROL_PIN, HIGH);
      prevValveTime = millis();
      isValveOn = 1;
      Serial.println("Start pumping...");
    }
  }

}  // End of loop()

