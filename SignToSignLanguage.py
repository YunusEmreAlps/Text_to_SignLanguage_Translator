# Packages
import nltk
nltk.download('punkt')
from nltk import word_tokenize
import useless_words
from nltk.stem import PorterStemmer
import time
from shutil import copyfile
from difflib import SequenceMatcher
from selenium import webdriver
import shutil, sys  # copyfile

# CONSTANTS     
SIGN_PATH = "D:\\SignLanguage\\Signs"   
DOWNLOAD_WAIT = 7                       # bekleme süresi
SIMILIARITY_RATIO = 0.9                 # benzerlik orani
# Get words
def download_word_sign(word):
    # Download Firefox browser
    browser = webdriver.Firefox()
    browser.get("http://www.aslpro.com/cgi-bin/aslpro/aslpro.cgi")
    first_letter = word[0]
    letters = browser.find_elements_by_xpath('//a[@class="sideNavBarUnselectedText"]')
    for letter in letters:
        if first_letter == str(letter.text).strip().lower():
            letter.click()
            time.sleep(2)
            break

    # Show drop down menu ( Spinner )
    spinner = browser.find_elements_by_xpath("//option")
    best_score = -1.
    closest_word_item = None
    for item in spinner:
        item_text = item.text
        # if stem == str(item_text).lower()[:len(stem)]:
        s = similar(word, str(item_text).lower())
        if s > best_score:
            best_score = s
            closest_word_item = item
            print(word, " ", str(item_text).lower())
            print("Score: " + str(s))        
    if best_score < SIMILIARITY_RATIO:
        print(word + " not found in dictionary")
        browser.close()
        return
    real_name = str(closest_word_item.text).lower()

    print("Downloading " + real_name + "...")
    closest_word_item.click()
    time.sleep(DOWNLOAD_WAIT)
    in_path = "D:\\Downloads\\" + real_name + ".swf"
    out_path = SIGN_PATH + "\\" + real_name + ".mp4"
    convert_file_format(in_path, out_path)
    browser.close()
    return real_name

def convert_file_format(in_path, out_path):
    # Converts .swf filw to .mp4 file and saves new file at out_path
    from ffmpy import FFmpeg
    
    ff = FFmpeg(executable='C:\\Users\\Dell\\Desktop\\GitHub\\ffmpeg\\bin\\ffmpeg.exe',
    inputs = {in_path: None},
    outputs = {out_path: None})
    ff.run()

def get_words_in_database():
    import os
    vids = os.listdir(SIGN_PATH)
    vid_names = [v[:-4] for v in vids]
    return vid_names

def process_text(text):
    # Split sentence into words
    words = word_tokenize(text)
    # Remove all meaningless words
    usefull_words = [str(w).lower() for w in words if w.lower() not in set(useless_words.words())]
    return usefull_words


def merge_signs(words):
    # Write a text file containing all the paths to each video
    with open("vidlist.txt", 'w') as f:
        for w in words:
            global PLAY_VIDEO
            if(w != None):
                f.write("file '" + SIGN_PATH + "\\" + w + ".mp4'\n")
                PLAY_VIDEO = True
            else:
                PLAY_VIDEO = False
            
    command = "ffmpeg -f concat -safe 0 -i vidlist.txt -c copy output.mp4 -y"
    import shlex
    # Splits the command into pieces in order to feed the command line
    # command not working, we don't have a output
    args = shlex.split(command)
    import subprocess
    process = subprocess.Popen(args, shell=True)
    process.wait() # Block code until process is complete 
    shutil.copyfile("output.mp4",SIGN_PATH + "\\Output\\out.mp4") # copyfile(src, dst)

def in_database(w):
    db_list = get_words_in_database()
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    s = ps.stem(w)
    for word in db_list:
        if s == word[:len(s)]:
            return True
    return False


def similar(a, b):
    # Returns a decimal representing the similiarity between the two strings.
    return SequenceMatcher(None, a, b).ratio()

def find_in_db(w):
    best_score = -1.
    best_vid_name = None
    for v in get_words_in_database():
        s = similar(w, v)
        if best_score < s:
            best_score =  s
            best_vid_name = v
    if best_score > SIMILIARITY_RATIO:
        return best_vid_name
    
    
# Sign Language
text = str(input("Enter the text you would like to translate : \n"))
print("Text: " + text)
# Process text
words = process_text(text)
# Download words that have not been downloaded in previous sessions.
real_words = []
for w in words:
    real_name = find_in_db(w)
    if real_name:
        print(w + " is already in db as " + real_name)
        real_words.append(real_name)
    else:
        real_words.append(download_word_sign(w))
words = real_words
# Concatenate videos and save output video to folder
merge_signs(words)

# Play the video
if(PLAY_VIDEO == True):
    from os import startfile
    startfile(SIGN_PATH + "\\Output\\out.mp4")



















