import sys
from xml.etree.ElementTree import tostring
from ids_peak import ids_peak as peak
from ids_peak_ipl import ids_peak_ipl 
 
m_device = None
m_dataStream = None
m_node_map_remote_device = None
 
 
def open_camera():
    global m_device, m_node_map_remote_device
    try:
        # Create instance of the device manager
        device_manager = peak.DeviceManager.Instance()
 
      # Update the device manager
        device_manager.Update()
 
      # Return if no device was found
        if device_manager.Devices().empty():
            return False
 
      # open the first openable device in the device manager's device list
        device_count = device_manager.Devices().size()
        for i in range(device_count):
            if device_manager.Devices()[i].IsOpenable():
                m_device = device_manager.Devices()[i].OpenDevice(peak.DeviceAccessType_Control)
 
              # Get NodeMap of the RemoteDevice for all accesses to the GenICam NodeMap tree
                m_node_map_remote_device = m_device.RemoteDevice().NodeMaps()[0]
 
                return True
    except Exception as e:
        # ...
         str_error = str(e)
 
    return False
 
 
def prepare_acquisition():
    global m_dataStream
    try:
        data_streams = m_device.DataStreams()
        if data_streams.empty():
            # no data streams available
            return False
 
        m_dataStream = m_device.DataStreams()[0].OpenDataStream()
 
        return True
    except Exception as e:
        # ...
        str_error = str(e)
 
    return False
 
 
def set_roi(x, y, width, height):
    try:
        # Get the minimum ROI and set it. After that there are no size restrictions anymore
        x_min = m_node_map_remote_device.FindNode("OffsetX").Minimum()
        y_min = m_node_map_remote_device.FindNode("OffsetY").Minimum()
        w_min = m_node_map_remote_device.FindNode("Width").Minimum()
        h_min = m_node_map_remote_device.FindNode("Height").Minimum()
 
        m_node_map_remote_device.FindNode("OffsetX").SetValue(x_min)
        m_node_map_remote_device.FindNode("OffsetY").SetValue(y_min)
        m_node_map_remote_device.FindNode("Width").SetValue(w_min)
        m_node_map_remote_device.FindNode("Height").SetValue(h_min)
 
        # Get the maximum ROI values
        x_max = m_node_map_remote_device.FindNode("OffsetX").Maximum()
        y_max = m_node_map_remote_device.FindNode("OffsetY").Maximum()
        w_max = m_node_map_remote_device.FindNode("Width").Maximum()
        h_max = m_node_map_remote_device.FindNode("Height").Maximum()

        # uncomment here to get the x, y, width, height value
        #print("min value is ",x_min, y_min, w_min, h_min)
        #print("max value is ",x_max, y_max, w_max, h_max)
 
        if (x < x_min) or (y < y_min) or (x > x_max) or (y > y_max):
            print("exceed x or y")
            return False
        elif (width < w_min) or (height < h_min) or ((x + width) > w_max) or ((y + height) > h_max):
            if width < w_min:
                print("width < w_min")
            elif height < h_min:
                print("height < h_min")
            elif (x + width) > w_max:
                print("(x + width) > w_max")
            else:
                print("(y + height) > h_max")
            print("exceed width or height")
            return False
        else:
            # Now, set final AOI
            m_node_map_remote_device.FindNode("OffsetX").SetValue(x)
            m_node_map_remote_device.FindNode("OffsetY").SetValue(y)
            m_node_map_remote_device.FindNode("Width").SetValue(width)
            m_node_map_remote_device.FindNode("Height").SetValue(height)
 
            return True
    except Exception as e:
        print(e)
        # ...
        str_error = str(e)
 
    return False
 
 
def alloc_and_announce_buffers():
    try:
        if m_dataStream:
            # Flush queue and prepare all buffers for revoking
            m_dataStream.Flush(peak.DataStreamFlushMode_DiscardAll)
 
            # Clear all old buffers
            for buffer in m_dataStream.AnnouncedBuffers():
                m_dataStream.RevokeBuffer(buffer)
 
            payload_size = m_node_map_remote_device.FindNode("PayloadSize").Value()
 
            # Get number of minimum required buffers
            num_buffers_min_required = m_dataStream.NumBuffersAnnouncedMinRequired()
 
            # Alloc buffers
            for count in range(num_buffers_min_required):
                buffer = m_dataStream.AllocAndAnnounceBuffer(payload_size)
                m_dataStream.QueueBuffer(buffer)
 
            return True
    except Exception as e:
        # ...
        str_error = str(e)
 
    return False
 
 
def start_acquisition():
    try:
        m_dataStream.StartAcquisition(peak.AcquisitionStartMode_Default, peak.DataStream.INFINITE_NUMBER)
        m_node_map_remote_device.FindNode("TLParamsLocked").SetValue(1)
        m_node_map_remote_device.FindNode("AcquisitionStart").Execute()
       
        return True
    except Exception as e:
        print(e)
        # ...
        str_error = str(e)
 
    return False

