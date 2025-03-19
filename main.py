import os.path

from shiftlab_ocr.doc2text.reader import Reader

from control.interface import Interface
from control.manager import Manager

manager = Manager()

interface = Interface()
interface.update()

reader = Reader()
manager.setDetector(reader.detector)
manager.setRecognizer(reader.recognizer)

startPressedFlag = False
processingInProgress = False
it = 1

while True:
    interface.update()

    if interface.startPressed != startPressedFlag:
        startPressedFlag = True
        manager.setScansArchivePath(interface.scansArchivePath)
        manager.unzipArchivePath(interface.outputDirectory)
        validation = manager.validateScans()
        interface.validateScans(validation)
        startPressedFlag = validation
        if not validation:
            manager.cleanScans()
            startPressedFlag = False
        else:
            processingInProgress = True
            manager.createDatasetDirectory()
            manager.makeImagesDir()
        interface.update()

    if processingInProgress:
        processingInProgress = manager.iterateScanProcessing(interface.textPath, interface.replaceLimit, interface)
        interface.updateProgressBar(len(manager.scanFileNames), it)
        interface.update()
        it += 1