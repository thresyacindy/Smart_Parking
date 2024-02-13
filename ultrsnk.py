#Kelompok 24
# 13321007 - Albert Panggabean
# 13321045 - Cindy Thresya Situmeang

import time
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

broker = '192.168.43.44'  # Ganti dengan alamat IP broker MQTT Anda
port = 1883
topic_publish = "sensor/"
client_id = 'python-mqtt'
username = 'test'
password = 'test'

GPIO.setmode(GPIO.BCM)
TRIG = 17  # Pin trigger sensor ultrasonik
ECHO = 27  # Pin echo sensor ultrasonik
BUZZER = 22  # Pin buzzer

# Konfigurasi pin buzzer sebagai output
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(BUZZER, GPIO.LOW)  # Matikan buzzer pada awalnya

first_connection = True  # Variabel untuk menandai koneksi pertama

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        global first_connection
        if rc == 0 and first_connection:  # Hanya kirim pesan jika koneksi pertama berhasil
            print("Terhubung ke Broker MQTT!")
            first_connection = False
        elif rc != 0:
            print("Gagal terhubung, kode return %d\n" % rc)

    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def read_distance():
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def control_buzzer(distance):
    if distance < 20:  # Ubah nilai jarak sesuai kebutuhan
        GPIO.output(BUZZER, GPIO.HIGH)  # Aktifkan buzzer jika jarak kurang dari 10 cm
    else:
        GPIO.output(BUZZER, GPIO.LOW)  # Matikan buzzer jika jarak lebih dari 10 cm

def publish_sensor_data(client):
    while True:
        start_time = time.time()

        distance = read_distance()

        ultrasonic_message = {
            "Distance": distance
        }
        ultrasonic_msg = json.dumps(ultrasonic_message)
        client.publish(topic_publish, ultrasonic_msg)
        print(f"Published Ultrasonic Data - Distance: {distance}")

        control_buzzer(distance)  # Kontrol buzzer berdasarkan jarak yang terbaca

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < 5:
            time.sleep(5 - elapsed_time)  # Menunggu sisa waktu dalam 1 detik

def run():
    client = connect_mqtt()
    client.loop_start()

    publish_sensor_data(client)  # Publish data sensor

    try:
        while True:
            # Melakukan apapun yang diperlukan selama program berjalan
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Cleaning up GPIO.")
        GPIO.cleanup()

# Bagian utama kode
if _name_ == '_main_':
    run()