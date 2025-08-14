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
import json # imports json library to handle JSON files to find the id of each item

# -------------- API KEY --------------

apiKey = os.getenv("OPENAI_API_KEY") # user should asign here the api key if not using environment variables

client = OpenAI(api_key=apiKey) # initializes the OpenAI client with the API key

# -------------- FUNCTIONS --------------

SAVE_FOLDER_FILE = "save_folder.txt" # file to save the folder path

# encodes an image to base64
def encodeImage(imagePath):
    with open(imagePath, "rb") as image_file: # opens the image file in binary mode
        return base64.b64encode(image_file.read()).decode("utf-8") # returns the image encoded to base64

# reads the folder where screenshots will be saved and if there is no folder we asign one
def readSaveFolder():
    if os.path.exists(SAVE_FOLDER_FILE):
        with open(SAVE_FOLDER_FILE, 'r', encoding="utf-8") as f:
            path = f.read().strip()
            if path and os.path.isdir(path):
                return path
    defaultFolder = os.path.join(os.path.expanduser("~"), "Pictures") # initial folder for the images
    writeSaveFolder(defaultFolder) # sets the default folder
    return defaultFolder

# updates the folder where screenshots will be saved
def writeSaveFolder(path):
    with open(SAVE_FOLDER_FILE, "w", encoding="utf-8") as f:
        f.write(path)

saveFolder = readSaveFolder() # get the folder where screenshots will be saved
saveRoute = os.path.join(saveFolder, "screenshot.png") # path to save the screenshot

# captures the screen and analyzes the screenshot
def scAndAnalyze():
    patchNumber = patchInput.get().strip() # get the patch number from the input

    if not patchNumber: # if no patch number is entered
        analyzingTag.config(text="Please enter a patch number.",fg="red") # shows error if no patch number is entered
        analyzingTag.pack() # shows the analyzing label

        return
    
    firstNumber = int(patchNumber.split(".")[0]) # get the first number of the patch
    realVersionFirstNumber = firstNumber - 10 # get the real version first number
    realVersion = str(realVersionFirstNumber) + "." + patchNumber.split(".")[1] + ".1" # gets the real version of the patch
    
    url = f"https://ddragon.leagueoflegends.com/cdn/{realVersion}/data/en_US/item.json" # URL to get the items

    response = requests.get(url) # makes a request to the URL

    global JSONResponse
    JSONResponse = response.json() # gets the JSON response

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

        analyzingTag.config(text="Analyzing...",fg = "black") # shows the analyzing label
        analyzingTag.pack() # shows the analyzing label
        
        base64Image = encodeImage(saveRoute) # encodes the screenshot to base64

        patchNumber = patchInput.get().strip() # get the patch number from the input
        firstNumber = int(patchNumber.split(".")[0]) # get the first number of the patch
        realVersionFirstNumber = firstNumber - 10 # get the real version first number
        realVersion = str(realVersionFirstNumber) + "." + patchNumber.split(".")[1] + ".1" # gets the real version of the patch

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
            f"To find the ID of the items that you will have to use later on your response you must find it in that you can find here https://ddragon.leagueoflegends.com/cdn/{realVersion}/data/en_US/item.json"
            "You MUST ONLY USE THE ITEMS FROM THIS WEBSITE https://leagueofitems.com/items , if the item is not there DO NOT SUGGEST IT"

            "Next, you MUST perform the following steps strictly in order: "
            f"Step 1: Using the exact patch number {realVersion}, use WEB SEARCH to find the best builds for the USER CHAMPION against enemy champions and synergies with ally champions ON CURRENT PATCH. Prioritize items strong against multiple enemies. You should never show search() or anythign to related. Only show what you found"

            "Then add the next lines to your response"  
            "Line 3: list of items in https://leagueofitems.com/items of the first build separated by commas, after every item type : and id of the item"
            "Line 4: short reasoning and approach for the first build"
            "Line 5: list of items in https://leagueofitems.com/items of the second build  separated by commas, after every item type : and id of the item"
            "Line 6: short reasoning and approach for the second build"
            f"Line 7: The patch number used for this search."

            "The build must be written as a comma-separated list of exactly six items: item1,item2,item3,item4,item5,item6."
            "Remember you must always show these 7 lines of information and nothing else. Do not tell the user when you searched something. Do not add stuff to your response. Just those lines given the instructions"
        )

        # Send the request to the API
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

        print(AIResponse) # prints the AI response to the console

        if AIResponse.strip() == "NO CHAMP SELECT": # if the AI response is NO CHAMP SELECT
            analyzingTag.config(text="No champion select detected.", fg="red")
            return

        showImages(AIResponse)
        analyzingTag.config(text=AIResponse) # shows the analyzing label
        analyzeButton.pack_forget() # hides the analyze button

    # start the analysis in the separate thread
    threading.Thread(target=analyzeAI).start() # starts the analysis in a separate thread

