#!/bin/sh

#These are the steps required in order to Install ImageMagick with JPG, PNG and TIFF delegates.
sudo apt-get update 

#Install Build-Essential in order to configure and make the final Install
sudo apt-get install build-essential 

#basic JPG files
sudo apt-get install -y libjpeg62-dev 
#TIFF file format
sudo apt-get install -y libtiff-dev 
#PNG files
sudo apt-get install -y libpng-dev

#Download ImageMagick

MAGICK_TAR=ImageMagick.tar.gz
MAGICK_FOLDER=imagemagick
curl -o ${MAGICK_TAR} -LO https://www.imagemagick.org/download/ImageMagick.tar.gz

mkdir ${MAGICK_FOLDER}
tar -xzf ${MAGICK_TAR} -C ${MAGICK_FOLDER} --strip-components=1 
rm ${MAGICK_TAR}

cd ${MAGICK_FOLDER}


./configure --disable-shared
#Make and install
sudo make
sudo make install

#Display info of the instalation
identify -version