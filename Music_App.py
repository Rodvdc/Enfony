from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import os
import time
import vlc
from mutagen.mp4 import MP4
import threading
import mutagen
from yt_dlp import YoutubeDL
import urllib.request
import ctypes

#TODO: include a shortcut to pause music
#TODO: Second artist of & doesn't show
#TODO: Add a queue instead of playing the next song that is on display

global Immortals
Immortals = {}

#TODO Add search bar
#TODO - IN PROGRESS Add option to edit song
#TODO Add an auto pause option / after amount of time

Root = Tk()
Root.title("Music App")
Root.resizable(width = False, height = False)


def Get_MusicPath():
    if not os.path.exists("paths.txt"):
        f = open("paths.txt", 'w')
        f.close()

    f = open("paths.txt", 'r+')
    lines = f.readlines()
    print("lines", lines)
    if (lines and "Music_Path:" in lines[0]):
        print("0", lines[0])
        path = lines[0].split(":", 1)[1]
    else:
        path = str(os.path.expanduser('~') + "\\Music\\")
        lines.insert(0, "Music_Path:"+path)
        for line in lines:
            f.write(line)
    f.close()
        
    return path.replace("\n", "")

#Important Variables
global Music_Path
Music_Path = Get_MusicPath()
FONT = ("MS ", 10, "bold")
Mus_Font = ("MS", 15)
Art_Font = ("MS", 10)
#Thumbnail_Folder = Music_Path + "Thumbnails/"

global Back_Img, Pause_Img, Play_Img, Next_Img
Back_Img = Image.open("Photos/Back.png").resize((90, 90)).crop((9, 27, 83, 63))
Back_Img = ImageTk.PhotoImage(Back_Img)
Pause_Img = Image.open("Photos/Pause.png").resize((90, 90)).crop((9, 27, 83, 63))
Pause_Img = ImageTk.PhotoImage(Pause_Img)
Next_Img = Image.open("Photos/Next.png").resize((90, 90)).crop((9, 27, 83, 63))
Next_Img = ImageTk.PhotoImage(Next_Img)
Play_Img = Image.open("Photos/Play.png").resize((90, 90)).crop((9, 27, 83, 63))
Play_Img = ImageTk.PhotoImage(Play_Img)


Songs = []      
Songs_Playing = []
Current_Song = "Nothing is playing"
        
def Clear():
    list = Root.grid_slaves()
    for i in list:
        i.destroy()
 
    list = Root.pack_slaves()
    for i in list:
        i.destroy()

def QUIT():
    global End
    End = True
    try:
        Songs_Playing[-1].stop()
    except:
        pass
    Root.quit()
    Root.destroy()
    exit()

def Setup():
    Clear()

    Library = Button(Root, text = "Library", width = 100, height = 2, bg = "white",
                     font = FONT, foreground = "red", cursor = "hand2", command = lambda: Get_Music("All", None)).pack()

    Album = Button(Root, text = "Albums", width = 100, height = 2, bg = "white",
                   font = FONT, fg = "red", cursor = "hand2", command = lambda: Get_Cat("Albu")).pack()

    Artist = Button(Root, text = "Artists", width = 100, height = 2, bg = "white",
                   font = FONT, fg = "red", cursor = "hand2", command = lambda: Get_Cat("Arti")).pack()
    
    Download_Button = Button(Root, text = "Download", width = 100, height = 2, bg = "white", 
                             font = FONT, foreground = "red", cursor = "hand2",
                             command = Download_Page).pack()
    Settings = Button(Root, text = "Settings", width = 100, height = 2, bg = "white",
                      font = FONT, foreground = "red", cursor = "hand2",
                      command = Settings_Page).pack()
    
    Quit = Button(Root, text = "Quit", width = 100, height = 2, bg = "white",
                  font = FONT, foreground = "red", cursor = "hand2",
                  command = QUIT)
    Quit.pack()

def Get_Cat(Category):
    #TODO maybe add some spacing pady in grid or outside
    Clear()
    
    Cat_Names = []
    
    Place = 1
    i = 0
    
    Files = (os.listdir(path = Music_Path))
    #TODO: Put the song names in dictionary with the category name as key
    #So that when loading the songs it doesn't have to re loop through all of them
    for File in Files:
        if ".mp3" in File or ".m4a" in File: 
            try:
                Song_Element = mutagen.File(Music_Path + File)[Category]
                if ("&" in Song_Element[0] or "," in Song_Element[0]):
                    Song_Element = Song_Element[0].split("&")
                    Song_Element = Song_Element[0].split(",")
                    for i in Song_Element:
                        i = i.strip()
                        if not(i in Cat_Names):
                            Cat_Names.append(i)
                else:
                    if not(Song_Element[0] in Cat_Names):
                        Cat_Names.append(Song_Element[0])
            except:
                pass
    Cat_Names.sort()

    Get_Music(Category, Cat_Names)
    
