import argparse
import filecmp
import json
import os
import random
import re
import shutil
import sys
from datetime import datetime

from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from exif import Image


class Error(Exception):
    def __init__(self, message):
        self.message = message


def validate_ip_form(ip_string):
    if not re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$').match(ip_string):
        raise argparse.ArgumentTypeError
    return ip_string


use_profile = False
backup_parser = None

if not use_profile:
    backup_parser = argparse.ArgumentParser(description='Performs the backup of a specific phone directory to another '
                                                        'specified directory.')
    backup_parser.add_argument('phone_ip', help='the IP of the device from which get the files to backup.',
                               type=validate_ip_form, metavar='phone_IP')
    backup_parser.add_argument('adb_key', help='the path were the ADB key of the specific Android device is stored.',
                               metavar='ADB_key', type=str)
    backup_parser.add_argument('backup_dir', help='the backup path of the folder in which the backup will be done.',
                               type=str, metavar='backup_folder')
    backup_parser.add_argument('phone_dir', help='the original directory where the images to backup are stored.',
                               type=str, metavar='phone_folder')
    backup_parser.add_argument('--temp_dir', help='the temp directory in which the incoming images of the '
                                                  'device will be stored.', type=str)
    backup_parser.add_argument('--max_android_files', help='specify the maximum number of files to backup.',
                               type=int)

args = backup_parser.parse_args()

# Defined values.
# Android-related paths.
phone_ip = args.phone_ip
adbkey_route = args.adb_key.replace("/", "\\")
# Last bar is important. Bar position is important.
android_path = args.phone_dir.replace("\\", "/")
# Final-backup related paths.
max_android_files = args.max_android_files or None
# Dependent-value for function.
bckpPath = args.backup_dir.replace("/", "\\")
# Dependent-value for function.
if args.temp_dir:
    temp_directory = args.temp_dir.replace("/", "\\")
else:
    temp_directory = os.path.join(os.path.split(bckpPath)[0], 'jabs_tmp')
# Check and prepare paths.
if not os.path.exists(adbkey_route):
    raise Error("The specified ADB key was not found.")
for path in [bckpPath, temp_directory]:
    if not os.path.exists(path):
        os.makedirs(path)


# Date object for images.
class Date(object):
    """docstring for Date."""

    # Initialization of Date
    def __init__(self):
        super(Date, self).__init__()
        self.year = None
        self.day = None
        self.month = None
        self.hour = None
        self.minute = None
        self.second = None

    # Methods for Date
    # Checks is Date objects has been initialized, return array of boolean.
    def is_initialized(self):
        y = False
        mo = False
        d = False
        h = False
        min = False
        s = False
        if self.year is not None:
            y = True
        if self.month is not None:
            mo = True
        if self.day is not None:
            d = True
        if self.hour is not None:
            h = True
        if self.minute is not None:
            min = True
        if self.second is not None:
            s = True
        if y and mo and d and h and min and s:
            return [True, y, mo, d, h, min, s]
        else:
            return [False, y, mo, d, h, min, s]

    # Covert a given string with format YYYYMMDDhhmmss
    def covert_continue(self, initial_str):
        # Checks possible date according to physics.
        if (int(initial_str[4:6]) <= 12) and (int(initial_str[6:8]) <= 31):
            self.year = int(initial_str[0:4])
            self.month = int(initial_str[4:6])
            self.day = int(initial_str[6:8])
            self.hour = int(initial_str[8:10])
            self.minute = int(initial_str[10:12])
            self.second = int(initial_str[12:14])

    # COPY PASTE STACKOVERFLOW
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


# Object for reduced info. files.
class AndroidPhoto(object):
    """docstring for androidPhoto."""

    def __init__(self):
        super(AndroidPhoto, self).__init__()
        self.name = None
        self.path = None
        self.size = None


