'''

@Máté Szűcs, 2021

'''

import numpy as np
import cv2
import h5py
import imutils
import pandas as pd
from scipy.signal import medfilt
import matplotlib.pyplot as plt


def hotspot_universal(shot_num, port, frame_num=None):
    '''
    Find hotspots in the images of the EDICAM camera system.
    Using EDICAM data located on BEAM, in hdf5 filetype.
    
    Currently works only on ports ending with 1, e.g. AEQX1.
    
    Under heavy construction!
    
    shot_num: Identifier of the discharge using format: YYYYMMDD_XXX_XXXXXX, e.g. 20180801_025_142543
    port: Port number of the camera using format: AEQXX, e.g. AEQ31
    frame_num: None to analyze the whole discharge, int type value to only analyze one frame
    
    returns: - IF one frame: Image with hotspots marked
             - IF whole shot: .csv file containg number of hotspots found in given frame and the coordinates of their centers
    
    TODO: - changeable threshold maybe
          - make it work on other ports
          - divertor problems
    '''
    
    with h5py.File(f'/data/W7-X/EDICAM/{port}/{shot_num[:8]}/{port}_edi_{shot_num}.h5', 'r') as hdf:
        roip = hdf.get('ROIP')
        roip1 = roip.get('ROIP1')
        roip1_data = roip1.get('ROIP1Data')
        roi1_average = roip1.get('ROIP1Average')

        med_range = 2 * (roip1_data.shape[2]//12) + 1
        roi1_medfilt = medfilt(roi1_average, med_range)

        if frame_num != None:
            if type(frame_num) != int:
                raise ValueError('frame_num must be an integer!')

            else:
                image0 = np.array(roip1_data[:1280, :1024, frame_num])
                image_blurred = cv2.medianBlur(image0, 5)

                top = cv2.morphologyEx(image_blurred, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(70,70)))

                top[350:700, 610:1024] = 0

                if (np.max(top) + np.min(top)) / 2 > 1300:
                    thresh_val = (np.max(top) + np.min(top)) / 2

                else:
                    thresh_val = 1300

                thresh = cv2.threshold(top, 0.9 * thresh_val, 4095, cv2.THRESH_BINARY)[1]

                thresh = cv2.convertScaleAbs(thresh, alpha=(255.0/4095.0))

                cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                image = cv2.convertScaleAbs(image0, alpha=(255.0/4095.0))
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

                for (i,c) in enumerate(cnts):
                    cv2.drawContours(image, [c], -1, (255, 0, 0), 2)

                print('Number of hotspots found:', len(cnts))

                plt.figure(figsize=(14,8))

                plt.subplot(121)
                plt.imshow(image0, cmap='gray')
                plt.title('ORIGINAL IMAGE', size=15)
                plt.axis('off')

                plt.subplot(122)
                plt.imshow(image, cmap='gray')
                plt.title('HOTSPOTS', size=15)
                plt.axis('off')

                plt.tight_layout()
                plt.show()

        else:
            nums = []
            coords = []

            for i in range(roip1_data.shape[2]):

                if 1.3 * roi1_medfilt[i] < roi1_average[i]:
                    nums.append(0)
                    coords.append(0)

                else:

                    image0 = np.array(roip1_data[:1280, :1024, i])

                    image_blur = cv2.medianBlur(image0, 5)

                    top = cv2.morphologyEx(image_blur, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(70,70)))

                    top[350:700, 610:1024] = 0


                    if (np.max(top) + np.min(top)) / 2 > 1300:

                        thresh_val = (np.max(top) + np.min(top)) / 2

                    else:

                        thresh_val = 1300

                    thresh = cv2.threshold(top, 0.9 * thresh_val, 4095, cv2.THRESH_BINARY)[1]
                    thresh = cv2.convertScaleAbs(thresh, alpha=(255.0/4095.0))

                    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    centers = []

                    nums.append(len(cnts))

                    for c in cnts:
                        M = cv2.moments(c)

                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                        else:
                            cX, cY = 0, 0
                            
                        centers.append([cX, cY])
                    
                    if len(cnts) == 0:
                        coords.append(0)
                    else:
                        coords.append(centers)

            df = pd.DataFrame({'Frame': np.arange(roip1_data.shape[2]),
                                   'Number of hotspots': nums, 'Position of hotspots': coords})

            df.to_csv(f'{shot_num}.csv', index=False)