def Display_All(Canvas_Songs, Frame_Buttons, Key, Item):
    Song_Names = []
    Place = 0
    i = 0

    #TODO If it's an album: sort by track nr°/ If it's a year sort by year?
    
    Files = (os.listdir(path = Music_Path))

    if Key != "All" and isinstance(Item, list):
        for Element in Item:
            action = lambda x = Element: Get_Music(Key, x)
            #TODO Improve the layout (specifically: anchor)
            Button(Frame_Buttons, text = Element, width = 100, font = FONT, command = action, bg = "white", anchor = W).grid(row = Place, column = 0)
            Place += 1
        return            
   
    for File in Files:
        if ".mp3" in File or ".m4a" in File:
            Song_Info = mutagen.File(Music_Path + File)
            try:
                if Item:
                    if not(Item in Song_Info[Key][0]):
                        continue
            except:
                continue
            Songs.append(File)
            
            try:
                Name = Song_Info["Titl"][0]
            except:
                Name = File.replace(".mp3", "").replace(".m4a", "")
            Song_Names.append(Name)
            
            action = lambda x = i: Play_Music(x)    #i = index number of the song
            Player_Buttons = Button(Frame_Buttons, text = Song_Names[i], width = 100, bd = 0, bg = "white",
                                    font = Mus_Font, anchor = W, cursor = "hand2", command = action)
            action2 = lambda x = File: Edit_Interface(x)
            Edit_Button = Button(Frame_Buttons, text = "Edit", width = 3, bd = 0, bg = "white", font = Mus_Font, anchor = E, command = action2)
            try:
                Info = Song_Info["Arti"]
                Art_Name = ""
                for ArN in range(len(Info)):
                    Art_Name += Info[ArN]
                    if ArN != len(Info) - 1 :
                        Art_Name += ", "
            except:
                Art_Name = "None"
            Artist_Button = Button(Frame_Buttons, text = Art_Name, width = 137, padx = 3, bd = 0, bg = "white", borderwidth = 0,
                                   font = Art_Font, anchor = W, fg = "grey", cursor = "hand2", command = action)

            try:
                Art = Image.open(Music_Path + "Thumbnails/" + File.replace(".m4a", ".png")).resize((107, 60)).crop((24, 0, 84, 60))
            except:
                Art = Image.open("Photos/Default.jpg").resize((60, 60))
            Art = ImageTk.PhotoImage(Art)
            Immortals[Song_Names[i]] = Art
            
            Art_Button = Button(Frame_Buttons, image = Immortals[Song_Names[i]], bd = 0, anchor = N, cursor = "hand2", command = action)
            
            Place += 1
            Art_Button.grid(row = Place, column = 0, rowspan = 2, sticky = NW)
            Player_Buttons.grid(row = Place, column = 1, columnspan = 10)
            Edit_Button.grid(row = Place, column = 3)
            
            Place += 1
            Artist_Button.grid(row = Place, column = 1, columnspan = 5, pady = (0, 3))

            i += 1

