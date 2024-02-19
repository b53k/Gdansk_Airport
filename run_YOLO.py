from ultralytics import YOLO
import torch


'''This scrpt simply runs the YOLO model'''

#link = 'Data/Videos/6/Gdansk_Live_Stream_6.mp4'
#link = 'Data/08_11_2023/Frame_0.jpg'
link = 'https://62abe29de64ab.streamlock.net:4444/EPGD/pps3.stream/chunklist_w2096451211.m3u8'


# clear cache
#torch.cuda.empty_cache()

# Load the trained model (last epoch or best epoch)
model = YOLO('weights/1024.pt')

for result in model.track(source = link, show = True, 
                                conf = 0.7, save = False, 
                                line_width = 4, stream = True, 
                                persist = True, save_txt = False,
                                save_frames = False, show_labels = True, show_boxes = True):
    pass
