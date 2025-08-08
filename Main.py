import tkinter as tk # tkinter library for GUI
import requests # requests library for conections with OLlama

# -------------- FUNCTIONS --------------

# screenshots the league client
def captureScreenshot():
    pass

# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("600x600") # 600 pixels resolution

# -------------- COMPONENTS --------------

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=) # button to analyze text

# -------------- RUN --------------

rootWindow.mainloop() # starts the app