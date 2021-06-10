from os import walk, rename, makedirs
from os.path import curdir, splitext
from posixpath import abspath, dirname, basename
from subprocess import DEVNULL, PIPE, Popen
import sys

def optimize(inputFolder):
    print("Optimizing folder: " + inputFolder)
    outputFolder = dirname(inputFolder) + "/" + basename(inputFolder) + "_optimized"

    makedirs(outputFolder, exist_ok=True)

    #TODO: read options from config file
    Popen(['magick', 'mogrify', 
        '-strip', 
        '-interlace', 'JPEG',
        '-format', 'jpg',
        '-colorspace', 'sRGB',
        '-sampling-factor', '4:2:0',
        '-quality', '75', 
        '-path', outputFolder,
        inputFolder + "/*\.jp*g"]).communicate()
    
    return(outputFolder)

def sevenzip(inputFolder):
    outputFolder = dirname(inputFolder)
    print("creating archive at " + outputFolder + " from " + inputFolder)
    system = Popen(
        ['7z', 'a', '-tzip', inputFolder, inputFolder]
        , stdout=DEVNULL
    )
    system.communicate()
    return(inputFolder + ".zip")

def packageCbz(file):
    print ("original filename: " + file)
    newExtension = ".cbz"
    name, _ = splitext(file)
    newName = name.replace("_optimized", "") + newExtension
    print("new name: " + newName)
    rename(file, newName)

def compressCbzs(path):
    for (dirpath, _, filenames) in walk(path):
        fileMatchers = ["JPG", "JPEG", "jpg", "jpeg"]
        files = [filename 
                for filename in filenames 
                if any(matcher in filename for matcher in fileMatchers)]

        if (len(files) > 0):   
            optimizedFolder = optimize(dirpath)
            zippedFolder = sevenzip(optimizedFolder)
            packageCbz(zippedFolder)
            
#TODO: prompt delete original and/or compressed folder
#TODO: unpack original cbr/cbz
#TODO: prompt to delete original cbr/cbz
#TODO: make optimization optional
        
#TODO: make this more robust
path = ""
if len(sys.argv) > 1:
    path = sys.argv[-1]
else:
    path = curdir

compressCbzs(path)
