import serial
import json
import asyncio
import time
import config

class ArduinoService:
    def __init__(self):
        self.port = config.ARDUINO_PORT
        self.baudrate = config.ARDUINO_BAUDRATE
        self.ser = None
        self.running = False
        self.sensor_data = {"ldr": 0, "b1": 0, "b2": 0, "b3": 0}

    def connect(self):
        print(f"Connecting to {self.port}...")
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(3)
            self.ser.reset_input_buffer()
            self.running = True
            print("Serial connected")
            return True
        except Exception as e:
            print(f"Serial connection error: {e}")
            self.ser = None
            return False

    def close(self):
        self.running = False
        if self.ser:
            self.ser.close()
            print("Serial disconnected")

    def send_command(self, device: str, value: str):
        if self.ser and self.ser.is_open:
            cmd = f"{device}:{value}\n"
            try:
                self.ser.write(cmd.encode())
            except Exception as e:
                print(f"Serial write error: {e}")

    async def read_loop(self):
        print("Starting serial read loop")
        while self.running and self.ser:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    try:
                        data = json.loads(line)
                        self.sensor_data.update(data)
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"Serial read error: {e}")
                break
            
            await asyncio.sleep(0.01)