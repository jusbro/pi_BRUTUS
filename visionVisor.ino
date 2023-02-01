#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

int sensorPin = A0;
int frontSensorValue = 0;

int leftSensorTrigPin = 9;
int leftSensorEchoPin = 10;

int rightSensorTrigPin = 6;
int rightSensorEchoPin = 5;

long duration;

int leftSensorValue;
int rightSensorValue;

float frontDistMapped;

void setup() {
  pinMode(leftSensorTrigPin, OUTPUT);
  pinMode(leftSensorEchoPin, INPUT);

  pinMode(rightSensorTrigPin, OUTPUT);
  pinMode(rightSensorEchoPin, INPUT);

  Serial.begin(9600);

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

  // Draw a single pixel in white
  display.drawPixel(10, 10, SSD1306_WHITE);

  // Show the display buffer on the screen. You MUST call display() after
  // drawing commands to make them visible on screen!
  display.display();
  delay(2000);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

}

void loop() {
  // read the value from the sensor:
  frontSensorValue = analogRead(sensorPin);
  frontDistMapped = map(frontSensorValue, 550, 0, 0, 100);

  digitalWrite(leftSensorTrigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(leftSensorTrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(leftSensorTrigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(leftSensorEchoPin, HIGH);
  // Calculating the distance
  leftSensorValue = duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(leftSensorValue);

  digitalWrite(rightSensorTrigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(rightSensorTrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(rightSensorTrigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(rightSensorEchoPin, HIGH);
  // Calculating the distance
  rightSensorValue = duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(rightSensorValue);

  // turn the ledPin on
  //Serial.println(sensorValue);
  Serial.println(frontDistMapped);
  display.setCursor(0, 0);
  display.print("Front: ");
  display.println(frontDistMapped);
  display.print("Left: ");
  display.println(leftSensorValue);
  display.print("Right: ");
  display.println(rightSensorValue);
  display.display();
  delay(100);
  display.clearDisplay();
}
