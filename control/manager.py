import os
import zipfile
import shutil

from base.scan import Scan


class Manager:
    def __init__(self):
        self.imagesPath = ''
        self.scansArchivePath = ''
        self.outputPath = ''
        self.scansPath = ''
        self.datasetPath = ''
        self.scanFileNames = []
        self.scans = []
        self.text = ''
        self.detector = None
        self.recognizer = None
        self.currentScan = 0

    def makeImagesDir(self):
        self.imagesPath = os.path.join(self.outputPath, 'images')
        os.makedirs(self.imagesPath, exist_ok=True)

    def createDatasetDirectory(self):
        self.datasetPath = os.path.join(self.outputPath, 'dataset')
        os.makedirs(self.datasetPath, exist_ok=True)

    def setScansArchivePath(self, path):
        self.scansArchivePath = path

    def unzipArchivePath(self, path):
        self.outputPath = path
        self.scansPath = os.path.join(path, 'scans')
        os.makedirs(self.scansPath, exist_ok=True)
        with zipfile.ZipFile(self.scansArchivePath, 'r') as zip_ref:
            zip_ref.extractall(self.scansPath)

    def validateScans(self) -> bool:
        self.scanFileNames = [os.path.join(self.scansPath, x) for x in os.listdir(self.scansPath)]
        for scanFileName in self.scanFileNames:
            filePath, fileExtension = os.path.splitext(scanFileName)
            if fileExtension != '.pdf':
                print(f'Error: file {scanFileName} has wrong extension')
                return False
        return True

    def cleanScans(self):
        shutil.rmtree(self.scansPath)

    def setDetector(self, detector):
        self.detector = detector

    def setRecognizer(self, recognizer):
        self.recognizer = recognizer

    def processScan(self, scanFileName, textPath, replacePercent, interface):
        scansImagesPath = os.path.join(self.imagesPath, os.path.splitext(os.path.basename(scanFileName))[0])
        interface.updateCurrentFileLabel(os.path.basename(scanFileName))
        interface.update()
        os.makedirs(scansImagesPath, exist_ok=True)
        scan = Scan(scanFileName, scansImagesPath)
        self.scans.append(scan)  # Create scan object

        interface.updateCurrentImage(scan.images[0].path)
        interface.update()

        scan.readText(textPath)

        scan.crop()

        scan.detection(self.detector)

        scan.recognition(self.recognizer)

        scan.align()

        scan.rateWords(replacePercent)

        scan.saveData(self.datasetPath, replacePercent)

    def iterateScanProcessing(self, textPath, replacePercent, interface):
        self.processScan(self.scanFileNames[self.currentScan], textPath, replacePercent, interface)
        self.currentScan += 1
        if self.currentScan < len(self.scanFileNames):
            return True
        else:
            return False
