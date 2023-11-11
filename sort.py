import re
from pathlib import Path
import sys
import shutil
from threading import Thread

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

registered_extensions = {'IMAGES': ['JPEG', 'PNG', 'JPG', 'SVG'],
                         'VIDEOS': ['AVI', 'MP4', 'MOV', 'MKV'],
                         'DOCUMENTS': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
                         'MUSIC': ['MP3', 'OGG', 'WAV', 'AMR'],
                         'ARCHIVES': ['ZIP', 'GZ', 'TAR'],
                         'OTHERS': []}
unknown_extensions = []
extensions = []
image_files_list = []
video_files_list = []
document_files_list = []
music_files_list = []
archive_files_list = []
other_files_list = []
folders = []


def get_extensions(file_name):
    """
    Return extension of the file without dot
    :param path: user path -> Path
    :return: str
    """
    return Path(file_name).suffix[1:].upper()


def normalize(name):
    """
    Normalize file name by transliterating to cyrillic, replacing invalid symbols to "_"
    :param name: user name -> str
    :return: str
    """
    name, extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{extension}"


def hande_file(file_name, folder, dist):
    """
    Move file in param file_name to the target folder = folder / dist
    :param file_name: user Path -> Path
           folder: user Path -> Path
           dist: user name -> str
    :return: None
    """
    target_folder = folder / dist
    target_folder.mkdir(exist_ok=True)
    file_name.rename(target_folder / normalize(file_name.name))


def handle_archive(path, folder, dist):
    """
    Unpack the archive  file in param path to the target folder = folder / dist
    :param path: user Path -> Path
           folder: user Path -> Path
           dist: user name -> str
    :return: None
    """
    target_folder = folder / dist
    target_folder.mkdir(exist_ok=True)

    norm_name = normalize(path.name).replace(".zip", '').replace(".gz", '').replace(".tar", '')

    archive_folder = target_folder / norm_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), archive_folder)
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def grabs_folder(folder):
    """
    Grabs all folders in folder
    :param folder: user path -> Path()
    :return: None
    """
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in registered_extensions.keys():
                folders.append(item)
                grabs_folder(item)


def scan(folder):
    """
    Scan all files in folder and sort by extensions
    :param folder: user path -> Path()
    :return: unknown_extensions -> list,
            extensions -> list,
            image_files_list -> list,
            video_files_list -> list,
            document_files_list -> list,
            music_files_list -> list,
            archive_files_list -> list,
            other_files_list -> list,
    """
    for item in folder.iterdir():
        if item.is_file():
            extension = get_extensions(file_name=item.name)
            new_name = folder / item.name
            if extension in registered_extensions['IMAGES']:
                image_files_list.append(new_name)
                extensions.append(extension)
            elif extension in registered_extensions['VIDEOS']:
                video_files_list.append(new_name)
                extensions.append(extension)
            elif extension in registered_extensions['DOCUMENTS']:
                document_files_list.append(new_name)
                extensions.append(extension)
            elif extension in registered_extensions['MUSIC']:
                music_files_list.append(new_name)
                extensions.append(extension)
            elif extension in registered_extensions['ARCHIVES']:
                archive_files_list.append(new_name)
                extensions.append(extension)
            else:
                other_files_list.append(new_name)
                unknown_extensions.append(extension)


def group_files(folder):
    """
    Group files in param folder
    :param folder: user Path -> Path
    :return: None
    """
    scan(Path(folder))

    for file in image_files_list:
        hande_file(file, folder, 'IMAGES')
    for file in video_files_list:
        hande_file(file, folder, 'VIDEOS')
    for file in document_files_list:
        hande_file(file, folder, 'DOCUMENTS')
    for file in music_files_list:
        hande_file(file, folder, 'MUSIC')
    for file in archive_files_list:
        handle_archive(file, folder, "ARCHIVE")
    for file in other_files_list:
        target_folder = folder / 'OTHERS'
        target_folder.mkdir(exist_ok=True)
        file.rename(target_folder / file.name)


def remove_empty_folders(path):
    """
    Remove empty folders
    :param path: user path -> Path
    :return: None
    """
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def main():
    path = sys.argv[1]
    print(f"Start in {path}")

    folders.append(Path(path))
    grabs_folder(Path(path))
    print(f"All folders: {folders}\n")

    threads = []
    for folder in folders:
        thread = Thread(target=group_files, args=(folder,))
        thread.start()
        threads.append(thread)

    [thread.join() for thread in threads]

    remove_empty_folders(Path(path))

    print(f"Image files: {image_files_list}\n")
    print(f"Video files: {video_files_list}\n")
    print(f"Document files: {document_files_list}\n")
    print(f"Music files: {music_files_list}\n")
    print(f"Archive files: {archive_files_list}\n")
    print(f"Unknown files: {other_files_list}\n")
    print(f"All extensions: {set(extensions)}\n")
    print(f"Unknown extensions: {set(unknown_extensions)}\n")


if __name__ == '__main__':
    main()