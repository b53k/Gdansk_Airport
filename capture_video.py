import subprocess
from multiprocessing import Process, freeze_support
import os
from datetime import datetime, timedelta
import csv
import glob
import argparse

'''
This script captures live stream video/image frames and stores them in Data/{Current Date}/ (PPS3 or WestPier)
Each sub-folder contains videos and images along with csv file that keeps track of each image frame and its corresponding time-stamp
'''

def parse_arguments():
    '''
        Command Line Argument Parser
    '''
    parser = argparse.ArgumentParser('Capture Live Videos/Image Frames')

    # Arguments
    parser.add_argument('--frame_interval', type = int, default = 10, help = 'Extract frames every (FRAME_INTERVAL) seconds, default = 10')
    parser.add_argument('--record_duration', type = int, default = 60, help = 'Specify the length of recording in seconds, default = 60')

    args = parser.parse_args()
    return args


def capture_video(chunklist_url, duration, video_file_path):
    '''
        Run video capture process
    '''
    command = [
        'ffmpeg',
        '-i', chunklist_url,
        '-t', str(duration),
        '-c:v', 'copy', video_file_path
    ]

    subprocess.run(command)
    

def capture_frames(chunklist_url, duration, frame_interval, frame_output_path, start_number):
    '''
        Run Image Frame capture process
    '''
    command = [
        'ffmpeg',
        '-i', chunklist_url,
        '-t', str(duration),
        '-vf', f'fps=1/{frame_interval}', 
        '-start_number', str(start_number),
        frame_output_path
    ]

    subprocess.run(command)


def setup_and_record(url, output_folder, args, processes):

    output_filename = f'{os.path.basename(output_folder)}_Live_stream.mp4'

    # Continuing/Starting number for Frame ID
    existing_frames = glob.glob(os.path.join(output_folder, 'Frame_*.jpg'))
    existing_indices = [int(os.path.splitext(os.path.basename(frame))[0].split('_')[1]) for frame in existing_frames]

    global start_number
    start_number = max(existing_indices, default = -1) + 1 # start from the next index
    

    # Add new video file everytime this routine is called
    existing_videos = glob.glob(os.path.join(output_folder, output_filename.rsplit('.', 1)[0] + '_*.mp4'))
    existing_indices = [int(os.path.splitext(os.path.basename(video))[0].rsplit('_', 1)[1]) for video in existing_videos]
    next_index = max(existing_indices, default=-1) + 1
    

    # Construct ffmpeg command for video and frame capture
    base_filename = output_filename.rsplit('.', 1)[0]
    video_file_path = os.path.join(output_folder, f'{base_filename}_{next_index}.mp4')
    frame_output_path = os.path.join(output_folder, 'Frame_%d.jpg')

    video_process = Process(target = capture_video, args = (url, args.record_duration, video_file_path), daemon = True)
    frame_process = Process(target = capture_frames, args = (url, args.record_duration, args.frame_interval, frame_output_path, start_number), daemon = True)

    video_process.start()
    frame_process.start()

    # Store process references in a list for later joining
    processes.extend([video_process, frame_process])



def record_stream(args, url_folders_dict):
    # Create a directory with the current date and time in GMT+1
    date_format = '%d_%m_%Y'
    current_time = datetime.utcnow() + timedelta(hours=1)
    folder_name = current_time.strftime(date_format)
    video_folder = os.path.join('Data', folder_name)
    os.makedirs(video_folder, exist_ok = True)

    processes = []
    for url, subfolder_name in url_folders_dict.items():
        if url:
            output_folder = os.path.join(video_folder, subfolder_name)
            os.makedirs(output_folder, exist_ok = True)
            setup_and_record(url, output_folder, args, processes)

    # Join all processes after completion
    for process in processes:
        process.join()

    # Deferred logging: reduces I/O operations during recording
    for url, subfolder_name in url_folders_dict.items():
        if url:
            output_folder = os.path.join(video_folder, subfolder_name)
            csv_file = os.path.join(output_folder, 'frame_infos.csv')


            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline = '') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'HH', 'MM', 'SS', 'FrameID'])

            
            # Continuing/Starting number for Frame ID
            existing_frames = glob.glob(os.path.join(output_folder, 'Frame_*.jpg'))
            existing_indices = [int(os.path.splitext(os.path.basename(frame))[0].split('_')[1]) for frame in existing_frames]

            # Calculate frame timestamps and write to CSV
            frame_prefix = 'Frame'
            num_frames = args.record_duration // args.frame_interval

            with open(csv_file, 'a', newline = '') as file:
                writer = csv.writer(file)
                for i in range(start_number, max(existing_indices)+1):
                    frame_time = current_time + timedelta(seconds = (i-start_number) * args.frame_interval)
                    writer.writerow([
                        frame_time.strftime('%d-%m-%y'),
                        frame_time.strftime('%H'),
                        frame_time.strftime('%M'),
                        frame_time.strftime('%S'),
                        f'{frame_prefix}_{i}.jpg'
                    ])


if __name__ == '__main__':
    freeze_support()            # For Windows support
    args = parse_arguments()
    pps3_url = 'https://62abe29de64ab.streamlock.net:4444/EPGD/pps3.stream/chunklist_w2096451211.m3u8'
    westpier_url = 'https://62abe29de64ab.streamlock.net:4444/EPGD/pirs2.stream/chunklist_w1496307832.m3u8'

    # You can set either of the URL's to None if you don't require capturing both live stream
    # e.g. url_dict = {pps3_url: 'PPS3, None: 'WestPier}
    url_dict = {pps3_url: 'PPS3', None: 'WestPier'}

    record_stream(args, url_dict)
