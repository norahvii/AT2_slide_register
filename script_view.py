import slideio
import pytesseract
import os,glob,csv,math,json,re,math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from IPython.display import display, HTML
from fuzzywuzzy import fuzz
from utils import show_images

# Open our folder and list the number of files inside
folder_name,type = 'A20-099','svs' # Specify the folder name (first param) and file type (second param)
folder = glob.glob(f"{folder_name}/*.{type}")
print(f"{len(folder)} {type} files identified.")

columns = ['participant_id', 'stain_id', 'brain_region','label']
csv_filename = f"{folder_name}.csv"  # Change this to your desired file name

with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(columns)

label_count = 0

for file in folder:
    slide = slideio.open_slide(file)
    scene = slide.get_scene(0)
    # print(scene)
    # This part gets the image per slide
    image_names = slide.get_aux_image_names()
    images = []
    for name in image_names:
        if name == 'Label':
            image = slide.get_aux_image_raster(name)
            images.append(image)  
            rotated_image = np.rot90(image, k=-1) # Capture a rotated image of the label
            image_text = pytesseract.image_to_string(rotated_image)
            lines = image_text.split('\n')
            for line in lines:
                # Pattern for matching participant ID
                participant_pattern = r'([A-Z0-9]{3})-([A-Z0-9]{3})'
                # Pattern for matching brain regions
                brain_region_pattern = r'\bL\d+[A-Z]?\b'

                participant_match = re.search(participant_pattern, line)
                if participant_match:
                    participant_id = participant_match[0]

                # Brain Region Matches
                brain_region_match = re.search(brain_region_pattern, line)
                if brain_region_match:
                    brain_region = brain_region_match[0]

                # Check top right quadrent for stain
                height, width, _ = rotated_image.shape
                top_right_quadrant = rotated_image[:height//2, width//2:]
                quadrent = pytesseract.image_to_string(top_right_quadrant)
                quadrent_lines = quadrent.split('\n')
                predefined_choices = ['LB509','HE','PHF-1','TDP-43','10D5']
                # Initialize variables to store the best match and its similarity score
                stain_id = None
                best_similarity = 0
                for line in quadrent_lines:
                    for choice in predefined_choices:
                        similarity = fuzz.ratio(line, choice)  # Calculate Lebenshtein distance
                        if similarity > best_similarity:
                            best_similarity = similarity
                            stain_id = choice
            
            label_count += 1      
            print(f"------------------ files parsed: {label_count}")
            print(f"Found Participant ID: {participant_id}")
            print(f"Found Brain Region: {brain_region}")
            print(f"Found Stain ID: {stain_id}")

            with open(f'{folder_name}.csv', mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                label = f"{participant_id}_{brain_region}_{stain_id}"
                csv_writer.writerow([participant_id, stain_id, brain_region, label])

