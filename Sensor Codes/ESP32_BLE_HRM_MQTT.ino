//  LIBRARIES
//BLE
#include "BLEDevice.h"
//#include "BLEScan.h"

//WIFI
#include <WiFi.h>

//MQTT
#include <PubSubClient.h>

//  VARIABLES
//BLE
static BLEAddress bleAddr("C5:72:1D:F1:5B:52");                         //CooSpo H6 (AFoF)
//static BLEAddress bleAddr("C5:36:EF:AF:E5:AE");                       //CooSpo H6 (KMV)
//static BLEAddress bleAddr("EB:86:46:F8:6F:1A");                       //Amazfit Bip (KMV)
static BLEUUID serviceUUID("0000180d-0000-1000-8000-00805f9b34fb");   //Service UUID
static BLEUUID    charUUID("00002a37-0000-1000-8000-00805f9b34fb");   //Characteristic UUID

static boolean doConnect = false;
static boolean connected = false;
static boolean doScan = false;
static BLERemoteCharacteristic* pRemoteCharacteristic;
static BLEAdvertisedDevice* myDevice;
boolean notification = false;
// bool ipmessageSent = false;

//WIFI
int recon_attempt = 0;
bool isDisconnect = true;

//MQTT
const char* ssid = "AFOF24";
const char* password = "AFoF2020";
const char* mqtt_server = "192.168.1.105";    //Connecting to a Raspberry Pi
IPAddress local_IP(192, 168, 1, 184); // set the static ip of esp32
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
WiFiClient espClient;
PubSubClient client(espClient);
long time_lastMsg = 0;

//  METHODS
//BLE
static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify) {
    //Serial.print("Notify callback for characteristic ");
    //Serial.print(pBLERemoteCharacteristic->getUUID().toString().c_str());
    //Serial.print(" of data length ");
    //Serial.println(length);
    //Serial.print("data: ");
    //Serial.write(pData, length);
    //printf("Value:  %d\n", *(pData) );
    //Serial.println(String(pData[1]));

    mqttSendMsg("mqtt/sensor/hrm", (String)pData[1]);
}

class MyClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
  }

  void onDisconnect(BLEClient* pclient) {
    connected = false;
    Serial.println("onDisconnect");
    Serial.println("BLE device disconnected");
    mqttSendMsg("mqtt/sensor/status", "disconnected");
  }
};

bool connectToBLEDevice() {
    Serial.print("Forming a connection to ");
    Serial.println(myDevice->getAddress().toString().c_str());
    
    BLEClient*  pClient  = BLEDevice::createClient();
    Serial.println(" - Created client");

    pClient->setClientCallbacks(new MyClientCallback());

    // Connect to the remove BLE Server.
    pClient->connect(myDevice);  // if you pass BLEAdvertisedDevice instead of address, it will be recognized type of peer device address (public or private)
    Serial.println(" - Connected to server");

    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      Serial.print("Failed to find our service UUID: ");
      Serial.println(serviceUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our service");


    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
      Serial.print("Failed to find our characteristic UUID: ");
      Serial.println(charUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our characteristic");

    // Read the value of the characteristic.
    if(pRemoteCharacteristic->canRead()) {
      std::string value = pRemoteCharacteristic->readValue();
      Serial.print("The characteristic value was: ");
      Serial.println(value.c_str());
    }

    if(pRemoteCharacteristic->canNotify())
      pRemoteCharacteristic->registerForNotify(notifyCallback);

    connected = true;
}

//Scan for BLE servers and find the first one that advertises the service we are looking for.
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
 //Called for each advertising BLE server.
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.print("BLE Advertised Device found: ");
    Serial.println(advertisedDevice.toString().c_str());

    // We have found a device, let us now see if it contains the service we are looking for.
    if (advertisedDevice.getAddress().equals(bleAddr)) {
      Serial.println("I found our device");

      BLEDevice::getScan()->stop();
      myDevice = new BLEAdvertisedDevice(advertisedDevice);
      doConnect = true;
      doScan = true;
    }
  }
};