# Object for the backup items
class Photo(object):
    """docstring for Photo."""

    # Initialization of Photo
    def __init__(self):
        super(Photo, self).__init__()
        self.directory = None
        self.name = None
        self.ddate = Date()
        self.size = None
        # Title
        self.tdate = Date()
        # EXIF #
        self.cdate = Date()

    # Methods for Photo
    # Checks existence of directory date. Return boolean.
    def is_ddate(self):
        if self.ddate.is_initialized()[0]:
            return True
        else:
            return False

    # Checks existence of title date. Return boolean.
    def is_tdate(self):
        if self.tdate.is_initialized()[0]:
            return True
        else:
            return False

    # Checks for creation (exif) date. Returns boolean.
    def is_cdate(self):
        if self.cdate.is_initialized()[0]:
            return True
        else:
            return False

    # Returns year (order preference: c - t - d)
    def get_year(self):
        return self.cdate.year or self.tdate.year or self.ddate.year or None

    # Returns month (order of preference c - t -d)
    def get_month(self):
        return self.cdate.month or self.tdate.month or self.ddate.month or None

    # Returns day (order of preference c - t - d)
    def get_day(self):
        return self.cdate.day or self.tdate.day or self.ddate.day or None

    # Returns hour (order of preference c - t - d)
    def get_hour(self):
        return self.cdate.hour or self.tdate.hour or self.ddate.hour or None

    # Returns minute (order of preference c - t - d)
    def get_minute(self):
        return self.cdate.minute or self.tdate.minute or self.ddate.minute or None

    # Returns second (order of preference c - t - d)
    def get_second(self):
        return self.cdate.second or self.tdate.second or self.ddate.second or None

    # Get image format
    def get_image_format(self):
        return os.path.splitext(self.name)[1]

    ##COPY PASTE STACKOVERFLOW
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def get_images(original_directory, suffixes, photos_per_move=None):
    """
    Scans a given directory searching for the given suffixes files (indexing looks like the most time-consuming action).
    :param original_directory: The original path where the images are located.
    :param suffixes: The suffixes of the files to be moved.
    :param photos_per_move: Number of files to move.
    :return: An array of Photo-type objects.
    """
    p_count = 0
    images_array = []
    for root, dirs, files in os.walk(original_directory):
        for file in files:
            for end in suffixes:
                if file.endswith(end):
                    if photos_per_move is not None and photos_per_move == p_count:
                        return images_array
                    else:
                        # Save actual file (image) info.
                        photo = Photo()
                        photo.directory = root
                        photo.name = file
                        d_numbers = os.path.getctime(os.path.join(root, file))
                        photo.size = os.path.getsize(os.path.join(root, file))
                        d_numbers = datetime.fromtimestamp(d_numbers).strftime(
                            '%Y%m%d%H%M%S')  # directory date, in Win the creation.
                        photo.ddate.covert_continue(d_numbers)
                        # Get Exif timestamp
                        actual_image = Image(open(os.path.join(root, file), 'rb'))
                        if actual_image.has_exif:
                            for exif_tag in dir(actual_image):
                                if exif_tag == 'datetime_original':
                                    # print("this works, you're amazing!")
                                    to_format = actual_image.datetime_original
                                    if isinstance(to_format, str):
                                        c_numbers = "".join(str(elem) for elem in list(filter(str.isdigit, to_format)))
                                        photo.cdate.covert_continue(str(c_numbers))
                        # Title timestamp
                        t_numbers = list(filter(str.isdigit, file))
                        if len(t_numbers) == 14:
                            t_numbers = "".join(str(elem) for elem in t_numbers)
                            photo.tdate.covert_continue(t_numbers)
                        # Add object to array.
                        images_array.append(photo)
                        p_count += 1
    return images_array


def log_pull_status(a, bytes_written=0, total_bytes=0):
    print(f"\rMoving {os.path.basename(a)} - {round(bytes_written / total_bytes * 100, 1)}%", end="")


def scan_phone_tcp(to_search_path, remote_ip, adb_key_file, max_files=None):
    """
    Search in the given directory for .jpg files and copy them to a temporarily folder.
    By default the 5555 port is used.
    After comparison, they're deleted from the original path.
    :param to_search_path: The path where the files are located.
    :param remote_ip: The IP of the device where the files are located.
    :param adb_key_file: The ADB key of the device to be connected.
    :param max_files: The number of files to be moved.
    :return: True
    """
    android_images = []
    with open(adb_key_file) as f:
        priv = f.read()
    signer = PythonRSASigner('', priv)
    device = AdbDeviceTcp(remote_ip, 5555, default_transport_timeout_s=100.)
    if device.connect(rsa_keys=[signer], auth_timeout_s=100.):
        if device.available:
            print("Connected to selected device.\n---")
        directory_scan = device.list(to_search_path, None, 9000)
        if max_files is None:
            max_files = len(directory_scan)
        for file in directory_scan:
            if os.path.splitext(file.filename.decode('utf-8'))[1] == ".jpg":
                save = AndroidPhoto()
                save.name = file.filename.decode("utf-8")
                save.size = file.size
                save.path = to_search_path
                android_images.append(save)
                if len(android_images) >= max_files:
                    break
    print(f"There're listed {len(android_images)} files.\n---")
    for image in android_images:
        device.pull(image.path + image.name, os.path.join(temp_directory, image.name),
                    progress_callback=log_pull_status,
                    transport_timeout_s=100, read_timeout_s=100)
        if image.size == os.path.getsize(os.path.join(temp_directory, image.name)):
            device.shell('rm -f ' + to_search_path + image.name)
            print("\r\r" + image.name + " is now in the temp folder.")
    print("---\nAll files are now in the temp folder.\n---")
    return True


