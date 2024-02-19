from ultralytics import YOLO
import torch
import h5py
import os
from datetime import datetime, timedelta
import numpy as np
from live_weather import get_current_weather


'''
    This script generates the time-series data from live-steam video in the following format -- float64 :-
    | Date(YYYYMMDD) | Hour | Minute | Seconds | Time Normalized | Track ID | Obj Class | Centroid_x | Centroid_y | Temp (C) 2m | Humidity (%) 2m |...
    ...| Rain (mm) | Showers (mm) | Cloud Cover (%) | 
'''


link = 'https://62abe29de64ab.streamlock.net:4444/EPGD/pps3.stream/chunklist_w2096451211.m3u8'
#link = 'Data/Videos/6/Gdansk_Live_Stream_6.mp4'

# clear cache
torch.cuda.empty_cache()

# Enable GPU if available
device = "0" if torch.cuda.is_available() else "cpu"
if device == "0":
    torch.cuda.set_device(0)


# Load the trained model (last epoch or best epoch)
model = YOLO('weights/last.pt')


# create a path to store time-series data if it doesn't exist already
folder_path = 'Raw_Time_Series_Data'
if not os.path.exists(folder_path):
    os.mkdir(folder_path)


# Prepare CSV File
hdf5_file_path = os.path.join(folder_path, 'tracking_data.h5')

try:
    # Create or open hdf5 file
    with h5py.File(hdf5_file_path, 'a', libver = 'latest', swmr = True) as file:
        # Enable Single Writer Multiple Reader (SWMR) Mode
        file.swmr_mode = True

        # Check if the dataset exists, create if not
        if 'tracking_data' not in file:
            # Create a resizable dataset to store tracking data
            maxshape = (None, 16)# Maximum shape is unknown for the first dimension
            dataset = file.create_dataset('tracking_data', (0, 16), maxshape = maxshape, dtype = np.float64)
        else:
            dataset = file['tracking_data']

        for result in model.track(source = link, show = False, 
                                conf = 0.7, save = False, 
                                line_width = 4, stream = True, 
                                persist = True, save_txt = False,
                                save_frames = True, show_labels = True, show_boxes = False):
            
            # GMT +1 Time
            current_time = datetime.utcnow() + timedelta(hours=1)

            # Get Live Weather Report
            current_temperature_2m, current_relative_humidity_2m, current_rain, current_showers, current_snowfall, current_cloud_cover = get_current_weather()
            
            # Get Ids, classes and bounding boxes 
            track_id = result.boxes.id.numpy()        
            obj_class = result.boxes.cls.numpy()     
            rectangle_bb = result.boxes.xyxy.numpy()

            # Calculate centroid
            x_centers = (rectangle_bb[:, 0] + rectangle_bb[:, 2])/2
            y_centers = (rectangle_bb[:, 1] + rectangle_bb[:, 3])/2

            # Time Component
            date = float(current_time.strftime('%Y%m%d'))
            hour = float(current_time.strftime('%H'))
            minute = float((datetime.utcnow() + timedelta(hours=1)).minute)
            seconds = float((datetime.utcnow() + timedelta(hours=1)).second)
            microseconds = float((datetime.utcnow() + timedelta(hours=1)).microsecond)

            time_normalized = (hour + minute/60.0 + seconds/3600.0 + microseconds/(60*60*1000000))/24

            # Replicate the weather data for each detected object
            replicated_temp = np.full(len(track_id), current_temperature_2m)
            replicated_humidity = np.full(len(track_id), current_relative_humidity_2m)
            replicated_rain = np.full(len(track_id), current_rain)
            replicated_showers = np.full(len(track_id), current_showers)
            replicated_snowfall = np.full(len(track_id), current_snowfall)
            replicated_cloud_cover = np.full(len(track_id), current_cloud_cover)

            data = np.column_stack((np.full(len(track_id), date),
                                    np.full(len(track_id), hour),
                                    np.full(len(track_id), minute),
                                    np.full(len(track_id), seconds),
                                    np.full(len(track_id), microseconds),
                                    np.full(len(track_id), time_normalized),
                                    track_id, obj_class, x_centers, y_centers,
                                    replicated_temp, replicated_humidity, replicated_rain, replicated_showers, replicated_snowfall, replicated_cloud_cover))
            
            # Append data to dataset
            new_size = dataset.shape[0] + len(data)
            dataset.resize(new_size, axis = 0)
            dataset[-len(data):] = data

            # Flush data to disk -- crucial to visualize the tracking plots in real-time via live_tracker.py
            file.flush()

except KeyboardInterrupt:
    print ('Interrupted by User, closing file and cleaning up. PLease wait...')
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print ('You might get this error: Segmentation fault (core dumped)')



'''
To access the file:

import h5py
folder_path = 'Raw_Time_Series_Data'
hdf5_file_path = os.path.join(folder_path, 'tracking_data.h5')

# Open the HDF5 file
with h5py.File(hdf5_file_path, 'r') as file:
    # Access the dataset
    dataset = file['tracking_data']

    # Read and print the entire dataset
    data = dataset[:]
    print(data)

    # Optionally, convert to a pandas DataFrame for better visualization
    # import pandas as pd
    # df = pd.DataFrame(data, columns=['Date', 'Hour', 'Minute', 'Seconds', 'Track_ID', 'Object Class', 'X', 'Y'])
    # print(df)
'''