def Get_Music(Selection, Detail):
    global Songs
    Clear()
    Songs = []

    if Selection != "All" and not isinstance(Detail, list):
        action = lambda: Get_Cat(Selection)
    else:
        action = Setup
    Back = Button(Root, text = "< Back", cursor = "hand2", font = FONT, command = action, fg = "red", width = 102, anchor = W, bg = "white")
    Back.grid(row = 0, column = 0, columnspan = 5)


    def Geometry(event):
        Canvas_Songs.configure(scrollregion = Canvas_Songs.bbox("all"), width = 809, height = 500) #OG width = 800, height = 500
    def on_mousewheel(event):
        Canvas_Songs.yview_scroll(int(-1*(event.delta/120)), "units")

    Frame_Songs = Frame(Root, width = 100)
    Frame_Songs.grid(row = 1, column = 0, columnspan = 5)

    Canvas_Songs = Canvas(Frame_Songs, bg = "white", highlightthickness = 0)
    Canvas_Songs.grid(row = 0, column = 0, sticky = "news")
    Frame_Songs.bind_all("<MouseWheel>", on_mousewheel)

    #FIXED IT'S THE FRAME BLOCKING THE LINE (From the canvas.create_line)
    Song_Scroll = Scrollbar(Frame_Songs, orient = VERTICAL, command = Canvas_Songs.yview)
    Canvas_Songs.configure(yscrollcommand = Song_Scroll.set)
    Frame_Buttons = Frame(Canvas_Songs, bg = "light grey")

    #TODO Increase loading speed?
    threading.Thread(target = Display_All, args = (Canvas_Songs, Frame_Buttons, Selection, Detail)).start()
    
    try:
        if Songs_Playing:
            global Current_Song
            TEXT = Current_Song.replace(".mp3", "")
            TEXT = TEXT.replace(".m4a", "")
            if Songs_Playing[-1].is_playing():
                Play_Image = Pause_Img
            else:
                Play_Image = Play_Img
        else:
            TEXT = "Nothing is playing"
            Play_Image = Play_Img
            
            
    except:
        TEXT = "ERROR"
        Play_Image = Play_Img
    
    Song_Label = Label(Root, text = TEXT, width = 72, height = 2, padx = 3, pady = 3, relief = RAISED, font = FONT).grid(row = 3, column = 0)

    Song_Scroll.grid(row = 0, column = 5, sticky = NS)
    Canvas_Songs.create_window((0, 0), window = Frame_Buttons, anchor = NW)
    Frame_Buttons.bind("<Configure>",Geometry)

    Back_Button = Button(Root, image = Back_Img, cursor = "hand2", command = lambda: Back_Next(-1)).grid(row = 3, column = 2)
    global Pause_Button
    Pause_Button = Button(Root, image = Play_Image, cursor = "hand2", command = Pause)
    Pause_Button.grid(row = 3, column = 3)
    Next_Button = Button(Root, image = Next_Img, cursor = "hand2", command = lambda: Back_Next(1)).grid(row = 3, column = 4)

    global Slider
    Slider = ttk.Scale(Root, length = 800, from_ = 0, to_ = 5000, orient = HORIZONTAL)
    Slider.configure(command = Slide)
    Slider.grid(row = 4, column = 0, columnspan = 5)

    
def Pause():
    global Waiting, Pause_Button, Length
    if Songs_Playing:
        Player = Songs_Playing[-1]
        try:
            Player.pause()
            if not(Player.is_playing()):
                print("Not playing")
                Pause_Button.configure(image = Pause_Img)
            else:
                Pause_Button.configure(image = Play_Img)
        except:
            pass
    else:
        Play_Music(0)
        Pause_Button.configure(image = Pause_Img)
        
def Back_Next(Direction):
    global Song_Index
    try:
        Play_Music(Song_Index + Direction)
    except:
        pass

def Wait(Length, Song_Index):
    #TODO: When not on the page when the song skips this thread stops working
    global End, Current_Time, Slider
    End = False
    Current_Song = Songs_Playing[-1]
    Amount = 5000
    Length -= 2
    if Length > 1:
        while (Length * 1000) > Current_Time:
            time.sleep(Length/Amount)
            Current_Time = Current_Song.get_time()
            #Slider.set(int(Current_Time/1000)) #if slider is == length of song (slider could equal length of song in ms
            #Slider.set(Current_Time * 5/Length)
            try:
                Slider.config(value = int(Current_Time * 5/Length))
            except:
                pass
            if End or Current_Song != Songs_Playing[-1]:
                break
    else:
        pass

    time.sleep(1)
    if Current_Time >= Length and Current_Song == Songs_Playing[-1] and not End:
        print("Hey")
        Song_Index += 1
        Play_Music(Song_Index)

#TODO: only update when slider is let go (pause when the slider is 'picked up')
def Slide(x):
    global Current_Time
    Player = Songs_Playing[-1]
    Length = Player.get_length()    
    x = int(float(x))
    Time = (Length) * (x/5000)
    Player.set_time(int(Time))    
    #Current_Time = Player.get_time()

def Stop_Prev(x):
    if Songs_Playing:
        Player = Songs_Playing[-1]
        Player.stop()
        print(Player, "stopped!")
    try:
        global End
        End = True
        #Waiting.join() #With the scale it just doesn't work
        Songs_Playing.remove(Player)
    except:
        print("Passed")
        pass
    
    #TODO: Add boolean Autoplay - set to true here. Else set it to false
    