def map_directory(home_path):
    """
    Map the backup directory.
    Scan a given directory for subfolders in the defined backup structure.
    :param home_path: the path to map.
    :return: (complex) Array
    """
    to_index = None
    for dirpath, dirnames, filenames in os.walk(home_path):
        if dirnames != []:
            if os.path.split(os.path.relpath(dirpath, home_path))[1] == os.path.relpath(home_path, home_path):
                to_index = dirnames
            else:
                for i, item in enumerate(to_index):
                    if os.path.relpath(os.path.split(dirpath)[0], home_path) == os.path.relpath(home_path, home_path):
                        if os.path.split(dirpath)[1] == item:
                            to_index[i] = [item, dirnames]
                    else:
                        if os.path.relpath(os.path.split(os.path.split(dirpath)[0])[0], home_path) == os.path.relpath(
                                home_path, home_path):
                            if type(item) == list:
                                if item[0] == os.path.split(os.path.relpath(dirpath, home_path))[0]:
                                    for x, month in enumerate(item[1]):
                                        if os.path.split(os.path.relpath(dirpath, home_path))[1] == month:
                                            to_index[i][1][x] = [month, dirnames]
    if type(to_index) == list:
        for z, eachYear in enumerate(to_index):
            if type(eachYear) == str:
                to_index[z] = [to_index[z], []]
            elif type(eachYear) == list:
                for d, eachMonth in enumerate(eachYear[1]):
                    if type(eachMonth) == str:
                        to_index[z][1][d] = [to_index[z][1][d], []]
    else:
        to_index = []
    return to_index


def search_directory(indexed_path, find_y, find_m, find_d):
    """
    Search for the existing Y, M and D folders.
    :param indexed_path: (complex) Array
    :param find_y: The year to find
    :param find_m: The month to find
    :param find_d: The day to find
    :return: Array [year, month, day, index, index, index]
    """
    is_year = False
    is_month = False
    is_day = False
    index_y = None
    index_m = None
    index_d = None
    for i, exst_y in enumerate(indexed_path):
        if type(exst_y) == str:
            if find_y == exst_y:
                is_year = True
                index_y = i
                break
        elif type(exst_y) == list:
            if exst_y[0] == find_y:
                is_year = True
                index_y = i
                for x, exst_m in enumerate(exst_y[1]):
                    if type(exst_m) == str:
                        if find_m == exst_m:
                            is_month = True
                            index_m = x
                            break
                    elif type(exst_m) == list:
                        if exst_m[0] == find_m:
                            is_month = True
                            index_m = x
                            for d, exst_d in enumerate(exst_m[1]):
                                if exst_d == find_d:
                                    is_day = True
                                    index_d = d
                                    break
    return [is_year, is_month, is_day, index_y, index_m, index_d]


def are_equal(original_f, copy_f):
    """
     Checks for differences in two files.
    :param original_f: should be a Photo type object.
    :param copy_f: is the final route of the file
    :return: Array of Booleans
    """
    equal_size = False
    if original_f.size == os.path.getsize(copy_f):
        equal_size = True
    py_compares = filecmp.cmp(os.path.join(original_f.directory, original_f.name), copy_f)
    equal_exif = None
    image_original_f = Image(open(os.path.join(original_f.directory, original_f.name), 'rb'))
    image_copy_f = Image(open(copy_f, 'rb'))
    if image_original_f.has_exif and image_copy_f.has_exif:
        if dir(image_original_f) == dir(image_copy_f):
            equal_exif = True
        else:
            equal_exif = False
    elif image_original_f.has_exif:
        equal_exif = False
    if equal_size and py_compares and ((equal_exif is None) or equal_exif):
        return [True, equal_size, py_compares, equal_exif]
    else:
        return [False, equal_size, py_compares, equal_exif]


print("---\nJABS, an open source backup system developed by Juan Cerdeño. Learn more at "
      "https://www.github.com/ajuancer/jabs.\n---")
# Start of program
scan_phone_tcp(android_path, phone_ip, adbkey_route, max_files=max_android_files)

# Prepare files.
initImages = get_images(temp_directory, ['.jpg'], photos_per_move=100)

openData = open(os.path.join(bckpPath, ("data_" + datetime.today().strftime("%M-%d-%m-%Y") + ".json")), "w+",
                encoding='utf-8')
openLog = open(os.path.join(bckpPath, ("log_" + datetime.today().strftime("%M-%d-%m-%Y") + ".txt")), "w+",
               encoding='utf-8')

