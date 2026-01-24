#include <LiquidCrystal.h>
#include <Servo.h>

// --- Configuration LCD & Servo ---
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
Servo moteur;

#define BTN1 6
#define BTN2 7
#define BTN3 8
#define LDR_PIN A0
#define SERVO_PIN 9

#define LCD_CONTRAST_PIN 13

unsigned long lastSensorTime = 0;

void setup() {
  Serial.begin(9600); // Vitesse de com

  pinMode(LCD_CONTRAST_PIN, OUTPUT);
  digitalWrite(LCD_CONTRAST_PIN, LOW);
  
  lcd.begin(16, 2);
  lcd.print("Ready via API");
  
  moteur.attach(SERVO_PIN);
  moteur.write(90);

  pinMode(BTN1, INPUT_PULLUP);
  pinMode(BTN2, INPUT_PULLUP);
  pinMode(BTN3, INPUT_PULLUP);
}

void loop() {
  // 1. ÉCOUTER PYTHON (Commandes reçues)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Protocole : "LCD:Message"
    if (command.startsWith("LCD:")) {
      String msg = command.substring(4);
      lcd.clear();
      lcd.print(msg);
    }
    // Protocole : "SERVO:Angle"
    else if (command.startsWith("SERVO:")) {
      int angle = command.substring(6).toInt();
      moteur.write(angle);
    }
  }

  // 2. ENVOYER VERS PYTHON (Capteurs)
  // On envoie l'état des boutons seulement s'ils changent ou sont appuyés
  // Pour simplifier, on envoie tout toutes les 100ms
  if (millis() - lastSensorTime > 100) {
    int ldr = analogRead(LDR_PIN);
    
    // On inverse la logique PULLUP pour que 1 = Appuyé (plus simple pour Python)
    int b1 = !digitalRead(BTN1); 
    int b2 = !digitalRead(BTN2);
    int b3 = !digitalRead(BTN3);

    // Format JSON pour faciliter la vie de Python
    Serial.print("{\"ldr\":");
    Serial.print(ldr);
    Serial.print(", \"b1\":");
    Serial.print(b1);
    Serial.print(", \"b2\":");
    Serial.print(b2);
    Serial.print(", \"b3\":");
    Serial.print(b3);
    Serial.println("}");

    lastSensorTime = millis();
  }
}