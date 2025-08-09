import tkinter as tk
from PIL import ImageGrab
import os

# reads the folder where screenshots will be saved
def readSaveFolder():
    SAVE_FOLDER_FILE = "save_folder.txt"
    if os.path.exists(SAVE_FOLDER_FILE):
        with open(SAVE_FOLDER_FILE, 'r', encoding="utf-8") as f:
            path = f.read().strip()
            if path and os.path.isdir(path):
                return path
    # default folder if file doesn't exist or path is invalid
    defaultFolder = os.path.join(os.path.expanduser("~"), "Pictures")
    return defaultFolder

# class to handle screen capturing
class ScreenCapture:
    def __init__(self, onComplete = None):
        self.saveFolder = readSaveFolder()
        self.onComplete = onComplete

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3) # semi-transparent to see the screen
        self.root.config(cursor="cross") # crosshair cursor

        # initialize variables for capturing
        self.startX = None
        self.startY = None
        self.rect = None

        # create a canvas for capturing
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.onButtonPress)
        self.canvas.bind("<B1-Motion>", self.onMouseDrag)
        self.canvas.bind("<ButtonRelease-1>", self.onButtonRelease)

    def startCapturing(self):
        self.root.mainloop()

    # handles mouse button press event
    def onButtonPress(self, event):
        self.startX = event.x
        self.startY = event.y
        self.rect = self.canvas.create_rectangle(self.startX, self.startY, self.startX, self.startY, outline='red', width=2)

    # handles mouse drag event
    def onMouseDrag(self, event):
        curX, curY = event.x, event.y
        self.canvas.coords(self.rect, self.startX, self.startY, curX, curY)

    # handles mouse button release event
    def onButtonRelease(self, event):
        endX, endY = event.x, event.y
        self.root.withdraw()  # hide the main window after capturing

        x1 = min(self.startX, endX)
        y1 = min(self.startY, endY)
        x2 = max(self.startX, endX)
        y2 = max(self.startY, endY)

        # captures the selected region
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        # saves the screenshot
        savePath = os.path.join(self.saveFolder, "screenshot.png")
        img.save(savePath)
        print(f"Captura guardada: {x1}, {y1}, {x2}, {y2}")

        # destroys the window
        self.root.destroy()
        if self.onComplete:
            self.onComplete()
