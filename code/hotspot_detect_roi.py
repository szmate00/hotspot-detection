import os
import cv2
import h5py
import numpy as np
import pandas as pd
from scipy.signal import medfilt

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')

threshold = 2800
day = '20181002'
aeq = 'AEQ31'
path = f'data/W7-X/EDICAM/{aeq}/{day}'
    
with h5py.File(f'/{path}/{File}.h5', 'r') as hdf:
    roip = hdf.get('ROIP')
    roip1 = roip.get('ROIP1')
    roip1_data = roip1.get('ROIP1Data')
    roi1_average = roip1.get('ROIP1Average')

    med_range = 2 * (roip1_data.shape[2]//12) + 1
    roi1_medfilt = medfilt(roi1_average, med_range)

    # ROI1  
    frames1 = []
    List1 = []
    List21 = []
              
    # ROI2  
    frames2 = []
    List2 = []
    List22 = []

    # for each image in dataset
    for i in range(roip1_data.shape[2]):

        # sorting out faulty images
        if 1.3 * roi1_medfilt[i] < roi1_average[i]:
            
            frames1.append(0)
            List21.append(-1)
            List1.append(-1)
              
            frames2.append(0)
            List22.append(-1)
            List2.append(-1)

        else:
                    
            # NOTE: less time consuming to do the transformations only on the bigger ROI
            # then cutting the smaller one out of it ?
            # would have done the same transformations on them anyways
                               
            # ROI2 (bigger one)
            image2 = np.array(roip1_data[65:265, 440:595, i])

            # using median filter
            blur = cv2.medianBlur(image2, 3)

            # binarization
            thresh2 = cv2.threshold(blur, threshold, 4095, cv2.THRESH_BINARY)[1]
              
            # cutting the smaller one (ROI1) out
            thresh1 = np.array(roip1_data[90:240, 465:570, thresh2])
            
            # counting the nonzero pixel values in the images
            nzCount1 = cv2.countNonZero(thresh1)
            nzCount2 = cv2.countNonZero(thresh2)
   
                    
            # adding the number of the frames and binary value of hotspot to lists
              
            # IF RO1 and ROI2 pixels match:
            # adding number of nonzero pixels to predifined lists frames1 and frames2
            if nzCount1 == 0 or nzCount2 - nzCount1 != 0:
                List1.append(0)
                List21.append(0)
                frames1.append(0)
              
            else:
                List1.append(1)
                List21.append(1)
                frames1.append(nzCount1)
              
            if nzCount2 == 0 or nzCount2 - nzCount1 != 0:
                List2.append(0)
                List22.append(0)
                frames2.append(0)
              
            else:
                List2.append(1)
                List22.append(1)
                frames2.append(nzCount2)


# creating a pdf with plots
with PdfPages(f'/home/szucsmate/roi/{path[-8:]}/pdf/{m}.pdf') as pdf:
              
    plt.figure(figsize=(8.27, 11.69), dpi=100)
    plt.suptitle(f'{m} (threshold={threshold})', fontweight="bold", fontsize=15)
              
    plt.subplot(3, 1, 1)
    plt.plot(frames1, color='r', label='size of ROI1: 85x130')
    plt.title('ROI1', size=12)
    plt.xlabel('Frames', size=12)
    plt.ylabel('Number of pixels above threshold', size=12)
    ax = plt.gca()
    Ylim = ax.get_ylim()

    plt.subplot(3, 1, 2)
    plt.plot(frames2, color='g', label='size of ROI2: 135x180')
    plt.title('ROI2', size=12)
    plt.xlabel('Frames', size=12)
    plt.ylabel('Number of pixels above threshold', size=12)
    ax = plt.gca()
    ax.set_ylim(Ylim)
    
    plt.subplot(3, 1, 3)
    plt.plot(List21, color='r', label='ROI1')
    plt.plot(List22, color='g', label='ROI2')

    plt.title('Binary Classification', size=12)
    plt.xlabel('Frames', size=12)
    plt.ylabel('Hotspot', size=12)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    pdf.savefig()
    plt.close()
    
# saving binary hotspot classification to .csv
df = pd.DataFrame(List1, columns=["Hotspot"])
df.to_csv(f'/home/szucsmate/roi/{path[-8:]}/csv/{File}.csv', index=True)
