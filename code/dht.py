import network
import time
import urequests
from machine import Pin
import dht

WIFI_SSID = "Binus-Access"
WIFI_PASSWORD = ""

# IP Address tergantung dengan Default Gateway Wifi
FLASK_URL = "http://10.34.129.188:5000/sensor_data"

dht_pin = dht.DHT11(Pin(21))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 60
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(f"Connecting to WiFi... {timeout} seconds remaining.")
        
    if wlan.isconnected():
        print("Connected to WiFi")
        print("IP Address:", wlan.ifconfig()[0])
        return True
    else:
        print("Failed to connect to WiFi")
        return False

def is_wifi_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def send_data(temp, hum, dist):
    try:
        print("Attempting to send data to:", FLASK_URL)
        headers = {"Content-Type": "application/json"}
        payload = {
            "temperature": temp,
            "humidity": hum,
            "motion": dist
        }
        print("Payload:", payload)
        response = urequests.post(FLASK_URL, json=payload, timeout=10)

        print("Response status code:", response.status_code)
        if response.status_code == 201:
            print("✅ Data sent successfully:", response.text)
        else:
            print("❌ Failed to send data. Response:", response.text)

        response.close()
    except Exception as e:
        print("Error sending data:", e)

if connect_wifi():  
    while True:
        try:
            # karena port vcc/3v3 di esp32 hanya ada 1 sehingga kami menguji 2 sensor secara terpisah
            dht_pin.measure()
            temperature = dht_pin.temperature()
            humidity = dht_pin.humidity()
            distance = 0

            print(f"🌡 Temperature: {temperature}°C, 💧 Humidity: {humidity}%")

            if is_wifi_connected():
                send_data(temperature, humidity, 0)
            else:
                print("WiFi not connected. Reconnecting...")
                connect_wifi()

            time.sleep(5)
        except Exception as e:
            print("❗ Error:", e)
            time.sleep(2)