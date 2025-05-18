# Ava Megyeri, retry


# imports for Kinova & Delsys API
import sys
import clr
import os
import time
import numpy as np
import threading
import utilities
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient

clr.AddReference(r"C:\Users\avame\Desktop\CVPRDemo\Python\resources\DelsysAPI.dll")
clr.AddReference("System.Collections")
from Aero import AeroPy

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABK6j3XKolzpmZLiPRgiaV7Qa8RycW+iq9OA2Ev0aAD7AocK39Q9bvYk8J7blLCdI9bsjUgDyVXSQrynk+td4ARU="
license = "<License>  <Id>f0a08902-c5cc-4e65-b1f3-bf46455d1110</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sean Banerjee</Name>    <Email>tars@clarkson.edu</Email>  </Customer>  <Expiration>Wed, 31 Dec 2031 05:00:00 GMT</Expiration>  <Signature>MEUCICX8TO1GpsGaszHDVhhkmmRvz89kICERiC53+AXR1chQAiEAt4oZ8SRlnyh6n6gDjEXE+I+UUjPzuqsjDQBbgBRQTdE=</Signature></License>"

"""Delsys API Section"""
class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()
    
"""
Scan for sensors function
"""
def scan_for_sensors(TrigBase):
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

"""
Outputs the data with PollData()
"""
def GetData(TrigBase):
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


"""Kinova API Section"""
class GripperCommandExample:
    def __init__(self, router, proportional_gain = 2.0):

        self.proportional_gain = proportional_gain
        self.router = router

        # Create base client using TCP router
        self.base = BaseClient(self.router)

    

    


def close_gripper2(base):
        gripper_command = Base_pb2.GripperCommand()
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger = gripper_command.gripper.finger.add()
        finger.finger_identifier = 1
        finger.value = 1.0  # Fully closed position

        base.SendGripperCommand(gripper_command)

        # Wait for a short period to ensure the gripper has time to close
        time.sleep(2)
        return True
def open_gripper(base):
    gripper_command = Base_pb2.GripperCommand()
    gripper_command.mode = Base_pb2.GRIPPER_POSITION
    finger = gripper_command.gripper.finger.add()
    finger.finger_identifier = 1
    finger.value = 0.0  # Fully closed position

    base.SendGripperCommand(gripper_command)

    # Wait for a short period to ensure the gripper has time to close
    time.sleep(2)
    return True

def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications

    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
            # print(notification)
    return check


TIMEOUT_DURATION = 30
def example_move_to_home_position(base):
    # Make sure the arm is in Single Level Servoing mode
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)
    
    # Move arm to ready position
    print("Moving the arm to a safe position")
    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
    action_list = base.ReadAllActions(action_type)
    action_handle = None
    for action in action_list.action_list:
        if action.name == "Home":
            action_handle = action.handle

    if action_handle == None:
        print("Can't reach safe position. Exiting")
        return False

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    base.ExecuteActionFromReference(action_handle)
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Safe position reached")
    else:
        print("Timeout on action notification wait")
    return finished

def populateCartesianCoordinate(waypointInformation):
    
    print(waypointInformation)
    waypoint = Base_pb2.CartesianWaypoint()  
    waypoint.pose.x = waypointInformation[0]
    waypoint.pose.y = waypointInformation[1]
    waypoint.pose.z = waypointInformation[2]
    waypoint.blending_radius = waypointInformation[3]
    waypoint.pose.theta_x = waypointInformation[4]
    waypoint.pose.theta_y = waypointInformation[5]
    waypoint.pose.theta_z = waypointInformation[6] 
    waypoint.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_BASE
    
    return waypoint

