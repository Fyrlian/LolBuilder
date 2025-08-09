import tkinter as tk # tkinter library for GUI
from tkinter import filedialog # filedialog for selecting folders
import requests # requests library for conections with OLlama
from PIL import ImageGrab as sc # imports the screenshot function from pillow library
import os # imports the os library for file operations
import ollama # imports the Ollama library to send requests to analyze champ select

# -------------- FUNCTIONS --------------

SAVE_FOLDER_FILE = "save_folder.txt" # file to save the folder path

# reads the folder where screenshots will be saved and if there is no folder we asign one
def readSaveFolder():
    if os.path.exists(SAVE_FOLDER_FILE):
        with open(SAVE_FOLDER_FILE, 'r', encoding="utf-8") as f:
            path = f.read().strip()
            if path and os.path.isdir(path):
                return path
    defaultFolder = os.path.join(os.path.expanduser("~"), "Pictures") # initial folder for the images
    writeSaveFolder(defaultFolder)
    return defaultFolder

# updates the folder where screenshots will be saved
def writeSaveFolder(path):
    with open(SAVE_FOLDER_FILE, "w", encoding="utf-8") as f:
        f.write(path)

saveFolder = readSaveFolder()
saveRoute = os.path.join(saveFolder, "screenshot.png")

def scAndAnalyze():
    captureScreenshot()
    analyzeScreenshot()

# screenshots the league client
def captureScreenshot():
    global saveRoute # allows access to saveRoute variable
    image = sc.grab() # takes the screenshot to analyze
    image.save(saveRoute) # saves the screenshot

# allows selecting the folder to save images
def selectSaveFolder():
    global saveFolder, saveRoute # allows access to saveFolder and saveRoute variables
    newFolder = filedialog.askdirectory(title="Please select the folder to save images") # opens a dialog to select folder
    if newFolder:
        saveFolder = newFolder # modifies saveFolder to be updated
        saveRoute = os.path.join(saveFolder, "screenshot.png") # sets the path to save the screenshot
        writeSaveFolder(saveFolder)
        folderTag.config(text=f"Current Save Folder: {saveFolder}") # updates the label to show the new save folder

# analyzes the champions in the screenshot using llava model
def analyzeScreenshot():
    response = ollama.chat(
        model = "llava",
        messages = [
            {"role":"user", "content": systemPrompt,"image":saveRoute}
        ]
    )
    
    print(response.message.content)

# -------------- CONFIGS --------------

systemPrompt = "Analyze the following screenshot. It might show a League of Legends champion select screen or something else.\
If the screenshot does NOT show a champion select screen, respond exactly with: " \
"NO CHAMP SELECT \
If the screenshot DOES show a champion select screen, respond ONLY with a comma-separated list of champions.\
- If you see both teams, list them in this exact order:\
[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5],[enemyChampion1],[enemyChampion2],[enemyChampion3],[enemyChampion4],[enemyChampion5]\
    - If you see ONLY the allied team, list only these champions as: " \
    "[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5]\
Do NOT provide any other information, explanation, or commentary. Your entire response must be exactly one line as specified above."

# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("600x600") # 600 pixels resolution

# -------------- COMPONENTS --------------

folderTag = tk.Label(rootWindow, text=f"Current Save Folder: {saveFolder}") # label to show current save folder

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=scAndAnalyze) # button to analyze text

changeFolderButton = tk.Button(rootWindow, text="Change Save Folder", command=selectSaveFolder) # button to change save folder

# -------------- PLACING COMPONENTS --------------

textTitle.pack(pady=20) # add title to window
changeFolderButton.pack(pady=10) # add change folder button to window
folderTag.pack(pady=10) # add folder tag to window
analyzeButton.pack(pady=10) # add analyze button to window


# -------------- RUN --------------

rootWindow.mainloop() # starts the app