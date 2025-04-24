import multiprocessing as mp
import os
import shutil
import zipfile
from ctypes import c_bool

from shiftlab_ocr.doc2text import Reader

from control.interface import Interface
from control.manager import Manager


def processing(pathsReady, scansArchivePath, outputPath, textPath, datasetName, replacePercent, currentScan, totalScans,
               inProcess, currentFileName, currentImageUpdated, processEnded, destroyProcess, repeat):
    reader = Reader()
    while not pathsReady.value:
        if destroyProcess.value:
            return
        pass
    scansArchivePathString = ''.join(scansArchivePath[:]).strip()
    outputPathString = ''.join(outputPath[:]).strip()
    textPathString = ''.join(textPath[:]).strip()
    datasetNameString = ''.join(datasetName[:]).strip()
    manager = Manager(scansArchivePathString, outputPathString, textPathString, datasetNameString,
                      replacePercent.value, reader.detector, reader.recognizer)
    manager.createDatasetDirectory()
    manager.createCurrentImageDirectory()
    manager.createImagesDirectory()
    manager.setScanFileNames()
    totalScans.value = len(manager.scanFileNames)

    endFlag = False
    while inProcess.value and not endFlag:
        endFlag = not manager.iterateProcessScan(currentScan, currentFileName, currentImageUpdated)
    #if endFlag:
        #repeat.value = True
    manager.endProcessing()
    processEnded.value = True


def unzipArchivePath(scansArchivePath, outputPath):
    scansPath = os.path.join(outputPath, 'scans')
    os.makedirs(scansPath, exist_ok=True)
    with zipfile.ZipFile(scansArchivePath, 'r') as zip_ref:
        zip_ref.extractall(scansPath)


def validateScans(outputPath):
    scansPath = os.path.join(outputPath, 'scans')
    scanFileNames = [os.path.join(scansPath, x) for x in os.listdir(scansPath)]
    for scanFileName in scanFileNames:
        filePath, fileExtension = os.path.splitext(scanFileName)
        if fileExtension != '.pdf':
            print(f'Error: file {scanFileName} has wrong extension')
            return False
    return True


def cleanScans(outputPath):
    scansPath = os.path.join(outputPath, 'scans')
    shutil.rmtree(scansPath)


if __name__ == '__main__':

    repeat = mp.Value(c_bool, True)

    while repeat.value:
        repeat.value = False
        pathsReady = mp.Value(c_bool, False)
        destroyProcess = mp.Value(c_bool, False)
        scansArchivePath = mp.Array('u', [' ' for i in range(1000)])
        outputPath = mp.Array('u', [' ' for i in range(1000)])
        textPath = mp.Array('u', [' ' for i in range(1000)])
        datasetName = mp.Array('u', [' ' for i in range(1000)])
        replacePercent = mp.Value('d', 0.)

        currentScan = mp.Value('i', 0)
        totalScans = mp.Value('i', 0)
        currentFileName = mp.Array('u', [' ' for i in range(1000)])
        currentImageUpdated = mp.Value(c_bool, False)

        inProcess = mp.Value(c_bool, False)
        processEnded = mp.Value(c_bool, False)

        interface = Interface()

        process = mp.Process(target=processing, args=[pathsReady, scansArchivePath, outputPath, textPath, datasetName,
                                                      replacePercent, currentScan, totalScans, inProcess,
                                                      currentFileName,
                                                      currentImageUpdated, processEnded, destroyProcess, repeat])

        process.start()

        while True:
            if interface.startPressed:
                unzipArchivePath(interface.scansArchivePath, interface.outputDirectory)
                if validateScans(interface.outputDirectory):
                    interface.validateScans(True)
                    inProcess.value = True
                    scansArchivePath[:len(interface.scansArchivePath)] = list(interface.scansArchivePath)
                    outputPath[:len(interface.outputDirectory)] = list(interface.outputDirectory)
                    textPath[:len(interface.textPath)] = list(interface.textPath)
                    datasetName[:len(interface.datasetNameEntry.get())] = list(interface.datasetNameEntry.get())
                    replacePercent.value = interface.replaceLimit
                    pathsReady.value = True
                else:
                    interface.validateScans(False)
                    cleanScans(interface.outputDirectory)

            if interface.destroyAll:
                destroyProcess.value = True

            if interface.endPressed:
                inProcess.value = False
                interface.endPressed = False

            if processEnded.value:
                interface.showSaveInfo()
                processEnded.value = False
                break

            interface.updateParallelProcess(''.join(currentFileName[:]).strip(), totalScans.value, currentScan.value,
                                            currentImageUpdated)
            interface.update()
