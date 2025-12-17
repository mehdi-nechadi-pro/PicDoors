# Secure Face Access Gate

IoT access control system based on facial recognition. This project orchestrates communication between a computing server (PC), a video capture device (Smartphone), and a physical actuator (Arduino) to manage secure door opening.

## Technical Architecture

The project is structured in a modular way:
* **Core (Python)**: Computer vision logic using OpenCV and DeepFace (ArcFace).
* **Web Interface (Flask)**: Dashboard for visualization and video stream control.
* **Hardware**: Serial communication management with the Arduino microcontroller.

## Prerequisites

* **Hardware**: PC (Server), Smartphone (IP Video Source), Arduino (Door Controller).
* **Software**: Python 3.10+, Git, "IP Webcam" application or equivalent on the smartphone.

## Installation

1. Clone the repository
   `git clone https://github.com/your-user/secure-gate.git`


2. Install dependencies 
   `pip install -r requirements.txt`

## Configuration

Modify the `config.py` file according to your local environment:

* `CAMERA_IP`: Local IP address of the smartphone streaming the video.
* `ARDUINO_PORT`: Arduino serial port (e.g., COM3 or /dev/ttyUSB0).
* `CHECK_INTERVAL`: Time interval between two biometric analyses (in seconds).

## Usage

1. Start the video server on the smartphone.
2. Connect the Arduino to the PC USB port.
3. Launch the application:
   python run.py
4. Access the interface via a browser: http://localhost:5000

## Authors

* **Mehdi**: Backend Python & AI
* **Enzo**: Web Backend & Flask
* **Nael**: Hardware & Arduino
* **Joubrane**: Web Frontend
* **Amir**: Network & Video Capture