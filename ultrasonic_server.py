import asyncio
import websockets
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# GPIO setup for the LED
LED_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 1)  # Set PWM frequency to 1Hz for blinking
pwm.start(0)  # Start PWM with 0% duty cycle

# MQTT setup
MQTT_BROKER = "mqtt-dashboard.com"  # Replace with your broker IP if needed
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/distance"

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

connected_clients = set()

async def handle_connection(websocket, path):
    global connected_clients
    connected_clients.add(websocket)
    print("Client connected")

    try:
        async for message in websocket:
            print(f"Received message: {message}")

            distance = float(message)
            if distance < 10:
                pwm.ChangeDutyCycle(50)  # Set LED to blink (50% duty cycle)
                print("LED is blinking")
            else:
                pwm.ChangeDutyCycle(0)  # Stop blinking
                print("LED stopped blinking")

            # Publish the received distance to MQTT broker
            mqtt_client.publish(MQTT_TOPIC, message)

            # Broadcast the numeric distance to all connected clients
            if connected_clients:
                await asyncio.gather(
                    *[client.send(message) for client in connected_clients if client != websocket]
                )

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pwm.stop()
        GPIO.cleanup()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