def Play_Music(Index):
    global Label_Song, Length, Song_Index, Current_Song, Current_Time
    Song_Index = Index
    try:
        Song = Songs[Song_Index]
    except:
        Song_Index = 0
        Song = Songs[0]
    Song_Info = mutagen.File(Music_Path + Song)
    Player = vlc.MediaPlayer(Music_Path + Song)

    Stop_Prev(Player)
    Songs_Playing.append(Player)
    Player.play()
    Current_Time = 0
    Current_Song = Song
    global Pause_Button
    Pause_Button.configure(image = Pause_Img)
    TEXT = Song.replace(".mp3", "")
    TEXT = TEXT.replace(".m4a", "")
    try:
        pass
        Label_Song.configure(text = TEXT)
    except:
        Label_Song = Label(Root, text = TEXT, width = 72, height = 2, font = FONT, relief = RAISED,padx = 3, pady = 3)
        Label_Song.grid(row = 3, column = 0, columnspan = 2)

    Length = Song_Info.info.length
    global Waiting
    Waiting = threading.Thread(target = Wait, args=(Length,Song_Index,))
    Waiting.start()

#####################################################Editing###########################################################
#TODO: Put Edit as popup rather than replace
#would require a refresh of only that song (since title/artist could've been changed)

def Edit_File(File_Name, New_Info):
    Path = Music_Path + File_Name
    Args = ["Titl", "Arti", "Albu", "Date", "Genr", "Trac"]
    if ".m4a" in File_Name:
        Song = MP4(Music_Path + File_Name)
        for i in range(6):
            Text = New_Info[i].get()
            if Text:
                Song[Args[i]][0] = Text
            else:
                Song[Args[i]][0] = "None"
        Song.save()
    #Still doesn't work
    #Should it be saved differently?
    else:
        Song = mutagen.File(Music_Path + File_Name)
        for i in range(6):
            Text = New_Info[i].get()
            if Text:
                Song[Args[i]] = mutagen.id3.TextFrame(encoding=3, text=[Text])
            else:
                Song[Args[i]] = mutagen.id3.TextFrame(encoding=3, text=["None"])
        Song.save()

    
    Setup()
    
def Edit_Interface(File_Name):
    Clear()
    Button(Root, text = "< Back", width = 50, fg = "red", font = FONT, cursor = "hand2", command = Setup, bg = "white", anchor = W).pack()
    Song = mutagen.File(Music_Path + File_Name)
    Args_Name = ["Title", "Artist", "Album", "Date", "Genre", "Track"]
    Args = ["Titl", "Arti", "Albu", "Date", "Genr", "Trac"]
    New_Info = []
    for i in range(len(Args)):
        Label(Root, font = FONT, text = Args_Name[i] + ":", width = 50,padx = 3).pack()
        New_Info.append(Entry(Root, font = FONT, width = 50, justify = CENTER))
        try:
            if Args[i] == "Titl" and (False):
                New_Info[i].insert(0, File_Name.replace(".m4a", ""))
            else:
                New_Info[i].insert(0, Song[Args[i]][0])
        except:
            if Args[i] == "Titl":
                New_Info[i].insert(0, File_Name.replace(".m4a", ""))
            else:
                New_Info[i].insert(0, "None")
        New_Info[i].pack()
        
    Confirm = Button(Root, text = "Confirm Edit", fg = "black", bg = "#F0F0ED", font = FONT, width = 50, cursor = "hand2", command = lambda: Edit_File(File_Name, New_Info))
    Confirm.pack()
    
       
#####################################################Download Stuff####################################################

def Download_Page():
    Clear()
    r = 0
    Back = Button(Root, text = "< Back", width = 50, fg = "red", font = FONT, cursor = "hand2", command = Setup, bg = "white", anchor = W)
    Back.grid(row = r, column = 0, columnspan = 2)
    
    Args = ["Link", "Title", "Artist", "Album", "Date", "Genre", "Track"]
    Args_Labels = []
    Args_Inputs = []
    for i in range(len(Args)):
        Args_Labels.append(Label(Root, font = FONT, text = Args[i] + ":", width = 50,padx = 3))
        Args_Inputs.append(Entry(Root, font = FONT, width = 50, justify = CENTER))

        r+=1
        Args_Labels[i].grid(row = r, column = 0, columnspan = 2)
        r+=1
        Args_Inputs[i].grid(row = r, column = 0, columnspan = 2)
    Defaultbg = "#F0F0ED"

    r+=1
    Label(Root, font = FONT, text = "Download thumbnail?").grid(row = r, column = 0, columnspan = 2)
    r+=1
    Thumb_Rad = StringVar()
    Radiobutton(Root, text = "Yes", variable = Thumb_Rad, value = 1, indicator = 1).grid(row = r, column = 0, padx = 0)
    Radiobutton(Root, text = "No", variable = Thumb_Rad, value = 0, indicator = 1).grid(row = r, column = 1, padx = 0)
    r+=1
    
    Download = Button(Root, text = "Download", fg = "black", bg = "#F0F0ED", font = FONT, width = 50, cursor = "hand2", command = lambda: Download_Song(Args_Inputs, Thumb_Rad.get()))
    Download.grid(row = r, column = 0, columnspan = 2)