# Copy photos to backup folder.
errorImages = []
movedImages = []
print("Organizing files (moving imgs to final location).\n---")
while len(initImages) != 0:
    for i, element in enumerate(initImages):
        directoryStatus = search_directory(map_directory(bckpPath), str(element.get_year()), str(element.get_month()),
                                           str(element.get_day()))
        if directoryStatus[0]:
            if directoryStatus[1]:
                if directoryStatus[2]:
                    # Check for same name
                    backupDirectory = os.path.join(bckpPath,
                                                   os.path.join(str(map_directory(bckpPath)[directoryStatus[3]][0]),
                                                                os.path.join(str(
                                                                    map_directory(bckpPath)[directoryStatus[3]][1][
                                                                        directoryStatus[4]][0]), str(
                                                                    map_directory(bckpPath)[directoryStatus[3]][1][
                                                                        directoryStatus[4]][1][
                                                                        directoryStatus[5]]))))
                    if os.path.exists(os.path.join(backupDirectory, element.name)):
                        os.rename(os.path.join(backupDirectory, element.name), os.path.join(backupDirectory,
                                                                                            os.path.splitext(
                                                                                                element.name)[
                                                                                                0] + "_" + str(
                                                                                                random.randint(0,
                                                                                                               40)) + "_" + str(
                                                                                                datetime.now().minute) + "_" + str(
                                                                                                datetime.now().second) +
                                                                                            os.path.splitext(
                                                                                                element.name)[1]))
                else:
                    # We don't have day folder.
                    try:
                        os.mkdir(
                            os.path.join(bckpPath, os.path.join(str(map_directory(bckpPath)[directoryStatus[3]][0]),
                                                                os.path.join(str(
                                                                    map_directory(bckpPath)[directoryStatus[3]][1][
                                                                        directoryStatus[4]][0]),
                                                                    str(element.get_day())))))
                    except FileExistsError:
                        print("We should review mapDirectory() #1")
                        openLog.write("We should review mapDirectory() #1\n")
                        sys.exit()
            else:
                # We don't have month folder.
                try:
                    os.makedirs(os.path.join(bckpPath, os.path.join(str(element.get_year()),
                                                                    os.path.join(str(element.get_month()),
                                                                                 str(element.get_day())))))
                except FileExistsError:
                    print("We should review mapDirectory() #2")
                    openLog.write("We should review mapDirectory() #2\n")
                    sys.exit()
        else:
            # We don't have even a year folder.
            try:
                os.makedirs(os.path.join(bckpPath, os.path.join(str(element.get_year()),
                                                                os.path.join(str(element.get_month()),
                                                                             str(element.get_day())))))
            except FileExistsError:
                print("We should review mapDirectory() #3")
                openLog.write("We should review mapDirectory() #3\n")
                sys.exit()
        # Move archive
        directoryStatus = search_directory(map_directory(bckpPath), str(element.get_year()), str(element.get_month()),
                                           str(element.get_day()))
        backupDirectory = os.path.join(bckpPath, os.path.join(str(element.get_year()),
                                                              os.path.join(str(element.get_month()),
                                                                           str(element.get_day()))))
        movedFile = None
        if directoryStatus[0] and directoryStatus[1] and directoryStatus[2] and not (
                os.path.exists(os.path.join(backupDirectory, element.name))):
            movedFile = shutil.copy2(os.path.join(element.directory, element.name), backupDirectory)
            if are_equal(element, movedFile)[0]:
                print(element.name + " has been moved successfully.")
                try:
                    os.remove(os.path.join(element.directory, element.name))
                    movedImages.append([element, movedFile])
                    removedFile = initImages.pop(i)
                    if not (removedFile == movedImages[-1][0]):
                        print("Something went wrong with the internal management #5")
                        openLog.write("Something went wrong with the internal management #5\n")
                        sys.exit()
                    else:
                        print("There're copied " + str(len(movedImages)) + ", there're " + str(
                            len(initImages)) + " left.")
                except IsADirectoryError:
                    print("Couldn't remove original file. #4")
                    openLog.write("Couldn't remove original file. #4\n")
                    sys.exit()
            else:
                print("Something went wrong with the internal management #6")
                openLog.write("Something went wrong with the internal management #6\n")
                sys.exit()
        else:
            print("Something else needs to be prepared. Hmm... that's strange. #7")
            openLog.write("Something else needs to be prepared. Hmm... that's strange. #7\n")
            sys.exit()

# Save results obtained. Should be done in a much proper way
for p, movedF in enumerate(movedImages):
    json.dump(movedF[0].toJSON(), openData, ensure_ascii=False, indent=4)  # save when something prints and close app
    json.dump(movedF[1], openData, ensure_ascii=False, indent=4)  # save when something prints and close app

print(f"---\nAll done! Navigate to {bckpPath} and see the results.")