def start_position(base, base_cyclic):
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)
    product = base.GetProductConfiguration()
    waypointsDefinition = tuple(tuple())
    if product.model == Base_pb2.ProductConfiguration__pb2.MODEL_ID_L53:
        waypointsDefinition = ((0.451, .004, .081, 0.0, 139.961, .263, 90.88),)
    else:
        print("Product is not compatible to run this example. Please contact support with the KIN number below")
        print("Product KIN is : " + product.kin)
        return False

    waypoints = Base_pb2.WaypointList()
    waypoints.duration = 0.0
    waypoints.use_optimal_blending = False
    
    index = 0
    waypoint = waypoints.waypoints.add()
    waypoint.name = "waypoint_" + str(index)
    waypoint.cartesian_waypoint.CopyFrom(populateCartesianCoordinate(waypointsDefinition[index]))

    # Verify validity of waypoints
    result = base.ValidateWaypointList(waypoints)
    if len(result.trajectory_error_report.trajectory_error_elements) == 0:
        e = threading.Event()
        notification_handle = base.OnNotificationActionTopic(
            check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        print("Moving cartesian trajectory...")
        base.ExecuteWaypointTrajectory(waypoints)
        finished = e.wait(TIMEOUT_DURATION)
        base.Unsubscribe(notification_handle)

        if finished:
            print("Cartesian trajectory completed")
            return True
        else:
            print("Timeout on action notification wait")
            return False
    else:
        print("Error found in trajectory")
        print(result)
        return False 




def end_example(base, base_cyclic):
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)
    product = base.GetProductConfiguration()
    waypointsDefinition = tuple(tuple())
    if product.model == Base_pb2.ProductConfiguration__pb2.MODEL_ID_L53:
        waypointsDefinition = ((0.655, .001, .345, 0.0, 140.222, .263, 90.885),)
    else:
        print("Product is not compatible to run this example. Please contact support with the KIN number below")
        print("Product KIN is : " + product.kin)
        return False

    waypoints = Base_pb2.WaypointList()
    waypoints.duration = 0.0
    waypoints.use_optimal_blending = False
    
    index = 0
    waypoint = waypoints.waypoints.add()
    waypoint.name = "waypoint_" + str(index)
    waypoint.cartesian_waypoint.CopyFrom(populateCartesianCoordinate(waypointsDefinition[index]))

    # Verify validity of waypoints
    result = base.ValidateWaypointList(waypoints)
    if len(result.trajectory_error_report.trajectory_error_elements) == 0:
        e = threading.Event()
        notification_handle = base.OnNotificationActionTopic(
            check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        print("Moving cartesian trajectory...")
        base.ExecuteWaypointTrajectory(waypoints)
        finished = e.wait(TIMEOUT_DURATION)
        base.Unsubscribe(notification_handle)

        if finished:
            print("Cartesian trajectory completed")
            return True
        else:
            print("Timeout on action notification wait")
            return False
    else:
        print("Error found in trajectory")
        print(result)
        return False 




def configure_and_stream(TrigBase, base, base_cyclic, holding_max):
    max_values = []
    success = True 
    TrigBase.Configure(False, False)
    
    ready_to_start = TrigBase.IsPipelineConfigured()
    print(f"Is pipeline configured for data streaming: {ready_to_start}")
    threshold = (holding_max * .25)
    threshold_flag = True
    if ready_to_start:
        TrigBase.Start()
        success &= example_move_to_home_position(base)
        success &= start_position(base, base_cyclic)
        time.sleep(1)
        success &= close_gripper2(base)
        success &= end_example(base, base_cyclic)

        time.sleep(.5)
        while threshold_flag:
            Dataout = GetData(TrigBase=TrigBase)
            if Dataout is not None:
                
                print(max(Dataout[0][0]))
                if max(Dataout[0][0]) >= (holding_max * .75):
                    continue
                if max(Dataout[0][0]) >= threshold:
                    print(max(Dataout[0][0]))
                    print("threshold reached")
                    #we open the the gripper here 
                    success &= open_gripper(base)
                    success &= example_move_to_home_position(base)
                    threshold_flag = False
         
        TrigBase.Stop()
        TrigBase.ResetPipeline()
    return success










"""_
idea:
1. move to a spot to grab object (only once) **
2. close gripper to grab object **
3. set trajectory to go towards the person **
4. person w sensors grabs object
5. if the sensor goes higher than a certain amount then robot opens its gripper when person grasps obejct
6. back to either home spot or spot to grab object
"""

def get_thresholds(TrigBase):
    print("-----Getting Thresholds-----")
    TrigBase.ValidateBase(key,license)

    # select the sensor used 
    scan_for_sensors(TrigBase)

    TrigBase.Configure(False, False)
            
    ready_to_start = TrigBase.IsPipelineConfigured()
    print(f"Is pipeline configured for data streaming: {ready_to_start}")

    max_flag = True
    if ready_to_start:
        TrigBase.Start()
        time.sleep(.5)
    
        while max_flag:
            Dataout = GetData(TrigBase)
            if Dataout is not None:
                if max(Dataout[0][0]) >= 1:
                        continue
                #get resting max
                holding_max = max(Dataout[0][0])
                print(holding_max)
                max_flag = False
                
    TrigBase.Stop()
    TrigBase.ResetPipeline()
    print("-----Complete-----")
    return holding_max
        
def main():
    
    
    #Delsys API setup
    base = TrignoBase()
    TrigBase = base.BaseInstance
    
    #Get thresholding needed
    holding_max = get_thresholds(TrigBase)
    
    #validate the base
    # TrigBase.ValidateBase(key,license)
    
    #scan for sensors
    # scan_for_sensors(TrigBase=TrigBase)  

    # Parse arguments
    args = utilities.parseConnectionArguments()
    
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        # Create required services
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)

        # success = True
        # success &= example_move_to_home_position(base)
        # success &= start_position(base, base_cyclic)
        # # time.sleep(2)
        # success &= close_gripper2(base)
        # success &= end_example(base, base_cyclic)
        # #add a function to configure and start the data streaming
        # success &= configure_and_stream(TrigBase, base)
        
        #for cvpr
        success = True
        success &= configure_and_stream(TrigBase, base, base_cyclic, holding_max)
    
        if not success:
            print("An error occurred during the execution.")      
        
        
        
        

        
        

if __name__ == "__main__":
    main()