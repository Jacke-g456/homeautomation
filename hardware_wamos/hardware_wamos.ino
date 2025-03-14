
#include <SoftwareSerial.h>
// IMPORT ALL REQUIRED LIBRARIES
#include <NewPing.h>
#include <ArduinoJson.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef ARDUINO_H
#include <Arduino.h>
#endif 

#include <math.h>
   
//**********ENTER IP ADDRESS OF SERVER******************//

#define HOST_IP     "172.20.10.2"       // REPLACE WITH IP ADDRESS OF SERVER ( IP ADDRESS OF COMPUTER THE BACKEND IS RUNNING ON) 
#define HOST_PORT   "8080"            // REPLACE WITH SERVER PORT (BACKEND FLASK API PORT)
#define route       "api/update"      // LEAVE UNCHANGED 
#define idNumber    "620165845"       // REPLACE WITH YOUR ID NUMBER 

// WIFI CREDENTIALS
#define SSID        "MonaConnect"      // "REPLACE WITH YOUR WIFI's SSID"   
#define password    ""  // "REPLACE WITH YOUR WiFi's PASSWORD" 

#define stay        100
 
//**********PIN DEFINITIONS******************//

 
#define espRX         11
#define espTX         10
#define espTimeout_ms 300

 
 
/* Declare your functions below */

#define Trigger 6
#define Echo 7
#define sensor_height 94.5
#define max_height 77.763
#define difference 16.737
#define radius 30.75



void espInit();
void espSend(char command[] );
void espUpdate(char mssg[]);
double calcReserve(double height);

 

SoftwareSerial esp(espRX, espTX); 
NewPing sonar(Trigger, Echo, max_height); // Create an instance of NewPing called sonar

void setup(){

  Serial.begin(115200); 
  // Configure GPIO pins here
 

 

  espInit();  
 
}

void loop(){ 
   
  // send updates with schema ‘{"id": "student_id", "type": "ultrasonic", "radar": 0, "waterheight": 0, "reserve": 0, "percentage": 0}’
  double radar =  sonar.ping_in()-16.737; // 
  double water_height =  max_height - radar;
  double reserve = calcReserve(water_height);
  double percent = (water_height/max_height)*100;
  
  StaticJsonDocument<1000> doc;
  char mssg[200]={0};

  doc["id"] = "620165845";
  doc["type"] = "ultrasonic";
  doc["radar"] = radar;
  doc["waterheight"] = water_height;
  doc["reserve"] = reserve;
  doc["percentage"] = percent;

   serializeJson(doc, mssg);
   espUpdate(mssg);


  delay(1000);  
}

 
void espSend(char command[] ){   
    esp.print(command); // send the read character to the esp    
    while(esp.available()){ Serial.println(esp.readString());}    
}


void espUpdate(char mssg[]){ 
    char espCommandString[50] = {0};
    char post[500]            = {0};

    snprintf(espCommandString, sizeof(espCommandString),"AT+CIPSTART=\"TCP\",\"%s\",%s\r\n",HOST_IP,HOST_PORT); 
    espSend(espCommandString);    //starts the connection to the server
    delay(stay);

    // GET REQUEST 
    // snprintf(post,sizeof(post),"GET /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n",route,HOST_IP,strlen(mssg),mssg);

    // POST REQUEST
    snprintf(post,sizeof(post),"POST /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n",route,HOST_IP,strlen(mssg),mssg);
  
    snprintf(espCommandString, sizeof(espCommandString),"AT+CIPSEND=%d\r\n", strlen(post));
    espSend(espCommandString);    //sends post length
    delay(stay);
    Serial.println(post);
    espSend(post);                //sends POST request with the parameters 
    delay(stay);
    espSend("AT+CIPCLOSE\r\n");   //closes server connection
   }

void espInit(){
    char connection[100] = {0};
    esp.begin(115200); 
    Serial.println("Initiallizing");
    esp.println("AT"); 
    delay(1000);

    
    esp.println("AT+CWMODE=1");
    delay(1000);
    while(esp.available()){ Serial.println(esp.readString());} 

    snprintf(connection, sizeof(connection),"AT+CWJAP=\"%s\",\"%s\"\r\n",SSID,password);
    delay(5000);
if(esp.available()) {
    Serial.println(esp.readString());
}

    esp.print(connection);

    delay(3000);  //gives ESP some time to get IP

    if(esp.available()){   Serial.print(esp.readString());}
    
    Serial.println("\nFinish Initializing");    
   
}



//***** Design and implement all util functions below ******
 
 double calcReserve(double height){
  return (M_PI * pow(radius,2) * height) / 231.0;
 }

