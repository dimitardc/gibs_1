from http.cookiejar import CookieJar
import urllib.request as urllib2
from bs4 import BeautifulSoup
import os
import json
from urls import url_dict
from earthdata_helper import login

DATA_DIR = '../../data/'
EARTHDATA_PROJECT_DIR = '../../src/earthdata_project/'
CONFIG_FILE_PATH = "../../config/user_config.json"

def select_date(date_links):
    print("Select a date by entering its index! You can look at the DATE_INDEX.txt for all the dates")
    index = int(input("Enter the index of the date you want to select: ")) - 1
    if index < 0 or index >= len(date_links):
        print("Invalid index! Please enter a valid index.")
        return select_date(date_links)
    return date_links[index]

def select_hdf_file(hdf_links):
    print("Select an HDF file by entering its index:")
    for i, hdf_file in enumerate(hdf_links, start=1):
        print(f"{i}: {hdf_file}")
    index = int(input("Enter the index of the HDF file you want to select: ")) - 1
    if index < 0 or index >= len(hdf_links):
        print("Invalid index! Please enter a valid index.")
        return select_hdf_file(hdf_links)
    return hdf_links[index]

def save_date_indices(date_links):
    with open(os.path.join(DATA_DIR, 'DATE_INDEX.txt'), 'w') as file:
        for i, date in enumerate(date_links, start=1):
            file.write(f"{i}: {date}\n")

def select_dir(dir_links):
    print("Select a sample")
    index = int(input("Enter the index of the sample you want to select: ")) - 1
    if index < 0 or index >= len(dir_links):
        print("Invalid index! Please enter a valid index.")
        return select_dir(dir_links)
    return dir_links[index]

def create_folder(new_dir):
    folder_name = os.path.join(DATA_DIR, new_dir)
    os.makedirs(folder_name, exist_ok=True)  

def read_html_page(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    
    body = response.read()

    html_object = BeautifulSoup(body, 'html.parser')
    links = html_object.find_all("a")

    dir_links = []
    file_links = []
    hdf_links = []
    found_parent_dir = False
    for link in links:
        if link.get_text() == "Parent Directory":
            found_parent_dir = True
            continue
        if link.get_text() == "NASA Web Privacy Policy and Important Notices ":
            break
        if found_parent_dir:
            href = link.get('href')
            if href and href.endswith("/"):
                if href not in dir_links:
                    dir_links.append(href)
            elif href and not href.endswith("/"):
                if href not in file_links and not href.endswith(('.hdf', '.h5', '.he5', 'HDF5')):
                    file_links.append(href)
                if href not in hdf_links and href.endswith(('.hdf', '.h5', '.he5', 'HDF5')):
                    hdf_links.append(href)
    print("DIRECTORIES: ", dir_links[:10])
    print("FILES: ", file_links[:10])
    print("HDF : ", hdf_links[:10])
    return dir_links, file_links, hdf_links

with open(CONFIG_FILE_PATH) as config_file:
    config = json.load(config_file)
    username = config["username"]
    password = config["password"]

# this is where you input a link 
url_0 = url_dict[1]

opener = login(username, password)

# file_links and hdf_links isnt used
dir_links, file_links, hdf_links = read_html_page(url_0)

save_date_indices(dir_links)

selected_date = select_date(dir_links)
print("Selected date:", selected_date)

create_folder(selected_date)

# date/files
url_1 = url_0 + selected_date

# the info inside the date folder
# at this level, there could be either directories which has the info inside
# or the info itself
dir_links, file_links, hdf_links = read_html_page(url_1)

# if there are directories inside the date folder
if dir_links:
    with open(os.path.join(DATA_DIR, selected_date, "ALL_DIRECTORIES_OUTPUT.txt"), "w") as file:
        for i, file in enumerate(dir_links, start=1):
            file.write(f"{i}: {file}\n")

    selected_dir = select_dir(dir_links)
    path_str = os.path.join(selected_date, selected_dir)
    create_folder(path_str)
    
    #date/dir/files
    url_2 = url_1 + selected_dir

    #reading inside the dir after date
    dir_links, file_links, hdf_links = read_html_page(url_2)
    os.chdir(os.path.join(DATA_DIR, path_str))
    if file_links:
        urllib2.urlretrieve(url_2, file_links[0])
        print(f"Downloaded: {file_links[0]}")
    if hdf_links:
        selected_hdf_file = select_hdf_file(hdf_links)
        print("Selected HDF file:", selected_hdf_file)
        urllib2.urlretrieve(url_2, selected_hdf_file)
        print(f"Downloaded: {selected_hdf_file}")
    os.chdir(os.path.join(EARTHDATA_PROJECT_DIR))

# if the files are inside the date folder and not inside other directories
elif file_links or hdf_links:
    os.chdir(os.path.join(DATA_DIR, selected_date))
    print(url_1)
    if file_links:
        urllib2.urlretrieve(url_1, file_links[0])
    if hdf_links:
        selected_hdf_file = select_hdf_file(hdf_links)
        print("Selected HDF file:", selected_hdf_file)
        urllib2.urlretrieve(url_1, selected_hdf_file)
        print(f"Downloaded: {selected_hdf_file}")
    os.chdir(os.path.join(EARTHDATA_PROJECT_DIR))
