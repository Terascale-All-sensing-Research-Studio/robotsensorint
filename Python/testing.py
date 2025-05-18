"""
This class creates an instance of the Trigno base. Put your key and license here.
"""
import clr
import time
import numpy as np
clr.AddReference(r"C:\Users\avame\Desktop\CVPRDemo\Python\resources\DelsysAPI.dll")
clr.AddReference("System.Collections")

from Aero import AeroPy

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABK6j3XKolzpmZLiPRgiaV7Qa8RycW+iq9OA2Ev0aAD7AocK39Q9bvYk8J7blLCdI9bsjUgDyVXSQrynk+td4ARU="
license = "<License>  <Id>f0a08902-c5cc-4e65-b1f3-bf46455d1110</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sean Banerjee</Name>    <Email>tars@clarkson.edu</Email>  </Customer>  <Expiration>Wed, 31 Dec 2031 05:00:00 GMT</Expiration>  <Signature>MEUCICX8TO1GpsGaszHDVhhkmmRvz89kICERiC53+AXR1chQAiEAt4oZ8SRlnyh6n6gDjEXE+I+UUjPzuqsjDQBbgBRQTdE=</Signature></License>"

class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()
    

def scan_for_sensors():
    f = TrigBase.ScanSensors().Result
    all_scanned_sensors = TrigBase.GetScannedSensorsFound()
    print("Sensors Found:\n")
    for sensor in all_scanned_sensors:
        print("(" + str(sensor.PairNumber) + ") " +
            sensor.FriendlyName + "\n" +
            sensor.Configuration.ModeString + "\n")
    SensorCount = len(all_scanned_sensors)
    for i in range(SensorCount):
        TrigBase.SelectSensor(i)


def GetData():
    dataReady = TrigBase.CheckDataQueue()
    
    if dataReady:
        
        DataOut = TrigBase.PollData()   
        outArr = [[] for i in range(len(DataOut.Keys))]             # Set output array size to the amount of channels being outputted from the DelsysAPI

        channel_guid_keys = list(DataOut.Keys)                      # Generate a list of all channel GUIDs in the dictionary
        for j in range(len(DataOut.Keys)):                          # loop all channels
            chan_data = DataOut[channel_guid_keys[j]]               # Index a single channels data from the dictionary based on unique channel GUID (key)
            outArr[j].append(np.asarray(chan_data, dtype='object')) # Create a NumPy array of the channel data and add to the output array

                   # Dictionary<Guid, List<double>> (key = Guid (Unique channel ID), value = List(Y) (Y = sample value)
        return outArr
    else:
        return None




base = TrignoBase()
TrigBase = base.BaseInstance

# validate the base
TrigBase.ValidateBase(key,license)

# select the sensor used 
scan_for_sensors()

TrigBase.Configure(False, False)
        
ready_to_start = TrigBase.IsPipelineConfigured()
print(f"Is pipeline configured for data streaming: {ready_to_start}")

resting_flag = True
max_flag = True
if ready_to_start:
    TrigBase.Start()
    time.sleep(.5)
    while max_flag:
        Dataout = GetData()
        if Dataout is not None:
            if max(Dataout[0][0]) >= 1:
                    continue
            #get resting max
            holding_max = max(Dataout[0][0])
            print(holding_max)
            print(f" 90% percent: {holding_max * .9}")
            max_flag = False
            
TrigBase.Stop()
TrigBase.ResetPipeline()




#want to get resting max, then when holding object max. Then use both of those to set the threshold and jittering 
