#!/usr/bin/python3

import argparse
import os
from os import walk, rename, makedirs
from os.path import  splitext
from posixpath import  dirname, basename
from subprocess import DEVNULL, PIPE, Popen

def compress(inputFolder):
    print("Compressing folder: " + inputFolder)
    outputFolder = dirname(inputFolder) + "/" + basename(inputFolder) + "_compressed"

    makedirs(outputFolder, exist_ok=True)

    #TODO: read options from config file
    Popen(['magick', 'mogrify', 
        '-strip', 
        '-interlace', 'JPEG',
        '-format', 'jpg',
        '-colorspace', 'sRGB',
        '-sampling-factor', '4:2:0',
        '-quality', '75', 
        #'-resize', '100%',
        '-path', outputFolder,
        inputFolder + "/*\.jp*g"], 
        stdout=DEVNULL, stderr=DEVNULL).communicate()
    
    return(outputFolder)

def sevenzip(inputFolder):
    outputFolder = dirname(inputFolder)
    print("creating archive at " + outputFolder + " from " + inputFolder)
    system = Popen(
        ['7z', 'a', '-tzip', inputFolder, inputFolder]
        , stdout=DEVNULL, stderr=DEVNULL
    ).communicate()
    return(inputFolder + ".zip")

def changeExt(file):
    newExtension = ".cbz"
    name, _ = splitext(file)
    newName = name.replace("_compressed", "") + newExtension
    print("creating file: " + newName)
    rename(file, newName)

def deleteCompressed(path):
    #find . -type d -name "*_optimized" -exec rm -rf {} \;

    folders = Popen(
        ['find', path, 
        '-type', 'd', 
        '-name', '*_compressed']
        , stdout=PIPE, stderr=DEVNULL
    ).communicate()[0]
    folders = Popen(
        ['sed', 's|\ |\\\ |g'], 
        stdout=PIPE, stderr=DEVNULL, stdin=PIPE
    ).communicate(folders)[0]

    Popen(
        ['xargs', 'rm', '-rf'], 
        stdout=DEVNULL, stderr=DEVNULL, stdin=PIPE
    ).communicate(folders) 
    
def deleteOriginals(path):
    #find . -name "*.jp*g" -exec dirname {} \; | sed 's|\ |\\ |g' | uniq  | grep -v _optimized | xargs rm -rf

    folders = Popen(
        ['find', path, 
        '-name', '*.jp*g', 
        '-exec', 'dirname', '{}', ';']
        , stdout=PIPE, stderr=DEVNULL
    ).communicate()[0]
    
    folders = Popen(
        ['sed', 's|\ |\\\ |g'], 
        stdout=PIPE, stderr=DEVNULL, stdin=PIPE
    ).communicate(folders)[0] 
   
    unique = Popen(
        ['uniq'], 
        stdout=PIPE, stderr=DEVNULL, stdin=PIPE
    ).communicate(folders)[0]

    filtered = Popen(
        ['grep', '-v', '_compressed'], 
        stdout=PIPE, stderr=DEVNULL, stdin=PIPE
    ).communicate(unique)[0]
    
    Popen(
        ['xargs', 'rm', '-rf'], stdout=DEVNULL, stdin=PIPE
    ).communicate(filtered)
    

def packageCbzs(path, doCompress, doPack):
    for (dirpath, _, filenames) in walk(path):
        fileMatchers = ["JPG", "JPEG", "jpg", "jpeg"]
        files = [filename 
                for filename in filenames 
                if any(matcher in filename for matcher in fileMatchers)]

        if (len(files) > 0):   
            zipPath = dirpath
            if (doCompress):
                zipPath = compress(dirpath)
            
            if (doPack):
                zippedFolder = sevenzip(zipPath)
                changeExt(zippedFolder)
            
#TODO: unpack original cbr/cbz
#TODO: prompt to delete original cbr/cbz
#TODO: original size comparison original/packaged

def createArgParser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=str, default=os.getcwd(), help="Input folder to pack, if empty, the working dir will be used")

    ap.add_argument("-p" , "--pack", action='store_true', required=False,
    help="Pack folders containing .jpg/.jpeg images into .cbz packages")

    ap.add_argument("-c", "--compress", action='store_true', required=False,
    help="If passed, lossy compression will be applied to the jpg images before packaging")

    ap.add_argument("-sc", "--store-compressed", action='store_true', required=False,
    help="If passed, the intermediate _compressed folders won't be deleted after completion")

    ap.add_argument("-dc", "--delete-compressed", action='store_true', required=False,
    help="If passed, the intermediate _compressed will be removed")

    ap.add_argument("-do", "--delete-originals", action='store_true', required=False,
    help="If passed, the original unpacked folders will be deleted after completion")

    return ap

argParser = createArgParser()
args = argParser.parse_args()

path = args.input
doPack = args.pack
doCompress = args.compress
storeCompressed = args.store_compressed
delCompressed = args.delete_compressed
delOriginals = args.delete_originals

if doPack | doCompress:
    packageCbzs(path, doCompress, doPack)
    if doCompress & (not storeCompressed):
        deleteCompressed(path)

if delCompressed:
    print("Deleting compressed folders")
    deleteCompressed(path)

if delOriginals:
    deleteOriginals(path)
