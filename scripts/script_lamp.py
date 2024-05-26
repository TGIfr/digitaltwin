import boto3
import uuid
import datetime
import random
import time

# AWS SiteWise Alias
lampLigthStatusAlias = '/home/lamp1/light'
lampNoizeLevelAlias = '/home/lamp1/noize'
climateTemperatureAlias = '/home/clim1/temperature'
climateIsCoolingAlias = '/home/clim1/isCooling'
climateIsHeatingAlias = '/home/clim1/isHeating'

currentTemp = 21
currentNoiseLevel = 40

clapThreshold = 100

startHeatingThreshold = 18
stopHeatingThreshold = 20

startCoolingThreshold = 25
stopCoolingThreshold = 22

currentLampStatus = True
currentHeatingStatus = False
currentCoolingStatus = False


def get_lamp_status(noise_level):
    global currentLampStatus
    if noise_level > clapThreshold:
        currentLampStatus = not currentLampStatus

    return currentLampStatus


climateCounter = 0


def update_climate_values():
    global currentCoolingStatus
    global currentHeatingStatus
    global currentTemp

    if climateCounter < 20:
        currentTemp += 0.5
    elif climateCounter < 30:
        currentTemp += random.random() / 2
    elif climateCounter < 50:
        currentTemp -= 0.5
    elif climateCounter < 70:
        currentTemp += random.random() / 2

    if currentCoolingStatus:
        currentTemp -= 1

    if currentHeatingStatus:
        currentTemp += 1

    if currentTemp >= startCoolingThreshold and not currentCoolingStatus:
        currentCoolingStatus = True
    elif currentTemp <= stopCoolingThreshold and currentCoolingStatus:
        currentCoolingStatus = False

    if currentTemp <= startHeatingThreshold and not currentHeatingStatus:
        currentHeatingStatus = True
    elif currentTemp >= startHeatingThreshold and currentHeatingStatus:
        currentHeatingStatus = False

# Create a Boto3 SiteWise client (Make sure region_name is the one you plan to use)
client = boto3.client('iotsitewise', region_name='eu-west-1')

# Send data at 1-second intervals indefinitely
while True:
    currentNoiseLevel = random.randrange(10, 110)
    isLampOn = get_lamp_status(currentNoiseLevel)
    update_climate_values()

    epoch = int(time.time())  # Get the current epoch timestamp using time.time()

    # Create the JSON payload
    payload = {
        "entries": [
            {
                "entryId": str(uuid.uuid4()),
                "propertyAlias": climateTemperatureAlias,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": currentTemp
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(uuid.uuid4()),
                "propertyAlias": climateIsHeatingAlias,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": currentHeatingStatus
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(uuid.uuid4()),
                "propertyAlias":climateIsCoolingAlias,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": currentCoolingStatus
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(uuid.uuid4()),
                "propertyAlias": lampLigthStatusAlias,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": isLampOn
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(uuid.uuid4()),
                "propertyAlias": lampNoizeLevelAlias,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": currentNoiseLevel
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            }
        ]
    }

    # Send the data to AWS SiteWise
    try:
        response = client.batch_put_asset_property_value(entries=payload['entries'])
        print("Data sent successfully: {}".format(payload))
    except Exception as e:
        print("Error sending data: {}".format(e))

    time.sleep(1)  # Wait for 1 second before sending