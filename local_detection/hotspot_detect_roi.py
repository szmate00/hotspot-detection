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

threshold = 3000
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
    pixel_sum = []
    binary = []

    # for each image in dataset
    for i in range(roip1_data.shape[2]):

        # sorting out faulty images
        if 1.3 * roi1_medfilt[i] < roi1_average[i]:
            
            pixel_sum.append(0)
            binary.append(-1)

        else:
                               
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
                pixel_sum.append(0)
                binary.append(0)
              
            else:
                binary.append(1)
                pixel_sum.append(nzCount1)

# creating a pdf with plots
with PdfPages(f'/home/szucsmate/roi/{path[-8:]}/pdf/{m}.pdf') as pdf:
              
    plt.figure(figsize=(8.27, 11.69), dpi=100)
    plt.suptitle(f'{m} (threshold={threshold})', fontweight="bold", fontsize=15)
              
    plt.subplot(2, 1, 1)
    plt.plot(pixel_sum, color='r')
    plt.title('Hotspot size', size=12)
    plt.xlabel('Frames', size=12)
    plt.ylabel('Number of pixels above threshold', size=12)
    ax = plt.gca()
    Ylim = ax.get_ylim()

    plt.subplot(2, 1, 3)
    plt.plot(binary, color='r')
    plt.title('Binary Classification', size=12)
    plt.xlabel('Frames', size=12)
    plt.ylabel('Hotspot', size=12)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    pdf.savefig()
    plt.close()
    
# saving binary hotspot classification to .csv
df = pd.DataFrame(binary, columns=["Hotspot"])
df.to_csv(f'/home/szucsmate/roi/{path[-8:]}/csv/{File}.csv', index=True)
