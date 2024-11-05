import asyncio
import websockets
import RPi.GPIO as GPIO
import time

# Setup GPIO for ultrasonic sensor
TRIG_PIN = 14
ECHO_PIN = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    speed_of_sound = 34300  # Speed of sound in cm/s
    distance = (pulse_duration * speed_of_sound) / 2

    return distance

async def send_distance_value():
    uri = "ws://172.20.10.4:8765"  # Replace with the IP address of your server
    async with websockets.connect(uri) as websocket:
        while True:
            distance = get_distance()
            await websocket.send(str(distance))
            print(f"Sent distance: {distance} cm")
            await asyncio.sleep(1)  # Adjust the frequency as needed

if __name__ == "__main__":
    try:
        asyncio.run(send_distance_value())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
