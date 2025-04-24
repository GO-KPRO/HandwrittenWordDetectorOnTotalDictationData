import os
import codecs

import PyPDF2
import cv2
from pdf2image import convert_from_path, convert_from_bytes

from base.image import Image
from base.levenstein import getLevenshteinEditorialInstruction, align


class Scan:

    def __init__(self, scanPath: str, imagesFolder: str):
        self.scanPath = scanPath
        self.imagesFolder = imagesFolder
        self.images = []
        self.originalText = ''
        self.originalWords = []
        self.originalWordId = []
        self.recognizedText = ''
        self.recognizedWords = []
        self.recognizedWordId = []
        self.metric = 0
        self.editorialInstruction = ''
        self.alignedRecognizedWordId = []
        try:
            popplerPath = os.path.join(os.getcwd(), 'sources\\poppler-24.08.0\\Library\\bin').replace('\\', os.sep).\
                replace('/', os.sep)
            file = open(self.scanPath, 'rb')
            pdfReader = PyPDF2.PdfReader(file)
            while len(pdfReader.pages) < 1:
                print(len(pdfReader.pages))
                file = open(self.scanPath, 'rb')
                pdfReader = PyPDF2.PdfReader(file)
            for i, image in enumerate(convert_from_path(self.scanPath, poppler_path=popplerPath)):
                imagePath = os.path.join(imagesFolder, str(i) + '.png')
                image.save(imagePath, 'PNG')
                self.images.append(Image(imagePath))
        except Exception as e:
            print(f"Error converting or saving images: {str(e)}")

    def readText(self, path: str):
        try:
            with codecs.open(path, 'r', 'utf_8_sig') as f:
                lines = [line.strip() for line in f.readlines()]
                self.originalText = ' '.join(lines)
                self.originalWords = self.originalText.split()
                for id, word in enumerate(self.originalWords):
                    for letter in word:
                        self.originalWordId.append(id)
                    self.originalWordId.append(-1)
                self.originalWordId = self.originalWordId[:-1]
        except Exception as e:
            print(f"Error processing text file: {str(e)}")

    def crop(self, crops=None):
        if crops is None:
            crops = [[[50, 1450], [650, 2150]], [[50, 1450], [0, 1750]]]
        if len(crops) != len(self.images):
            print(f'Wrong crops list size: is {len(crops)}, must be {len(self.images)}')
            return
        for i, image in enumerate(self.images):
            self.images[i].crop(crops[i][0], crops[i][1])

    def detection(self, detector):
        startId = 0
        for i, image in enumerate(self.images):
            startId = self.images[i].detection(detector, startId)

    def recognition(self, recognizer):
        for i, image in enumerate(self.images):
            self.images[i].recognition(recognizer)
            for j, word in enumerate(self.images[i].words):
                self.recognizedWords.append([word.label, i])
                self.recognizedText += word.label + ' '
                for k, char in enumerate(word.label):
                    self.recognizedWordId.append(word.id)
                self.recognizedWordId.append(-1)

        self.recognizedText.strip()

    def align(self):
        if len(self.originalText) == 0:
            print('No original text readed')
            return
        try:
            self.metric, self.editorialInstruction = getLevenshteinEditorialInstruction(self.originalText,
                                                                                        self.recognizedText)
            self.alignedRecognizedWordId = align(self.recognizedWordId, self.editorialInstruction)
        except Exception as e:
            print(f"Error aligning texts: {str(e)}")

    def rateWords(self, replacePercent):
        if len(self.alignedRecognizedWordId) != len(self.originalWordId):
            print(
                f'Error: bad align; length of strings are not the same: {len(self.alignedRecognizedWordId)} and {len(self.originalWordId)}')

        counter = [[] for i in range(len(self.originalWords))]
        for i in range(len(self.alignedRecognizedWordId)):
            currentId = self.originalWordId[i]
            if currentId != -1:
                counter[currentId].append(self.alignedRecognizedWordId[i])
        for i, idSet in enumerate(counter):
            if not ('i' in idSet):
                targetWordNum = max(idSet, key=idSet.count)
                if type(targetWordNum) == int:
                    if len(self.originalWords[i]) == len(self.recognizedWords[targetWordNum][0]):
                        metric = idSet.count('r') / len(self.originalWords[i])
                        if metric <= replacePercent:
                            imageNum = self.recognizedWords[targetWordNum][1]
                            for j, word in enumerate(self.images[imageNum].words):
                                if word.id == targetWordNum:
                                    self.images[imageNum].words[j].alignedLabel = self.originalWords[i]
                                    self.images[imageNum].words[j].metric = metric

    def saveData(self, path, rate):
        for image in self.images:
            for word in image.words:
                if (word.metric <= rate) and (word.metric != -1):
                    imgDir = os.path.join(path, word.alignedLabel.strip('\\/|:*?\"<>|\n\t '))
                    os.makedirs(imgDir, exist_ok=True)
                    scanName, extension = os.path.splitext(os.path.basename(self.scanPath))
                    imgFileName = os.path.join(imgDir, scanName + '_' + str(word.id) + '.png')
                    cv2.imwrite(imgFileName, word.image)