//WIFI
//ESP connect to WiFi
void setup_wifi() 
{
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  } 
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");\
  Serial.println(WiFi.localIP());
}

//Stop Wi-Fi connection
void stop_wifi()
{
  Serial.println("Stopping WiFi");
  WiFi.disconnect();
  WiFi.softAPdisconnect(true);
}

// This code initiates full cycle of reconnection process. It includes disconnecting/connecting to/from Wi-Fi as well as reconnecting to MQTT broker
void initReconnect()
{
  stop_wifi();
  setup_wifi();
  reconnect();
}


//MQTT
//ESP - connects and subscribes to mqtt topic
bool reconnect() 
{
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "SEMS_ESP_1";
    if (client.connect(clientId.c_str(), "Afof2023", "Afof2023")) {
      Serial.println("connected");
      Serial.println("Subscribing to topic: mqtt/sensor/hrm");
      client.subscribe("mqtt/sensor/hrm");
      //client.subscribe("homeassistant/smartlight/brightness/command");
      //mqttSendMsg("mqtt/sensor/hrm","online");
      
      return true;
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
      return false;
    }
  }
}

//ESP - called once received mqtt message to subscribed topic
void callback(char* topic, byte* payload, unsigned int length) 
{
  String stringPayload = "";
   for (int i=0;i<length;i++) {
      stringPayload += (char)payload[i];
    }
    
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]:");
  Serial.println(stringPayload);
}

bool mqttSendMsg(String topic, String msg)
{
  Serial.println("mqttSendMsg initiated. Sending MQTT message");
  if (client.publish(topic.c_str(), msg.c_str(), true))
    {
      Serial.print("Publish message: ");
      Serial.println(msg);
      return true;
    } else {
      Serial.println("error sending");
      return false;
    }
}

void setup() {
  Serial.begin(115200);

  //Establishing WiFi connection
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  initReconnect();
  
  Serial.println("Starting Arduino BLE Client application...");
  BLEDevice::init("");

  // Retrieve a Scanner and set the callback we want to use to be informed when we
  // have detected a new device.  Specify that we want active scanning and start the
  // scan to run for 5 seconds.
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setInterval(1349);
  pBLEScan->setWindow(449);
  pBLEScan->setActiveScan(true);
  pBLEScan->start(5, false);
}



// This is the Arduino main loop function.
void loop() {
  // If the flag "doConnect" is true then we have scanned for and found the desired
  // BLE Server with which we wish to connect.  Now we connect to it.  Once we are 
  // connected we set the connected flag to be true.
  //  if (!ipmessageSent) {
  //   // send the message
  //   client.subscribe("esp32/connectivity/status");
  //   String localIP = String(WiFi.localIP()[0]) + "." + String(WiFi.localIP()[1]) + "." + String(WiFi.localIP()[2]) + "." + String(WiFi.localIP()[3]);
  //   mqttSendMsg("esp32/connectivity/status", localIP);
  //   ipmessageSent = true; 
  // }
  if (doConnect == true) {
    if (connectToBLEDevice()) {
      Serial.println("We are now connected to the BLE Device.");
      client.subscribe("mqtt/sensor/status");
      mqttSendMsg("mqtt/sensor/status","connected");
    } else {
      Serial.println("We have failed to connect to the server; there is nothin more we will do.");
    }
    doConnect = false;

  }
  // Check if BLE device is connected
  if (connected && !client.connected()) {
    Serial.println("BLE device disconnected");
    mqttSendMsg("mqtt/sensor/status", "disconnected");
  }

  // Turn notification on
  if (connected) {
    if (notification == false) {
      Serial.println(F("Turning Notification On"));
      const uint8_t onPacket[] = {0x1, 0x0};
      pRemoteCharacteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue((uint8_t*)onPacket, 2, true);
      notification = true;
    }
    
  }
  
  delay(1000); // Delay a second between loops.
} // End of loop
