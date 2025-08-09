import tkinter as tk # tkinter library for GUI
from tkinter import filedialog # filedialog for selecting folders
import requests # requests library for conections with OLlama
from PIL import ImageGrab as sc # imports the screenshot function from pillow library
import os # imports the os library for file operations
from ollama import Ollama # imports the Ollama library to send requests to analyze champ select
# -------------- FUNCTIONS --------------

# screenshots the league client
def captureScreenshot():
    image = sc.grab() # takes the screenshot to analyze
    image.save(saveRoute)

# allows selecting the folder to save images
def selectSaveFolder():
    newFolder = filedialog.askdirectory(title="Please select the folder to save images") # opens a dialog to select folder
    if newFolder:
        global saveFolder # allows access to saveFolder variable
        global saveRoute # allows access to saveRoute variable

        saveFolder = newFolder # modifies saveFolder to be updated
        saveRoute = os.path.join(saveFolder, "screenshot.png") # sets the path to save the screenshot

        folderTag.config(text=f"Current Save Folder: {saveFolder}") # updates the label to show the new save folder

# analyzes the champions in the screenshot using llava model
def analyzeScreenshot():
    response = ollama.chat(
        model = "llava",
        messages = [
            {"role":"user", "content": systemPrompt,"image":saveRoute}
        ]
    )

    print(response['choices'][0]['message']['content']) # prints the response from the model

# -------------- CONFIGS --------------

saveFolder = os.path.join(os.path.expanduser("~"), "Pictures") # initial folder for the images
saveRoute = os.path.join(saveFolder, "screenshot.png") # sets the path initial route to save the screenshot
ollama = Ollama() # creates an instance of the Ollama class to send requests
systemPrompt = "Analyze the following screenshot for League of Legends champion select:" 

# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("600x600") # 600 pixels resolution

# -------------- COMPONENTS --------------

folderTag = tk.Label(rootWindow, text=f"Current Save Folder: {saveFolder}") # label to show current save folder

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=captureScreenshot) # button to analyze text

changeFolderButton = tk.Button(rootWindow, text="Change Save Folder", command=selectSaveFolder) # button to change save folder

# -------------- PLACING COMPONENTS --------------

textTitle.pack(pady=20) # add title to window
changeFolderButton.pack(pady=10) # add change folder button to window
folderTag.pack(pady=10) # add folder tag to window
analyzeButton.pack(pady=10) # add analyze button to window


# -------------- RUN --------------

rootWindow.mainloop() # starts the app