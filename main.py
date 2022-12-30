# _*_ coding:utf-8 _*_
import os
import os.path
import eyed3
import urllib.request
import urllib
import re
from datetime import date
import youtube_dl
import concurrent.futures


def metadata(path, title, artist, album):
    audiofile = eyed3.load(str(path))
    audiofile.tag.artist = artist
    audiofile.tag.title = title
    audiofile.tag.album = album
    audiofile.tag.description = "from youtube"

    audiofile.tag.save()


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def parser(path):
    names = []  # list of song names

    with open(path, 'r',encoding='UTF-8') as f:
        song = ''
        artist = ''
        playlist = ''
        playlist_flag = 0
        for line in f:
            if '<key>Name</key><string>' in line and not playlist_flag:
                song = line.strip().replace('<key>Name</key><string>', '').replace('</string>', '').replace('&#38;',
                                                                                                            '&')
            elif '<key>Artist</key><string>' in line:
                artist = line.strip().replace('<key>Artist</key><string>', '').replace('</string>', '').replace('&#38;',
                                                                                                                '&')
                names.append((song, artist))  # artist always comes after name so if artist is found append to list
            elif '<key>Playlists</key>' in line:
                playlist_flag = 1
            elif '<key>Name</key><string>' in line and playlist_flag:
                playlist = line.strip().replace('<key>Name</key><string>', '').replace('</string>', '').replace('&#38;',
                                                                                                                '&')
                return names, playlist


def download_audio(url, playlist, name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': "mp3",
        'outtmpl': f'{playlist[1:-1]}/{name[0]}.',
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '192',

        # }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except:
            download_audio(url, playlist, name)
    


def search(song):
    query = song[0] + " - " + song[1] + " official audio"
    query = query.replace(" ", "+").encode()
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + str(query))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return "https://www.youtube.com/watch?v=" + video_ids[0]


def init(playlist):
    try:
        playlist = playlist[1:-1]
        os.mkdir(playlist)
    except FileExistsError:
        playlist = str(input("A folder with that playlist name already exists\n please enter a new name:"))
        init(shellquote(playlist))
    return str(playlist)


def mainfunc(PATH):
    names, playlist = parser(f'{PATH}')
    playlist = shellquote(playlist)
    playlist = init(playlist)
    print(names)
    links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as executor:
        for song in names:
            link = search(song)
            links.append(link)
            executor.submit(download_audio, str(link), shellquote(playlist), song)
    print(links)
    albumname = f"{playlist} - {date.today()}"
    for name in names:
        metadata(rf"{playlist}/{name[0]}.mp3", f"{name[0]}", name[1], albumname)


mainfunc("Terraria.xml")  # your playlist's xml file