def set_focus():
    try:
        # Before accessing FocusAuto, make sure OpticControllerSelector is set correctly
        # ﻿# Set OpticControllerSelector to "OpticController0" (str)
        m_node_map_remote_device.FindNode("OpticControllerSelector").SetCurrentEntry("OpticController0")
        # Determine the current entry of FocusAuto (str)
        value_auto = m_node_map_remote_device.FindNode("FocusAuto").CurrentEntry().SymbolicValue()
        # print("FocusAuto: "+value_auto)
        # Get a list of all available entries of FocusAuto
        allEntries = m_node_map_remote_device.FindNode("FocusAuto").Entries()
        availableEntries = []
        for entry in allEntries:
            if (entry.AccessStatus() != peak.NodeAccessStatus_NotAvailable
            and entry.AccessStatus() != peak.NodeAccessStatus_NotImplemented):
                availableEntries.append(entry.SymbolicValue())
        # Set FocusAuto to "Off" (str)
        m_node_map_remote_device.FindNode("FocusAuto").SetCurrentEntry("Off")

        # Before accessing FocusStepper, make sure OpticControllerSelector is set correctly
        # ﻿# Set OpticControllerSelector to "OpticController0" (str)
        m_node_map_remote_device.FindNode("OpticControllerSelector").SetCurrentEntry("OpticController0")
        # Determine the current FocusStepper (int)
        value_stepper = m_node_map_remote_device.FindNode("FocusStepper").Value()
        # print("FocusStepper: "+tostring(value_stepper))
        # Set FocusStepper to 100 (int)
        m_node_map_remote_device.FindNode("FocusStepper").SetValue(1)

        return True

    except Exception as e:
        print(e)

    return False
    
def set_exposure(ms_value):
    try:
        
        # Get remote device nodemap
        # m_node_map_remote_device = m_device.RemoteDevice().NodeMaps().at(0)
        m_node_map_remote_device = m_device.RemoteDevice().NodeMaps()[0]
        
        # min_exposure_time = 0
        # max_exposure_time = 0
        # inc_exposure_time = 0

        # # Get exposure range. All values in microseconds
        # min_exposure_time = m_node_map_remote_device.FindNode("ExposureTime").Minimum()
        # max_exposure_time = m_node_map_remote_device.FindNode("ExposureTime").Maximum()
        # print('2')
        # print('max_fps & min_fps: ')
 
        # if m_node_map_remote_device.FindNode("ExposureTime").HasConstantIncrement():
        #    inc_exposure_time = m_node_map_remote_device.FindNode("ExposureTime").Increment()
        # else:
        #   # If there is no increment, it might be useful to choose a suitable increment for a GUI control element (e.g. a slider)
        #    inc_exposure_time = 1000

        # # Get the current exposure time
        # exposure_time = m_node_map_remote_device.FindNode("ExposureTime").Value()

        # Set exposure time to minimum
        m_node_map_remote_device.FindNode("ExposureTime").SetValue(ms_value)
        
        return True
        
    except Exception as e:
        str_error = str(e)
    
    return False

def set_frame_rate(fps_value):
    try:
        print('fr')
        # Get the NodeMap of the RemoteDevice
        m_node_map_remote_device = m_device.RemoteDevice().NodeMaps()[0]
        print('y')

        min_frame_rate = 0
        max_frame_rate = 0
        inc_frame_rate = 0

        # Get frame rate range. All values in fps.
        min_frame_rate = m_node_map_remote_device.FindNode("AcquisitionFrameRate").Minimum()
        max_frame_rate = m_node_map_remote_device.FindNode("AcquisitionFrameRate").Maximum()

        if m_node_map_remote_device.FindNode("AcquisitionFrameRate").HasConstantIncrement():
           inc_frame_rate = m_node_map_remote_device.FindNode("AcquisitionFrameRate").Increment()
        else:
          # If there is no increment, it might be useful to choose a suitable increment for a GUI control element (e.g. a slider)
           inc_frame_rate = 0.1

        # Get the current frame rate
        frame_rate = m_node_map_remote_device.FindNode("AcquisitionFrameRate").Value()

        # Set frame rate to maximum
        m_node_map_remote_device.FindNode("AcquisitionFrameRate").SetValue(fps_value)
        
        return True
        
    except Exception as e:
        str_error = str(e)
        
    return False
 
def main():
    
    # initialize library
    peak.Library.Initialize()
 
    if not open_camera():
        # error
        sys.exit(1)
 
    if not prepare_acquisition():
        # error
        sys.exit(2)
 
    # (x-0), (y-0), (width-0), (height-0) must be divided by 12 with no rest
    #if not set_roi(24, 24, 2784, 1968):
    if not set_roi(1164, 290, 984, 2330):
        # error
        sys.exit(3)

    if not set_focus():
        sys.exit(4)
    print('1')
 
    if not set_frame_rate(19.73):
        sys.exit(6)
       
    if not set_exposure(1.05):
        sys.exit(5)
    

    
 
    if not alloc_and_announce_buffers():
        # error
        sys.exit(7)
 
    if not start_acquisition():
        # error
        sys.exit(8)
    

    
 
    
    try:
        # Get buffer from device's DataStream. Wait 5000 ms. The buffer is automatically locked until it is queued again.
        buffer = m_dataStream.WaitForFinishedBuffer(5000)
 
        # Create IDS peak IPL image from buffer
        image = ids_peak_ipl.Image_CreateFromSizeAndBuffer(
            buffer.PixelFormat(),
            buffer.BasePtr(),
            buffer.Size(),
            buffer.Width(),
            buffer.Height()
        )
 
        # Create IDS peak IPL image for debayering and convert it to RGBa8 format
        image_processed = image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
 
        # Queue buffer again
        m_dataStream.QueueBuffer(buffer)
 
        file = "airto_5.jpg"
        ids_peak_ipl.ImageWriter.Write(file, image_processed)
            
    except Exception as e:
            # ...
        str_error = str(e)
        print(str_error)

 
    peak.Library.Close()
    sys.exit(0)
 
 
if __name__ == '__main__':
    main()
