# Plot data in real time.
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# path to HDF5 file
folder_path = 'Raw_Time_Series_Data'
hdf5_file_path = os.path.join(folder_path, 'tracking_data.h5')

def read_hdf5_data():
    '''
    Reads the latest data from the HDF5 file
    '''
    with h5py.File(hdf5_file_path, 'r', swmr = True) as file:
        if 'tracking_data' in file:
            data = file['tracking_data'][:]
        else:
            data = np.array([])
    
    return data

# Setup the plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (10, 8))

def update_plot(frames):
    '''
    Update the Plot with new data
    '''
    data = read_hdf5_data()
    if data.size > 0:
        # Filter data with obj_class corresponding to 0,1,4,7
        classes_of_interest = [0,1,4,7]
        id_of_interest = [8, 12, 17, 18]      # Remove
        filtered_data = data[np.isin(data[:,6], classes_of_interest)]
        filtered_data = filtered_data[np.isin(filtered_data[:,5], id_of_interest)]    #Remove

        # Clear current axes
        ax1.clear()
        ax2.clear()

        # Set limits & labels
        ax1.set_xlabel('Time')
        ax1.set_ylabel('X-Coordinate')
        #ax1.set_xlim(0,1)
        #ax1.set_ylim(0, 640)

        ax2.set_xlabel('Time')
        ax2.set_ylabel('Y-Coordinate')
        #ax2.set_xlim(0,1)
        #ax2.set_ylim(0, 640)

        dictionary = {'0': 'Aircraft', '1': 'Airport_Tractor', '4': 'Fuel Truck', '7': 'Pushback Tug'}

        # Plot each object class
        for obj_class in classes_of_interest:
            class_data = filtered_data[filtered_data[:, 6] == obj_class]    # Get only the instances with a specific class o or 1 or 4 or 7
            # Time vs x-coordinate
            if class_data.size > 0:
                if obj_class == 0:
                    id = 8
                elif obj_class == 4:
                    id = 12
                elif obj_class == 1:
                    id = 17

                ax1.plot(class_data[:, 4], class_data[:,7], label = f'ID: {str(id)} {dictionary[str(obj_class)]}', linewidth = 0.9, alpha = 0.5)
                ax2.plot(class_data[:, 4], class_data[:,8], label = f'ID: {str(id)} {dictionary[str(obj_class)]}', linewidth = 0.9, alpha = 0.5)

        # Add legends
        ax1.legend(loc = 'upper left')
        ax2.legend(loc = 'upper left')

        plt.tight_layout()


# start animation
ani = FuncAnimation(fig, update_plot, frames = 15, interval = 1000)  # update every 0.5 seconds
plt.show()
