from paddleocr import PaddleOCR, draw_ocr
import os,glob,csv,math,json,re,math,cv2,slideio,logging, shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from IPython.display import display, HTML
from fuzzywuzzy import fuzz
from tqdm import tqdm

# Setup model
ocr_model = PaddleOCR(lang='en',use_angle_cls = False,show_log=False)

import logging
from ppocr.utils.logging import get_logger as ppocr_get_logger
ppocr_get_logger().setLevel(logging.ERROR)

# Open our folder and list the number of files inside
folder_name,type = 'A21-052','svs' # Specify the folder name (first param) and file type (second param)
folder = glob.glob(f"{folder_name}/*.{type}")
print(f"{len(folder)} {type} files identified.")
# Create the 'failed' folder if it doesn't exist
failed_folder = os.path.join(os.path.dirname(os.path.abspath(folder_name)), folder_name, 'failed')
os.makedirs(failed_folder, exist_ok=True)

def move_to_failed_folder(file, folder):
    failed_file = os.path.join(failed_folder, os.path.basename(file))
    shutil.move(file, failed_file)    
    
columns = ['participant_id', 'stain_id', 'brain_region','label']
csv_filename = f"{folder_name}.csv"  # Change this to your desired file name

with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(columns)

label_count = 0
failed_count = 0
good = True

while good == True:
    for file in tqdm(folder):
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
                result = ocr_model.ocr(rotated_image) # Process rotated image with Paddle
                good = True
                # Build a list containing all chunks identified by Paddle
                text_list = []

                for result_group in result:

                    for text_region in result_group:
                        text, confidence = text_region[1]  # Extract text and confidence
                        # print("Text:", text); print("Confidence:", confidence)
                        text_list.append(text)
                        # Coordinates are stored in text_region[0] if needed

                garbage = ['starfrost', 'adrc']  # Clean the result a little
                text_list = [thing for thing in text_list if thing.lower() not in garbage]
                logging.info(f"The current text list is: {text_list}. If empty, this will fail later.")

                try:
                    # Phase 1: Gather the Participant ID:
                    logging.info("Starting Phase 1")
                    participant_pattern = r'([A-Z0-9]{3})-([A-Z0-9]{3})'
                    participant_matches = [re.search(participant_pattern, i) for i in text_list if re.search(participant_pattern, i)]
                    participant_id = [match[0] for match in participant_matches]
                    participant_id = participant_id[0]; print(f"Participant ID: {participant_id}")
                except Exception as e:
                    logging.critical("Error in phase 1")
                    logging.error(f"An exception occurred while processing file: {file}")
                    logging.error(f"Exception details: {e} Participant ID")
                    good = False
                    move_to_failed_folder(file, failed_folder); failed_count += 1
                    continue

                try:
                    # Phase 2: Gather the Stain ID:
                    logging.info("Starting Phase 2")
                    predefined_choices = ['LB509', 'HE', 'PHF-1', 'TDP-43', '10D5','pSYN'] # Stain Choices
                    stain_id = None
                    best_similarity = 0
                    for i in text_list:
                        for choice in predefined_choices:
                            similarity = fuzz.ratio(i, choice)  # Calculate Lebenshtein distance
                            if similarity > best_similarity:
                                best_similarity = similarity
                                stain_id = choice
                    print(f"Stain ID: {stain_id}")
                except Exception as e:
                    logging.critical("Error in phase 2")
                    logging.error(f"An exception occurred while processing file: {file}")
                    logging.error(f"Exception details: {e} (Stain ID)")
                    good = False
                    move_to_failed_folder(file, failed_folder); failed_count += 1
                    continue

                try:
                    # Phase 3: Gather the Brain Region ID:
                    logging.info("Starting Phase 3")
                    brain_region_pattern = r'\bL\d+[A-Z]?\b'
                    brain_region_matchs = [re.search(brain_region_pattern, i) for i in text_list if re.search(brain_region_pattern, i)]
                    brain_region = [match[0] for match in brain_region_matchs]
                    brain_region = brain_region[0]; print(f"Brain region match: {brain_region}")
                except Exception as e:
                    logging.critical("Error in phase 3")
                    logging.error(f"An exception occurred while processing file: {file}")
                    logging.error(f"Exception details: {e} (Brain Region)")
                    good = False
                    move_to_failed_folder(file, failed_folder); failed_count += 1
                    continue

                # Phase 4 Print Results:
                logging.info("Starting Phase 4")
                if good == True:
                    label_count += 1
                    # Write the rows to the CSV file
                    with open(f'{folder_name}.csv', mode='a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        label = f"{participant_id}_{brain_region}_{stain_id}"
                        csv_writer.writerow([participant_id, stain_id, brain_region, label])
                    # Phase 5 Rename Each File:
                    new_name = os.path.join(os.path.dirname(file), label + ".svs")
                    os.rename(file, new_name)
                    logging.info("Finished Phase 4. Beginning new loop.")
                    
    break # Kill the loop after 1 file.
# Print Summary
print(f"Successfully processed {label_count} files. Moved {failed_count} files to the 'failed' folder.")
