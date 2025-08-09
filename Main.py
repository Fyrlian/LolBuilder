import tkinter as tk # tkinter library for GUI
from tkinter import filedialog
from urllib import response
from xmlrpc import client # filedialog for selecting folders
import requests # requests library for conections with OLlama
from PIL import ImageGrab as sc # imports the screenshot function from pillow library
import os # imports the os library for file operations
from ScreenCapture import ScreenCapture # imports the ScreenCapture file to use the class
from datetime import datetime # imports the datetime library to get the date of the screenshot
import threading # imports the threading library to handle concurrent tasks
from openai import OpenAI # imports the OpenAI library to use the API key
import base64

# -------------- API KEY --------------

apiKey = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=apiKey) # initializes the OpenAI client with the API key


# -------------- FUNCTIONS --------------

SAVE_FOLDER_FILE = "save_folder.txt" # file to save the folder path

def encodeImage(imagePath):
    with open(imagePath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

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
    ScreenCapture(onComplete=analyzeScreenshot) # we use a callback to analyze the screenshot after capturing

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

    if os.path.exists(saveRoute):

        # obtains last update date on the picture
        mod_timestamp = os.path.getmtime(saveRoute)
        mod_date = datetime.fromtimestamp(mod_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Picture analyzed date: {mod_date}")

    # function to analyze the screenshot using AI that will be executed in a separate thread
    def analyzeAI():

        analyzingTag.config(text="Analyzing...") # shows the analyzing label
        analyzingTag.pack() # shows the analyzing label
        
        base64Image = encodeImage(saveRoute) # encodes the screenshot to base64

        response = client.responses.create(
            model="gpt-4.1",
            tools=[{"type": "web_search_preview"}],
            temperature = 0,
            input=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": systemPrompt,
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64Image}",
                    }
                ]
                }
            ],
        )

        AIResponse = response.output_text
        print(AIResponse)
        analyzingTag.config(text=AIResponse) # shows the analyzing label

    # start the analysis in the separate thread
    threading.Thread(target=analyzeAI).start() # starts the analysis in a separate thread



# -------------- CONFIGS --------------

systemPrompt = "Analyze the following screenshot. It might show a League of Legends champion select screen or something else."\
"If the screenshot does NOT show a champion select screen, respond exactly with: " \
"NO CHAMP SELECT" \
"If the screenshot DOES show a champion select screen, respond ONLY with a comma-separated list of champions."\
"- If you see both teams, list them in this exact order:"\
"[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5],[enemyChampion1],[enemyChampion2],[enemyChampion3],[enemyChampion4],[enemyChampion5]"\
"- If you see ONLY the allied team, list only these champions as: " \
"[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5]"\
"After that you must add which champion the player has selected typing user:championSelected"\
"Now, the most important part, based on the champions you've found you must also recommend the user " \
"two builds for his game using information from the website LeagueOfGraphs. " \
"You must always have in mind ally and enemy champions for these suggestions"\
"and the response of the build with a comma-separated list of items item1,item2,item3,item4,item5,item6"\
"The structure for the info must follow this guide line1 : champions, line 2: user champion, line3 : build , line 4: explaining the reasoning ad the approach of the build , line 5 : build2 " \
", line 6 : explaining the reasoning and the approach the build 2 , line 7 : current league patch"\
"Do NOT provide any other information, explanation, or commentary. Your entire response must follow exactly the guide provided"

# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("600x600") # 600 pixels resolution

# -------------- COMPONENTS --------------

folderTag = tk.Label(rootWindow, text=f"Current Save Folder: {saveFolder}") # label to show current save folder

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=scAndAnalyze) # button to analyze text

changeFolderButton = tk.Button(rootWindow, text="Change Save Folder", command=selectSaveFolder) # button to change save folder

analyzingTag = tk.Label(rootWindow, text="Analyzing...") # label to show when analyzing
analyzingTag.pack_forget() # hide the analyzing label initially

# -------------- PLACING COMPONENTS --------------

textTitle.pack(pady=20) # add title to window
changeFolderButton.pack(pady=10) # add change folder button to window
folderTag.pack(pady=10) # add folder tag to window
analyzeButton.pack(pady=10) # add analyze button to window


# -------------- RUN --------------

rootWindow.mainloop() # starts the app