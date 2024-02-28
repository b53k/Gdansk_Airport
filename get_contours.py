'''
This script processes an image using the YOLOv8 segmentation model to detect objects and their corresponding masks. 
For each detected object, it identifies the largest contour of the mask and normalizes the contour coordinates relative 
to the image dimensions. These normalized coordinates, along with the class ID of the detected object, are then written 
to a text file. The output text file has the same base name as the input image but with a `.rf.txt` extension. Each line in 
the text file represents a detected object instance, starting with the class ID followed by the normalized coordinates 
of the largest contour of the object's mask. This format is designed to be compatible with the YOLOv8 segmentation model 
requirements for annotated data.

Parameters:
- image_filename (str): The filename of the image to be processed. This script assumes the image and its corresponding 
  prediction results (e.g., masks, class IDs) are already available through the YOLOv8 model's output. 
  NOTE: You need to change the original image filename to include '.rf.jpg' extension. 
  e.g. Frame_1.jpg ---> Frame_1.jpg.rf.jpg

Output:
- A `.txt` file named after the input image, containing the class IDs and normalized contour coordinates of the detected 
  objects' largest masks. This file is saved in the same directory as the script.
  e.g. Frame_1.jpg.rf.txt.
  Output is stored in 'Annoations' Folder

Usage: 
- Make a folder 'Annotations' store images with extension .rf.jpg. Call this module to generate contour plots. Make sure no image file has same name.
'''

import os
import numpy as np
import cv2
from ultralytics import YOLO

def annotate_image(image_path, model_weight):
    '''
    image_path --> e.g. 'Data/Frame_1.jpg.rf.jpg'
    model_weight --> e.g. 'weights/xxx.pt' 
    '''
    annotations_dir = 'Annotations'

    #if not os.path.exists(annotations_dir):
    #    os.makedirs(annotations_dir)

    txt_rename = os.path.split(image_path)[1][:-7] + '.rf.txt'
    txt_filename = os.path.join(annotations_dir, txt_rename)

    # Load Model
    model = YOLO(model_weight)

    for result in model.predict(source = image_path, show = False,
                                conf = 0.8, save = False,
                                line_width = 4, save_txt = False,
                                show_labels = False, show_boxes = False):
        pass

    
    # Get all class IDs
    classes = (result.boxes.cls).detach().cpu()


    with open(txt_filename, 'w') as file:
        for i in range(len(classes)):
            class_id = int(classes[i].item())
            mask = result.masks[i].data.detach().cpu().squeeze()

            mask = 255 * mask.numpy()
            mask = mask.astype(np.uint8)

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            image_height, image_width = mask.shape

            if len(contours) > 1:
                max_area = 0 
                max_index = -1

                for j, contr in enumerate(contours):
                    area = cv2.contourArea(contr)

                    if area > max_area:
                        max_area = area
                        max_index = j

                largest_contour = contours[max_index] if max_index != 1 else None
            elif len(contours) == 1:
                largest_contour = contours[0]
            else:
                largest_contour = None

            if largest_contour is not None and len(contours) > 0:
                
                # Normalize largest_contours
                largest_contour = largest_contour.astype(np.float32)
                largest_contour[:,0,0] = largest_contour[:,0,0] / image_width
                largest_contour[:,0,1] = largest_contour[:,0,1] / image_height

                # Prepare a line to write to the file: class_id followed by normalized coordinates
                line = f'{class_id} ' + ' '.join([f'{x[0][0]} {x[0][1]}' for x in largest_contour])

                # Write
                file.write(line + '\n')