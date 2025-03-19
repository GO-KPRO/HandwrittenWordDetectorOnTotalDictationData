import os
import tkinter as tk
from tkinter import filedialog, ttk


class Interface:
    def __init__(self):

        self.scansArchivePath = ''
        self.outputDirectory = ''
        self.textPath = ''
        self.dirReady = False
        self.archReady = False
        self.textReady = False
        self.startPressed = False
        self.replaceLimit = 0

        self.root = tk.Tk()
        self.root.title('Handwritten Word Detector On Total Dictation Data')
        self.root.geometry('400x400')
        self.root.resizable(width=False, height=False)
        icon = tk.PhotoImage(file=os.path.join(os.getcwd(), 'sources\\icon.png'))
        self.root.iconphoto(False, icon)
        self.root.iconwindow()

        self.canvas = tk.Canvas(self.root, height=400, width=4000)
        self.canvas.pack()

        self.frame = tk.Frame(self.root)
        self.frame.place(relwidth=1, relheight=1)

        def startProcessing():
            self.startPressed = True
            self.startStopButton['bg'] = 'red'
            self.startStopButton['text'] = 'Stop processing'

        self.startStopButton = tk.Button(self.frame, text='Start processing',
                                         state=tk.DISABLED, command=startProcessing)
        self.startStopButton.place(height=25, width=150, x=10, y=190)

        def chooseScansArchive():
            path = filedialog.askopenfilename()
            fileName = os.path.basename(path)
            clearName, fileExtension = os.path.splitext(fileName)
            if path != '':
                if fileExtension != '.zip':
                    self.fileNameLabel['text'] = f'{fileName} has wrong type'
                    self.fileButton['text'] = 'Choose another file'
                    self.fileNameLabel['fg'] = 'red'
                    self.archReady = False
                    self.scansArchivePath = ''
                else:
                    self.fileNameLabel['text'] = fileName
                    self.fileButton['text'] = 'Choose scans archive'
                    self.fileNameLabel['fg'] = 'black'
                    self.archReady = True
                    self.scansArchivePath = path

                if self.dirReady and self.archReady and self.textReady:
                    self.startStopButton['state'] = tk.NORMAL
                else:
                    self.startStopButton['state'] = tk.DISABLED

        self.fileButton = tk.Button(self.frame, text='Choose scans archive',
                                    command=chooseScansArchive)
        self.fileButton.place(height=25, width=150, x=10, y=365)

        self.fileNameLabel = tk.Label(self.frame, text='', anchor='e', relief='groove', bg='white')
        self.fileNameLabel.place(height=25, width=220, x=170, y=365)

        def chooseDirectory():
            path = filedialog.askdirectory()
            dirName = os.path.basename(path)
            if path != '':
                if len(os.listdir(path)) > 0:
                    self.dirLabel['text'] = 'Please choose empty one'
                    self.dirButton['text'] = 'Choose another directory'
                    self.dirLabel['fg'] = 'red'
                    self.dirReady = False
                else:
                    self.dirLabel['text'] = path
                    self.dirLabel['fg'] = 'black'
                    self.dirButton['text'] = 'Choose scans archive'
                    self.outputDirectory = path
                    self.dirReady = True

            if self.dirReady and self.archReady and self.textReady:
                self.startStopButton['state'] = tk.NORMAL
            else:
                self.startStopButton['state'] = tk.DISABLED

        self.dirButton = tk.Button(self.frame, text='Choose output directory',
                                   command=chooseDirectory)
        self.dirButton.place(height=25, width=150, x=10, y=330)

        self.dirLabel = tk.Label(self.frame, text='', anchor='e', relief='groove', bg='white')
        self.dirLabel.place(height=25, width=220, x=170, y=330)

        self.scanImage = tk.Label(self.frame)

        def chooseText():
            path = filedialog.askopenfilename()
            fileName = os.path.basename(path)
            clearName, fileExtension = os.path.splitext(fileName)
            if path != '':
                if fileExtension != '.txt':
                    self.textLabel['text'] = f'{fileName} has wrong type'
                    self.textButton['text'] = 'Choose another text file'
                    self.textLabel['fg'] = 'red'
                    self.textReady = False
                    self.textPath = ''
                else:
                    self.textLabel['text'] = fileName
                    self.textButton['text'] = 'Choose text file'
                    self.textLabel['fg'] = 'black'
                    self.textReady = True
                    self.textPath = path

                if self.dirReady and self.archReady and self.textReady:
                    self.startStopButton['state'] = tk.NORMAL
                else:
                    self.startStopButton['state'] = tk.DISABLED

        self.textButton = tk.Button(self.frame, text='Choose original text',
                                    command=chooseText)
        self.textButton.place(height=25, width=150, x=10, y=295)

        self.textLabel = tk.Label(self.frame, text='', anchor='e', relief='groove', bg='white')
        self.textLabel.place(height=25, width=220, x=170, y=295)

        self.progressBar = ttk.Progressbar(self.frame, length=100, value=0)
        self.progressBar.place(height=25, width=380, x=10, y=225)

        percent = tk.IntVar(value=0)

        self.replaceLabel = tk.Label(self.frame, text=f'Replace limit: {percent.get()}%')
        self.replaceLabel.place(height=25, width=150, x=10, y=260)

        def changeRL(newVal):
            curLim = round(float(newVal), 1)
            self.replaceLabel['text'] = f'Replace limit: {curLim}%'
            self.replaceLimit = curLim

        self.scale = ttk.Scale(self.frame, length=1000, from_=0., to=100.0, variable=percent, command=changeRL)
        self.scale.place(height=25, width=220, x=170, y=260)

        self.currentFileLabel = tk.Label(self.frame, text='')
        self.currentFileLabel.place(height=25, width=220, x=170, y=190)

    def updateCurrentFileLabel(self, label):
        self.currentFileLabel['text'] = label

    def updateCurrentImage(self, path):
        img = tk.PhotoImage(file=path)
        hScale = img.height() // 170
        img = img.subsample(hScale, hScale)
        self.scanImage.image = img
        self.scanImage['image'] = self.scanImage.image
        self.scanImage.place(height=170, width=380, x=10, y=10)

    def updateProgressBar(self, length, value):
        self.progressBar['maximum'] = length
        self.progressBar['value'] = value


    def update(self):
        self.root.update()

    def validateScans(self, flag):
        if flag:
            self.fileButton['state'] = tk.DISABLED
            self.dirButton['state'] = tk.DISABLED
            self.textButton['state'] = tk.DISABLED
            self.scale['state'] = tk.DISABLED
        else:
            self.fileNameLabel['text'] = f'Wrong files format'
            self.fileButton['text'] = 'Choose another archive'
            self.fileNameLabel['fg'] = 'red'
            self.startStopButton['text'] = 'Start processing'
            self.startStopButton['bg'] = 'white'
            self.archReady = False
            self.startPressed = False
            self.scansArchivePath = ''

            if self.dirReady and self.archReady:
                self.startStopButton['state'] = tk.NORMAL
            else:
                self.startStopButton['state'] = tk.DISABLED
