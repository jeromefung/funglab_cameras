'''
Look at techniques in Camera_Examples/Python/grab_single_frame.py

Need to use pip to install the Thorlabs python library first.
'''


import os
import sys
import numpy as np
import cv2
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE, ROI
import tifffile



# see Camera_Examples/Python/windows_setup.py
# configure path to import dlls
relative_path_to_dlls = '.' + os.sep + 'dlls' + os.sep + '64_lib'
absolute_path_to_file_directory = os.path.dirname(os.path.abspath(__file__))
absolute_path_to_dlls = os.path.abspath(absolute_path_to_file_directory + 
                                        os.sep + relative_path_to_dlls)
os.environ['PATH'] = absolute_path_to_dlls + os.pathsep + os.environ['PATH']
os.add_dll_directory(absolute_path_to_dlls)

# desired ROI
upper_left_x = 200
upper_left_y = 400
image_size_x = 600
image_size_y = 300
my_roi = ROI(upper_left_x, upper_left_y, upper_left_x + image_size_x, 
             upper_left_y + image_size_y)

# either use a with statement as here, or use dispose() method
# to destroy SDK instance prior to creating another one
with TLCameraSDK() as sdk():
    available_cemars = sdk.discover_available_cameras()
    if len(available_cameras) < 1:
        print("no cameras detected")
        
    with sdk.open_camera(available_cameras[0]) as camera:
        camera.exposure_time_us = 5000 # 5 ms
        camera.roi = my_roi
        camera.operation_mode = SOFTWARE_TRIGGERED 
        camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        
        # get 10 images per software trigger
        n_frames = 10
        camera.tl_camera_get_frames_per_trigger_zero_for_unlimited = n_frames
        
        # frame rate control
        camera.is_frame_rate_control_enabled = True 
        print(camera.frame_rate_control_value_range)
        camera.frame_rate_control_value = 10 # fps
        
        # arm the camera 
        camera.arm(n_frames) # buffer w/10 frames 
        
        # trigger
        camera.issue_software_trigger()
        
        # allocate an array to store data
        frame_data = np.zeros((n_frames, image_size_x, image_size_y), 
                              dtype = np.ushort)
        
        # get data from camera
        for i in range(n_frames):
            frame = camera.tl_camera_get_pending_frame_or_null()
            if frame is not None:
                print('frame ' + str(frame.frame_count) + ' received')
                frame_data[i, :, :] = np.copy(frame.image_buffer)
            else:
                print("timeout reached")
                break
                
        camera.disarm()
        
# save the data 
np.save('images.npy', frame_data)
                
# save as tiffs
for i in range(n_frames):
    fname = 'img_' _ str(i).zfill(2) + '.tif'
    tifffile.imwrite(fname, frame_data[i], photometric = 'minisblack')
    
        
        
        
        
