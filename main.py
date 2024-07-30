import os
import eyed3
import urllib.request
import urllib
import re
from datetime import date
import yt_dlp as youtube_dl
import concurrent.futures
import xml.etree.ElementTree as ET


def sanitize_filename(filename):
    """
    Sanitize the filename by replacing invalid characters and truncating if necessary.
    """
    sanitized = re.sub(r'[\\/*?:"<>|\']', "", filename)
    return sanitized[:130]  # Truncate to 130 characters, which is a typical limit for many filesystems.


def metadata(path, title, artist, album):
    audiofile = eyed3.load(str(path))
    audiofile.tag.artist = artist
    audiofile.tag.title = title
    audiofile.tag.album = album
    audiofile.tag.description = "from youtube"

    audiofile.tag.save()


def parser(path):
    tree = ET.parse(path)
    root = tree.getroot()
    songs = []

    for dict_tag in root.findall('.//dict/dict/dict'):
        song = artist = album = None
        for i, child in enumerate(dict_tag):
            if child.tag == 'key' and child.text == 'Name':
                song = dict_tag[i + 1].text
            elif child.tag == 'key' and child.text == 'Artist':
                artist = dict_tag[i + 1].text
            elif child.tag == 'key' and child.text == 'Album':
                album = dict_tag[i + 1].text

        if song and artist and album:
            songs.append((sanitize_filename(song), sanitize_filename(artist), sanitize_filename(album)))

    return songs


def download_audio(url, artist, album, name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{artist}/{album}/{name[0].replace("/", "_")}.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except:
            download_audio(url, artist, album, name)


def search(song):
    query = song[0] + " - " + song[1] + " official audio"
    query = query.replace(" ", "+").encode()
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + str(query))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return "https://www.youtube.com/watch?v=" + video_ids[0]


def init(directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except FileExistsError:
        directory = str(input(f"A folder with the name {directory} already exists\n please enter a new name:"))
        init(sanitize_filename(directory))
    return str(directory)


def main(PATH):
    songs = parser(PATH)

    for song in songs:
        artist_dir = sanitize_filename(song[1])
        album_dir = sanitize_filename(song[2])
        full_dir = os.path.join(artist_dir, album_dir)
        init(full_dir)

    print(songs)
    links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(songs)) as executor:
        for song in songs:
            link = search(song)
            links.append(link)
            executor.submit(download_audio, str(link), sanitize_filename(song[1]), sanitize_filename(song[2]), song)

    print(links)
    for song in songs:
        metadata(rf"{sanitize_filename(song[1])}/{sanitize_filename(song[2])}/{song[0].replace('/', '_')}.mp3", song[0],
                 song[1], song[2])


if __name__ == '__main__':
    main(r'file/path/here.xml')  # your playlist's xml file
