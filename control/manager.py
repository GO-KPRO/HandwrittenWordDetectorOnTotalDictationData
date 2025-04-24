import os
import time
import shutil

import cv2

from base.scan import Scan


class Manager:
    def __init__(self, scansArchivePath, outputPath, textPath, datasetName, replacePercent, detector, recognizer):
        self.imagesPath = ''
        self.scansArchivePath = scansArchivePath
        self.outputPath = outputPath
        self.scansPath = ''
        self.datasetPath = ''
        self.curImgPath = ''
        self.scanFileNames = []
        self.textPath = textPath
        self.datasetName = datasetName
        self.detector = detector
        self.recognizer = recognizer
        self.currentScanNumber = 0
        self.replacePercent = replacePercent

    def createImagesDirectory(self):
        self.imagesPath = os.path.join(self.outputPath, 'images')
        os.makedirs(self.imagesPath, exist_ok=True)

    def createDatasetDirectory(self):
        self.datasetPath = os.path.join(self.outputPath, 'dataset')
        os.makedirs(self.datasetPath, exist_ok=True)

    def createCurrentImageDirectory(self):
        self.curImgPath = os.path.join(self.outputPath, 'currentImage')
        os.makedirs(self.curImgPath, exist_ok=True)

    def setScanFileNames(self):
        self.scansPath = os.path.join(self.outputPath, 'scans')
        self.scanFileNames = [os.path.join(self.scansPath, x) for x in os.listdir(self.scansPath)]

    def iterateProcessScan(self, currentScan, currentFileName, currentImageUpdated):
        scanFileName = self.scanFileNames[self.currentScanNumber]
        currentScan.value = self.currentScanNumber
        scanImagesPath = os.path.join(self.imagesPath, os.path.splitext(os.path.basename(scanFileName))[0])
        currentFileName[:len(os.path.basename(scanFileName))] = os.path.basename(scanFileName)
        os.makedirs(scanImagesPath, exist_ok=True)
        time.sleep(1)
        scan = Scan(scanFileName, scanImagesPath)  # Create scan object
        interfaceImagePath = os.path.join(self.curImgPath, 'currentImage.png')
        cv2.imwrite(interfaceImagePath, scan.images[0].image)
        currentImageUpdated.value = True

        scan.readText(self.textPath)

        scan.crop()

        scan.detection(self.detector)

        scan.recognition(self.recognizer)

        scan.align()

        scan.rateWords(self.replacePercent)

        scan.saveData(self.datasetPath, self.replacePercent)

        self.currentScanNumber += 1

        if self.currentScanNumber < len(self.scanFileNames):
            return True
        else:
            return False

    def endProcessing(self):
        shutil.make_archive(base_name=os.path.join(self.outputPath, self.datasetName), format='zip',
                            root_dir=os.path.join(self.outputPath, 'dataset'))
