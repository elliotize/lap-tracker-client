'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from faceometer import FaceDetector
from datetime import datetime
import picamera
import sys
import logging
import time
import getopt
import boto3

camera = picamera.PiCamera()
facedetector = FaceDetector()
pics_dir = "/home/pi/laptracker/pics"
s3 = boto3.resource('s3')
bucket_name = "msmith-tracking-image-bucket"

# Say Cheese
def say_cheese():
    filename = time.strftime("%Y%m%d-%H%M%S",time.gmtime())
    print(filename)
	camera.capture("{pics_dir}/{filename}.jpg".format(filename=filename, pics_dir=pics_dir))
    print("from publisher: {pics_dir}/{filename}.jpg")
    return facedetector.detect("{pics_dir}/{filename}.jpg")

# Usage
usageInfo = """Usage:

Start face detection:
python face_publisher.py -i <seconds to wait between taking pictures>

Type "python face_publisher.py -h" for available options.
"""
# Help info
helpInfo = """-i, --interval
	Seconds to wait between taking pictures
-h, --help
	Help information
"""

# Read in command-line parameters
useWebsocket = False
interval=1
topic="facedetection1"
host = "a5026ozfxej17.iot.us-east-1.amazonaws.com"
rootCAPath = "/home/pi/security/root_ca.key"
certificatePath = "/home/pi/security/667_cert.pem"
privateKeyPath = "/home/pi/security/667_private_key.pem"
try:
	opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "interval="])
	# if len(opts) == 0:
	# 	raise getopt.GetoptError("No input parameters!")
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpInfo)
			exit(0)
		if opt in ("-i", "--interval"):
			interval = arg
except getopt.GetoptError:
	print(usageInfo)
	exit(1)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
# myAWSIoTMQTTClient = None
# if useWebsocket:
# 	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
# 	myAWSIoTMQTTClient.configureEndpoint(host, 443)
# 	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
# else:
# 	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
# 	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
# 	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
#
# # AWSIoTMQTTClient connection configuration
# myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
# myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
# myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
# myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
# myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
#
# # Connect and subscribe to AWS IoT
# myAWSIoTMQTTClient.connect()

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    detection_response = say_cheese()
    if detection_response.success:
        imagedata = open(detection_response.filepath, 'rb')
        s3.Bucket(bucket_name).put_object(Key=detection_response.filepath, Body=imagedata, Metadata=detection_response)
	# myAWSIoTMQTTClient.publish("facedetection1", detection_response, 1)
	loopCount += 1
	time.sleep(interval)
