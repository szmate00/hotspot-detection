from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import h5py
from matplotlib import pyplot as plt
import cv2
import pandas as pd
from scipy.signal import medfilt
import os
from PyPDF2 import PdfFileMerger
plt.style.use('seaborn-whitegrid')


# list consisting the name of folders to be processed, each folder contains the given day's data files
days = ['20181018']

for day in days:

    threshold = 2800
    Files = []
    # censored path on github
    path = ''
    pdfs = []
    merger = PdfFileMerger()

    # searching path directory for the right files to analyse
    for file in [f for f in os.listdir(f'/{path}') if not f.endswith(('down.h5', '.dat', '.tif', '.filepart'))]:
        Files.append(file.replace('.h5', ''))

    Files = sorted(Files)

    # crrating folders for the outputs
    os.makedirs(f'/home/szucsmate/roi/{path[-8:]}')
    os.makedirs(f'/home/szucsmate/roi/{path[-8:]}/pdf')
    os.makedirs(f'/home/szucsmate/roi/{path[-8:]}/csv')

    # going through each data file
    for m in Files:

        with h5py.File(f'/{path}/{m}.h5', 'r') as hdf:
            roip = hdf.get('ROIP')
            roip1 = roip.get('ROIP1')
            roip1_data = roip1.get('ROIP1Data')
            roi1_average = roip1.get('ROIP1Average')

            # calculating the right size of median filter for each file
            med_range = 2 * (roip1_data.shape[2]//3) + 1
            roi1_medfilt = medfilt(roi1_average, med_range)

            frames1 = []
            List1 = []
            List21 = []

            # ROI1
            for i in range(roip1_data.shape[2]):

                # sorting out faulty frames
                if 1.3*roi1_medfilt[i] < roi1_average[i]:

                    frames1.append(0)
                    List21.append(-1)
                    List1.append(-1)

                else:

                    image1 = np.array(roip1_data[90:240, 465:570, i])

                    # using median filter
                    blur1 = cv2.medianBlur(image1, 1)

                    # binarization
                    thresh1 = cv2.threshold(blur1, threshold, 4095, cv2.THRESH_BINARY)[1]

                    # counting the nonzero pixel values in the image
                    nzCount1 = cv2.countNonZero(thresh1)

                    # adding number of nonzero pixels to predifined list
                    frames1.append(nzCount1)

                    # adding the number of the frames and binary value of hotspot to
                    if nzCount1 == 0 or nzCount1/15750 > 0.15:
                        List1.append(0)
                        List21.append(0)
                    else:
                        List1.append(1)
                        List21.append(1)

            frames2 = []
            List2 = []
            List22 = []

            # ROI2
            for j in range(roip1_data.shape[2]):

                # sorting out faulty frames
                if 1.3*roi1_medfilt[j] < roi1_average[j]:

                    frames2.append(0)
                    List22.append(-1)
                    List2.append(-1)

                else:

                    image2 = np.array(roip1_data[65:265, 440:595, j])

                    # using median filter
                    blur2 = cv2.medianBlur(image2, 1)

                    # binarization
                    thresh2 = cv2.threshold(blur2, threshold, 4095, cv2.THRESH_BINARY)[1]

                    # counting the nonzero pixel values in the image
                    nzCount2 = cv2.countNonZero(thresh2)

                    # adding number of nonzero pixels to predifined list
                    frames2.append(nzCount2)

                    # adding the number of the frames and binary value of hotspot to
                    if nzCount2 == 0 or nzCount2/15750 > 0.15:
                        List2.append(0)
                        List22.append(0)
                    else:
                        List2.append(1)
                        List22.append(1)

        # creating a pdf with plots
        with PdfPages(f'/home/szucsmate/roi/{path[-8:]}/pdf/{m}.pdf') as pdf:
            plt.figure(figsize=(8.27, 11.69), dpi=100)
            plt.suptitle(f'{m} (threshold={threshold})', fontweight="bold", fontsize=15)
            plt.subplot(3, 1, 1)
            plt.plot(frames1, color='r', label='size of ROI1: 85x130')
            plt.title('ROI1', size=12)
            plt.xlabel('Frames', size=12)
            plt.ylabel('Number of pixels above threshold', size=12)
            plt.legend(loc='upper right', fontsize=12, handlelength=0, handletextpad=0, frameon=True)
            ax = plt.gca()
            Ylim = ax.get_ylim()

            plt.subplot(3, 1, 2)
            plt.plot(frames2, color='g', label='size of ROI2: 135x180')
            plt.title('ROI2', size=12)
            plt.xlabel('Frames', size=12)
            plt.ylabel('Number of pixels above threshold', size=12)
            plt.legend(loc='upper right', fontsize=12, handlelength=0, handletextpad=0, frameon=True)
            ax = plt.gca()
            ax.set_ylim(Ylim)

            plt.subplot(3, 1, 3)
            plt.plot(List21, color='r', label='ROI1')
            plt.plot(List22, color='g', label='ROI2')

            plt.title('Binary Classification', size=12)
            plt.xlabel('Frames', size=12)
            plt.ylabel('Hotspot', size=12)
            plt.legend(loc='upper right', fontsize=12, frameon=True)

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])

            pdf.savefig()
            plt.close()

            pdfs.append(f'/home/szucsmate/roi/{path[-8:]}/pdf/{m}.pdf')

            # saving binary hotspot classification to .csv
            df = pd.DataFrame(List1, columns=["Hotspot"])
            df.to_csv(f'/home/szucsmate/roi/{path[-8:]}/csv/{m}.csv', index=True)

    # creating a merged pdf containing all the the pdfs for the data files in the given folder
    for pdf in pdfs:
        merger.append(pdf)

    merger.write(f"/home/szucsmate/roi/{path[-8:]}/{path[-8:]}.pdf")
    merger.close()
