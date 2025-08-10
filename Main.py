import tkinter as tk # tkinter library for GUI
from tkinter import filedialog
from urllib import response
from xmlrpc import client # filedialog for selecting folders
import requests # requests library for conections with OLlama
from PIL import ImageGrab as sc # imports the screenshot function from pillow library
from PIL import Image, ImageTk
import os # imports the os library for file operations
from ScreenCapture import ScreenCapture # imports the ScreenCapture file to use the class
from datetime import datetime # imports the datetime library to get the date of the screenshot
import threading # imports the threading library to handle concurrent tasks
from openai import OpenAI # imports the OpenAI library to use the API key
import base64
import io # imports the io library for handling byte data

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

        patchNumber = patchInput.get().strip()
        if not patchNumber:
            analyzingTag.config(text="Please enter a patch number.") # shows error if no patch number is entered
            analyzingTag.pack() # shows the analyzing label

            return

        analyzingTag.config(text="Analyzing...") # shows the analyzing label
        analyzingTag.pack() # shows the analyzing label
        
        base64Image = encodeImage(saveRoute) # encodes the screenshot to base64

        systemPrompt = (
            "Analyze the following screenshot. It might show a League of Legends champion select screen or something else. "
            "If the screenshot does NOT show a champion select screen, respond exactly with: NO CHAMP SELECT. "
            "If the screenshot DOES show a champion select screen, respond ONLY with a comma-separated list of champions. "
            "- If you see both teams, list them in this exact order: "
            "[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5],"
            "[enemyChampion1],[enemyChampion2],[enemyChampion3],[enemyChampion4],[enemyChampion5]. "
            "- If you see ONLY the allied team, list only these champions as: "
            "[allyChampion1],[allyChampion2],[allyChampion3],[allyChampion4],[allyChampion5]. "
            "After that, add which champion the player has selected using: user:championSelected. "

            "Next, you MUST perform the following steps strictly in order: "
            f"Step 1: Using the exact patch number {patchNumber}, use WEB SEARCH internally to find the best builds for the USER CHAMPION against enemy champions and synergies with ally champions for that current patch. Prioritize items strong against multiple enemies."
            "Then add the next lines to your response"  
            "Line 3: list of items of the first build separated by commas "
            "Line 4: short reasoning and approach for the first build"
            "Line 5: list of items of the second build  separated by commas"
            "Line 6: short reasoning and approach for the second build"
            f"Line 7: The patch number used for this search."

            "The build must be written as a comma-separated list of exactly six items: item1,item2,item3,item4,item5,item6."
            "You must always show these 7 lines of information and nothing else. Do not tell the user when you searched something."
        )

        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search"}],
            temperature=0,
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
        showImages(AIResponse)
        analyzingTag.config(text=AIResponse) # shows the analyzing label


    # start the analysis in the separate thread
    threading.Thread(target=analyzeAI).start() # starts the analysis in a separate thread

def showImages(response):
    info = response.splitlines()
    champions = info[0].split(",")  # first line contains champions separated by commas
    print(champions)
    for i, champion in enumerate(champions):
        image = getChampionImage(champion)  # get the champion image
        if image:
            pic = ImageTk.PhotoImage(image)
            label = tk.Label(frame, image=pic)
            label.image = pic  # keep a reference to avoid garbage collection
            # place in grid rows and columns
            row = i // 5  # row 0 for first 5, row 1 for next 5
            col = i % 5   # column from 0 to 4
            label.grid(row=row, column=col, padx=5, pady=5)


def getChampionImage(championName):
    patchNumber = patchInput.get().strip() # get the patch number from the input
    firstNumber = int(patchNumber.split(".")[0]) # get the first number of the patch
    realVersionFirstNumber = firstNumber - 10 # get the real version first number
    realVersion = str(realVersionFirstNumber) + "." + patchNumber.split(".")[1] + ".1" # gets the real version of the patch
    championName = championName.replace(" ", "").replace("'","").replace(".", "").replace("Glasc", "").replace("Wukong", "MonkeyKing") # format the champion name
    url = f"https://ddragon.leagueoflegends.com/cdn/{realVersion}/img/champion/{championName}.png" # URL to get the champion image
    response = requests.get(url) # makes a request to the URL
    print(url,response.status_code)
    if response.status_code == 200:
        imageData = response.content # gets the content of the response
        image = Image.open(io.BytesIO(imageData)) # opens the image
        return image
    
    else:
        return None # returns None if the request was not successful
        print(f"Champion image for {championName} not found.") # prints an error message if the champion image was not found


# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("600x600") # 600 pixels resolution

frame = tk.Frame(rootWindow, bg="lightgray", width=500, height=400) # create a frame to hold the components


# -------------- COMPONENTS --------------

folderTag = tk.Label(rootWindow, text=f"Current Save Folder: {saveFolder}") # label to show current save folder

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=scAndAnalyze) # button to analyze text

changeFolderButton = tk.Button(rootWindow, text="Change Save Folder", command=selectSaveFolder) # button to change save folder

analyzingTag = tk.Label(rootWindow, text="Analyzing...") # label to show when analyzing

analyzingTag.pack_forget() # hide the analyzing label initially

global patchInput
patchInput = tk.Entry(rootWindow) # input field for the patch number

# -------------- PLACING COMPONENTS --------------

textTitle.pack(pady=20) # add title to window
changeFolderButton.pack(pady=10) # add change folder button to window
folderTag.pack(pady=10) # add folder tag to window
analyzeButton.pack(pady=10) # add analyze button to window
patchInput.pack(pady=10) # add patch input to window
frame.pack(padx=10, pady=10)  # place it


# -------------- RUN --------------

rootWindow.mainloop() # starts the app