import cv2

from base.word import Word


class Image:

    def __init__(self, path: str):
        self.image = None  # 3d np.array OpenCv BGR image format
        self.path = None  # Path to image to read
        self.words = []  # list of detected words
        try:
            self.image = cv2.imread(path)
            self.path = path
        except Exception as e:
            print(f"Error processing file: {str(e)}")

    def crop(self, x=None, y=None):  # Cropping the image
        if x is None:
            x = [50, 1450]
        if y is None:
            y = [0, 1750]
        try:
            self.image = self.image[y[0]:y[1], x[0]:x[1]]
            cv2.imwrite(self.path, self.image)
        except Exception as e:
            print(f"Error processing image: {str(e)}")

    def detection(self, detector, startId: int):  # Detecting the words and creating Word objects
        try:
            bboxes = detector.run(self.path)
            currentId = startId
            for bbox in bboxes:
                p1 = [int(bbox[0]), int(bbox[1])]
                p2 = [int(bbox[2]), int(bbox[3])]
                img = self.image[p1[1]:p2[1], p1[0]:p2[0]]
                self.words.append(Word(img, p1, p2))
            self.words.sort()
            for i, word in enumerate(self.words):
                self.words[i].id = currentId
                currentId += 1
            return currentId
        except Exception as e:
            print(f"Detecting error: {str(e)}")

    def recognition(self, recognizer):  # Recognition of words in all boxes.
        for i in range(len(self.words)):
            self.words[i].recognition(recognizer)