def Download_Song(Args_Inputs, Thumb_Download):
    #TODO Add ability to download playlists
            
    URL = Args_Inputs[0].get()
    Title = Args_Inputs[1].get()
    Artist = Args_Inputs[2].get()
    Album = Args_Inputs[3].get()
    Date = Args_Inputs[4].get()
    Genre = Args_Inputs[5].get()
    Track = Args_Inputs[6].get()
    Format = "m4a"
    Thumb_Download = int(Thumb_Download)
    print(Thumb_Download)
    try:
                  
        def Validate(Text):
            #TODO Find all the missing characters ( <, >, :, etc.)
            Text = Text.replace("/", "_")
            Text = Text.replace("?", "")
            Text = Text.replace("|", "_")
            Text = Text.replace("*", "_")
            Text = Text.replace("\\", "_")
            return Text
        

        Downloader = YoutubeDL({"format":Format})
        print("Extracting info...")
        x = Downloader.extract_info(URL, download = False)

        print (x)
        print("Setting metadata...")
        if Title and Artist:
            pass
        elif Title:
            Artist = x["channel"]
        elif Artist:
            Title = x["title"]
        else:
            Title = x["title"]
            Artist = x["channel"]
        File_Name = Artist + " - " + Title + ".m4a"
        print("That's done")

        if Thumb_Download:
            Thumbnail = x["thumbnail"]
            print("Thumbnail found")
            Thumbnail_Name = Artist + " - " + Title + ".png"
            print("Thumbnail name")
            urllib.request.urlretrieve(Thumbnail, Music_Path + "Thumbnails/" + Thumbnail_Name)
            print("url stuff")
        print("thumbnail done")
        Path = Music_Path + File_Name
        print("downloading")
        YoutubeDL({"format":Format, "outtmpl":Path}).extract_info(URL)
        print("Path done")
        Song_File = MP4(Path)
        Tags = [Title, Artist, Album, Date, Genre, Track]
        Song_Attribute = ["Title", "Artist", "Album", "Date", "Genre", "Track"]
        for i in range(len(Song_Attribute)):
            if not(Tags[i]):
                Tags[i] = "None"
            Song_File[Song_Attribute[i]] = Tags[i]
        Song_File.save(Path)
        Setup()
    except Exception as e:
        print(e)
        try:
            os.remove(Music_Path+"Thumbnails/"+Thumbnail_Name)
            os.remove(Path)
        except:
            pass
        ctypes.windll.user32.MessageBoxW(0, "Song didn't download properly!", "ERROR", 48)

######################################################Settings############################################################################################

def Save_Settings(Location):
    global Music_Path
    if Location[-1] != "\\" and Location[-1] != "/":
        Location = Location + "\\"

    with open("paths.txt", 'r') as f:
        lines = f.readlines()
        f.close()

    if (lines and "Music_Path" == lines[0].split(":", 1)[0]):
        lines[0] = "Music_Path:" + Location +"\n"
    else:
        lines.insert(0, "Music_Path:"+Location+"\n")

    with open("paths.txt", 'w') as f:
        for line in lines:
            f.write(line)
        f.close()

    Music_Path = Location
    Setup()    
        
def Settings_Page():
    #Music folder
    Clear()
    
    Back = Button(Root, text = "< Back", width = 50, fg = "red", font = FONT, cursor = "hand2", command = Setup, bg = "white", anchor = W)
    Back.grid(row = 0, column = 0, columnspan = 2)
    r=1
    Label_Folder = Label(Root, font = FONT, text = "Music folder location:", width = 50,padx = 3).grid(row = r, column = 0, columnspan = 2)
    r+=1
    Folder_Input = Entry(Root, font = FONT, width = 50, justify = CENTER)
    Folder_Input.insert(0, Get_MusicPath())
    Folder_Input.grid(row = r, column = 0, columnspan = 2)
    
    Defaultbg = "#F0F0ED"

    r+=1
    Save = Button(Root, text = "Save", fg = "black", bg = "#F0F0ED", font = FONT, width = 50, cursor = "hand2", command = lambda: Save_Settings(Folder_Input.get()))
    Save.grid(row = r, column = 0, columnspan = 2)





    
if __name__ == "__main__":
    Root.protocol('WM_DELETE_WINDOW', QUIT)
    Setup()
    Root.mainloop()

