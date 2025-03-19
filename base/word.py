class Word:

    def __init__(self, image, pointTopLeft: list, pointRightDown: list):
        self.id = None  # Unique number of word at scan
        self.image = image  # 3d np.array OpenCv BGR image format
        self.pointTopLeft = pointTopLeft  # Top left point of bounding box at original image
        self.pointRightDown = pointRightDown  # Down right point of bounding box at original image
        self.label = None  # Written word
        self.metric = -1  # Quality metric of bbox
        self.alignedLabel = ''

    def __eq__(self, other):  # The == function for auto sorting
        return (self.pointTopLeft == other.pointTopLeft) and (self.pointRightDown == other.pointRightDown)

    def __lt__(self, other):  # The < function for auto sorting
        # First sort vertically, then sort horizontally
        ys = (self.pointTopLeft[1] + self.pointRightDown[1]) / 2
        if ys < other.pointTopLeft[1]:
            return True
        elif ys > other.pointRightDown[1]:
            return False
        else:
            xs = (self.pointTopLeft[0] + self.pointRightDown[0]) / 2
            if xs < other.pointTopLeft[0]:
                return True
            elif xs > other.pointRightDown[0]:
                return False
            else:
                xo = (other.pointTopLeft[0] + other.pointRightDown[0]) / 2
                return xs < xo

    def recognition(self, recognizer):  # Recognition of word at the image
        try:
            self.label = recognizer.run(self.image)
        except Exception as e:
            print(f"Error recognizing text: {str(e)}")
