import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import yt_dlp as youtube_dl
from concurrent.futures import ThreadPoolExecutor
from threading import *
import re
import subprocess
import os
import datetime

counter=0
max_counter = 0

checklist = []

download_path = str('D:/Music/new_music')

def get_chapter_info(video_url):
    with youtube_dl.YoutubeDL({}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        chapters = info_dict.get('chapters', [])
        return chapters
    
def convert_seconds_to_time(seconds):
    time_obj = datetime.timedelta(seconds=seconds)
    time_str = str(time_obj)
    if '.' not in time_str:
        time_str += '.000'
    return time_str
    
#def chop_video_into_chapters(chapters):
#    for chapter in chapters:
#        start_time = chapter['start_time']
#        end_time = chapter.get('end_time')
#        chapter_title = chapter['title']
#        output_filename = str(chapter_title) + '.mp3' 
#        
#        if end_time:
#            subprocess.run(['ffmpeg', '-i', 'video.mp4', '-ss', start_time, '-to', end_time, '-vn', '-acodec', 'libmp3lame', output_filename])
#        else:
#            subprocess.run(['ffmpeg', '-i', 'video.mp4', '-ss', start_time, '-vn', '-acodec', 'libmp3lame', output_filename])




def chop_video_into_chapters(chapter, video_path):
    video_path = video_path + '.webm'
    chapter
    start_time = convert_seconds_to_time(chapter['start_time'])
    end_time = convert_seconds_to_time(chapter['end_time'])
    chapter_title = chapter['title']
    output_filename = download_path +'/'+ str(chapter_title) + '.mp3' 
    
    command = ['ffmpeg', '-i', video_path, '-ss', start_time]
    
    if end_time:
        command.extend(['-to', end_time])
    
    command.extend(['-vn', '-acodec', 'libmp3lame', output_filename])
    
    subprocess.run(command)



def clean_tracklsit(string):
    tracklist_clean = []
    pattern = r'\b\d{1,2}:\d{2}\b'
    string = re.sub(pattern, '', string)
    #string = re.sub(':','',string)
    list = re.split("\n", string)
    list = [x for x in list if x not in ['',':',' ','/n']]
    for track in list:
        track = re.sub("\n",'',track)
        for i in range(5):
            if track[0] == ' ':
                track = track[1:]
            if track[-1] == ' ':
                track = track[:-1]
        tracklist_clean.append(track)
    return tracklist_clean

def button_press():
    global download_path
    dir = filedialog.askdirectory()
    download_path = dir
    btn_openpath_label['text'] = download_path

def hook(d):
    global counter
    string = d['filename']
    split = re.split("\.webm|\.m4a", string)[0]
    split_path = download_path + '/'
    split_path = split_path.replace('/','\\')
    split1 = split.replace(split_path,'')
    if ((d['status'] == "downloading")):
        counter_text['text'] = '(' + str(counter) +'/' + str(max_counter) + ')'
    if ((d['status'] == 'finished')):
        split1 = split1[:-5]
        if split1 not in checklist:
            text_label_finished['text'] = text_label_finished['text'] + '\n' + split1
            checklist.append(split1)
            counter += 1
            counter_text['text'] = '(' + str(counter) +'/' + str(max_counter) + ')'

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)