# shows the images of the champions and items in the response
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
            if row == 1: # making space here for enemy tag
                row = 2
            label.grid(row=row+1, column=col, padx=5, pady=5)
    items = info[3].split(",") # 4th line contains the items separated by commas
    for i, item in enumerate(items):
        image = getItemImage(item)  # get the item image
        if image:
            pic = ImageTk.PhotoImage(image)
            label = tk.Label(frame, image=pic)
            label.image = pic  # keep a reference to avoid garbage collection
            label.grid(row=5, column=i, padx=5, pady=5)

    items2 = info[5].split(",") # 4th line contains the items separated by commas
    for i, item in enumerate(items2):
        image = getItemImage(item)  # get the item image
        if image:
            pic = ImageTk.PhotoImage(image)
            label = tk.Label(frame, image=pic)
            label.image = pic  # keep a reference to avoid garbage collection
            label.grid(row=5, column=i, padx=5, pady=5)

    hideMainWindow()  # hide the main window components
    showTags()  # show the ally and enemy team labels
    backButton.grid(row=6, column=0, padx=5, pady=5)  # add back button to window
    rootWindow.geometry("1000x600")  # set window size
    frame.pack(padx=10, pady=10)  # place the frame

# gets the image of a champion
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

# gets the image of an item
def getItemImage(item):
    patchNumber = patchInput.get().strip() # get the patch number from the input
    firstNumber = int(patchNumber.split(".")[0]) # get the first number of the patch
    realVersionFirstNumber = firstNumber - 10 # get the real version first number
    realVersion = str(realVersionFirstNumber) + "." + patchNumber.split(".")[1] + ".1" # gets the real version of the patch

    itemName = item.split(":")[0].strip() # get the item name from the response
    imageId = None # variable to store the image ID

    for itemId, itemDictionary in JSONResponse["data"].items(): # iterate through the items in the JSON response
        if itemDictionary["name"].lower() == itemName.lower(): # check if the item name matches
            imageId = itemDictionary["image"]["full"]
            break

    url = f"https://ddragon.leagueoflegends.com/cdn/{realVersion}/img/item/{imageId}" # URL to get the item image
    response = requests.get(url) # makes a request to the URL
    print(url,response.status_code)
    if response.status_code == 200:
        imageData = response.content # gets the content of the response
        image = Image.open(io.BytesIO(imageData)) # opens the image
        return image
    
    else:
        return None # returns None if the request was not successful
        print(f"Item image for {itemId} not found.") # prints an error message if the item image was not found

# goes back to the main window hiding build and champion images
def goBack():
    rootWindow.geometry("400x280") # 600 pixels resolution
    frame.pack_forget()
    changeFolderButton.pack(pady=10) # add change folder button to window
    folderTag.pack(pady=10) # add folder tag to window
    analyzeButton.pack(pady=10) # add analyze button to window
    patchInput.pack(pady=10) # add patch input to window
    analyzingTag.pack_forget() # add analyzing label to window

# hides the main window components
def hideMainWindow():
    analyzeButton.pack_forget() # hides the analyze button
    analyzingTag.pack_forget() # hides the analyzing label
    changeFolderButton.pack_forget() # hides the change folder button
    folderTag.pack_forget() # hides the folder tag
    patchInput.pack_forget() # hides the patch input

# shows the tags for enemy and ally teams
def showTags():
    enemyTeamTag = tk.Label(frame, text="Enemy team") # label to show when analyzing
    enemyTeamTag.grid(row=2, column=0, padx=5, pady=5)

    allyTeamTag = tk.Label(frame, text="Ally team") # label to show when analyzing
    allyTeamTag.grid(row=0, column=0, padx=5, pady=5)

    itemsTag = tk.Label(frame, text="Optimal build") # label to show when analyzing
    itemsTag.grid(row=4, column=0, padx=5, pady=5)

    enemyTeamTag.config(fg="red")
    allyTeamTag.config(fg="blue")

# -------------- WINDOW --------------

rootWindow = tk.Tk() # create main window of the app
rootWindow.title("Lol Builder") # title of the main window
rootWindow.geometry("400x280") # 600 pixels resolution

frame = tk.Frame(rootWindow, width=500, height=400) # create a frame to hold the components

# -------------- COMPONENTS --------------

folderTag = tk.Label(rootWindow, text=f"Current Save Folder: {saveFolder}") # label to show current save folder

textTitle = tk.Label(rootWindow, text="Lol Builder", font=("Arial", 24)) # main text of the window

analyzeButton = tk.Button(rootWindow, text="Analyze", command=scAndAnalyze) # button to analyze text

changeFolderButton = tk.Button(rootWindow, text="Change Save Folder", command=selectSaveFolder) # button to change save folder

analyzingTag = tk.Label(rootWindow, text="Analyzing...") # label to show when analyzing

analyzingTag.pack_forget() # hide the analyzing label initially

backButton = tk.Button(frame, text="Go back", command=goBack) # button to analyze text

global patchInput
patchInput = tk.Entry(rootWindow) # input field for the patch number

# -------------- PLACING COMPONENTS --------------

textTitle.pack(pady=20) # add title to window
changeFolderButton.pack(pady=10) # add change folder button to window
folderTag.pack(pady=10) # add folder tag to window
analyzeButton.pack(pady=10) # add analyze button to window
patchInput.pack(pady=10) # add patch input to window

# -------------- RUN --------------

rootWindow.mainloop() # starts the app