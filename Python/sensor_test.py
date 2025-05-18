"""
This class creates an instance of the Trigno base. Put your key and license here.
"""
import clr
import time
clr.AddReference(r"C:\Users\avame\Desktop\CVPRDemo\Python\resources\DelsysAPI.dll")
clr.AddReference("System.Collections")

from Aero import AeroPy

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABK6j3XKolzpmZLiPRgiaV7Qa8RycW+iq9OA2Ev0aAD7AocK39Q9bvYk8J7blLCdI9bsjUgDyVXSQrynk+td4ARU="
license = "<License>  <Id>f0a08902-c5cc-4e65-b1f3-bf46455d1110</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sean Banerjee</Name>    <Email>tars@clarkson.edu</Email>  </Customer>  <Expiration>Wed, 31 Dec 2031 05:00:00 GMT</Expiration>  <Signature>MEUCICX8TO1GpsGaszHDVhhkmmRvz89kICERiC53+AXR1chQAiEAt4oZ8SRlnyh6n6gDjEXE+I+UUjPzuqsjDQBbgBRQTdE=</Signature></License>"


class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()
    

base = TrignoBase()
TrigBase = base.BaseInstance

TrigBase.ValidateBase(key,license)
TrigBase.ScanSensors()
time.sleep(2)

#select the sensor found in the scan
TrigBase.SelectSensor(0)



TrigBase.Configure(False, False)

ready_to_start = TrigBase.IsPipelineConfigured()
print(f"Is pipeline configured for data streaming: {ready_to_start}")

while ready_to_start == True:
    TrigBase.Start()
    time.sleep(5)
    ready_to_start = False
TrigBase.Stop()
TrigBase.ResetPipeline()
#     if TrigBase.CheckDataQueue() == True:
#         Current_data = TrigBase.PollData()
#         print(Current_data)

#     time.sleep(5)
#     TrigBase.Stop()
#     ready_to_start = False

# normally an array to pull the data