def download_video(search_query):
    if 'soundcloud' in search_query.lower():
        #template = '"%(title)s"'
        command = f'yt-dlp -P {download_path} {search_query}'
        print(command) 
        run_command(command)
        

    
    else:
        if flag != True:
            print(flag)
            print(search_query)
            path = download_path + '/%(title)s'
            ydl_opts = {
                'simulate': False,
                'skip_download': False,
                'quiet': False,
                'no_warnings': False,
                'default_search': 'ytsearch',
                #'format': 'bestaudio[filesize<=20M]',
                'outtmpl': path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                "progress_hooks" : [hook],
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(search_query, download=True)


    if flag == True:
        print(flag)
        chapters = get_chapter_info(search_query)
        print(chapters)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video.mp4',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(search_query, download=True)
            video_path = ydl.prepare_filename(info_dict)
        
        chop_video_into_chapters(chapters,video_path)       

def start_download():
    global counter
    global max_counter
    global flag

    counter = 0
    max_counter = 0
    flag = False

    tracklist_unclean = ''
    url = ''

    progressbar.start()
    eta_label['text'] = 'IN PROGRESS'

    url = ent_url.get()

    text_label_finished['text'] = 'Succesful Songs \n'
    
    tracklist_unclean = text_tracklist.get('1.0', 'end')
    # Use the youtube_dl library to download the video information
    ydl_opts = {
        'simulate': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    if len(url) > 0:
        flag = True
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        chapters = info.get("chapters", [])
        # Extract the chapters information from the video info
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'video.mp4',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)
        with ThreadPoolExecutor() as executor:
            for chapter in chapters:
                chapter_name = chapter["title"]
                text_tracklist.insert(1.0, chapter_name + '\n')
                max_counter = len(chapters)
                executor.submit(chop_video_into_chapters, chapter,video_path)
                

    
    if (len(tracklist_unclean) > 0) and (tracklist_unclean != '\n'):
        tracklist_clean = clean_tracklsit(tracklist_unclean)
        with ThreadPoolExecutor() as executor:
            for track in tracklist_clean:
                search_query = f'{track}'
                max_counter = len(tracklist_clean)
                executor.submit(download_video, search_query)

    progressbar.stop()
    eta_label['text'] = 'FINISHED'







def threading_start():
    t1=Thread(target=start_download)
    t1.start()

def close():
    window.destroy()


window = tk.Tk()
window.title('YT Helper')

photo = tk.PhotoImage(file = "folder1.png")

frm_entry = tk.Frame(master = window,padx=5,pady=5)
lbl_url = tk.Label(master = frm_entry, text="Album Link: ")
ent_url = tk.Entry(master=frm_entry,width=35)
lbl_url.grid(row=0,column=0, sticky="w")
ent_url.grid(row=0,column=1, sticky="w")


btn_openpath_frame = tk.Frame(master=window)
btn_openpath_label = tk.Label(master=btn_openpath_frame, text= download_path,width=40,anchor='e')
btn_openpath = tk.Button(master=btn_openpath_frame,image= photo,command=button_press)
btn_openpath_label.grid(row=0,column=0, sticky="e",)
btn_openpath.grid(row=0,column=1, sticky="e")

label_tracklist_frame = tk.Frame(window,padx=5,pady=5)
label_text_tracklist_label = tk.Label(label_tracklist_frame, text='Tracklist:')
label_text_tracklist_label.grid(row=0,column=0)

text_tracklist_frame = tk.Frame(window,padx=5,pady=5)
text_tracklist = tk.Text(text_tracklist_frame)
text_tracklist.grid(row=0,column=0)


btn_download_frame = tk.Frame(master=window,padx=5,pady=5)
btn_start = tk.Button(master=btn_download_frame,text="START",command= threading_start)
btn_start.grid(row=0,column=1,sticky=tk.S+tk.E)

text_frame_finished=tk.Frame(master=window,padx=5,pady=5)
text_label_finished = tk.Label(text_frame_finished,anchor='c')
text_label_finished['text'] = 'Succesful Songs \n'
counter_text = tk.Label(text_frame_finished)
counter_text['text'] = '(' + str(counter) +'/' + str(max_counter) + ')'
text_label_finished.grid(row=0,column=0,sticky=tk.N)
counter_text.grid(row=0,column=1,sticky='nw')


progressbar_frame = tk.Frame(master=window,padx=5,pady=5)
eta_label = tk.Label(progressbar_frame,text='')
progressbar = ttk.Progressbar(master=progressbar_frame,orient="horizontal",mode="indeterminate",length=100)
progressbar.grid(row=0,column=0)
eta_label.grid(row=0,column=1)

label_tracklist_frame.grid(row=0,column=0)
btn_openpath_frame.grid(row=0,column=1,sticky='ne')
text_tracklist_frame.grid(row=1,column=0)
text_frame_finished.grid(row=1,column=1,sticky='n')
frm_entry.grid(row=2,column=0,sticky='w')
progressbar_frame.grid(row=3,column=0,sticky="w")
btn_download_frame.grid(row=3,column=1,sticky='e')

window.protocol('WM_DELETE_WINDOW', close)

window.mainloop()