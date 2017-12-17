#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib.request
import curses
import time
import threading
from bs4 import BeautifulSoup
from PIL import Image


dir = './pictures'
SCREEN_WIDTH = 80
COUNT = 14
ASCII_1 = ['#', 'W', 'B', 'E', 'F', 'I', 'i', '_', ',', '.', ' ']
ASCII_2 = ['#', '?', '%', '.', 'S', '+', '.', '*', ':', ',', '@']
ASCII_CHARS = ASCII_2
asciiArts = []


def init():
    if (os.path.exists(dir)):
        files = os.listdir(dir)
        for i, file in enumerate(files):
            os.remove('{}/{}'.format(dir, file))
            pass
    else:
        os.mkdir(dir)

    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)

    print('inited')


def searchBing():
    count = str(COUNT)
    url = 'https://cn.bing.com/images/async?q=%E4%B8%87%E5%9C%A3%E8%8A%82&first=0&count={}&relp={}&lostate=r&mmasync=1&dgState=x*909_y*830_h*198_c*4_i*36_r*5&IG=C6930B7A591C42338CBEDC52874DE363&SFX=2&iid=images.5756'.format(count, count)
    req = urllib.request.Request(url)
    req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('accept-language', 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7')
    req.add_header('cookie', 'DSQ=count=0; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=9BE870879AB24128B376F8C5DD669E40; SRCHUSR=DOB=20170228; _EDGE_V=1; MUIDB=278D70247F486F1403DC7A137EE96EFF; SRCHUID=V=2&GUID=3CFB548EF2F2403195DAC5CE68089450&dmnchg=1; MUID=278D70247F486F1403DC7A137EE96EFF; ENSEARCH=BENVER=0&TIPBUBBLE=1; ULC=T=1B979|23:15&H=1B979|17:12; _UR=OMD=13157965824&MC=1&H17=0; _ITAB=STAB=TR; _EDGE_S=mkt=zh-cn&SID=26DB339ADAA061322B3238C1DB7C6027; ipv6=hit=1513515929475&t=4; _FP=hta=on; RMS=A=gUACEAAAAAAQ; SRCHHPGUSR=CW=1903&CH=479&DPR=1.100000023841858&UTC=480&WTS=63649108133; _SS=SID=26DB339ADAA061322B3238C1DB7C6027&bIm=495839&HV=1513512923')

    # req.add_header('accept-encoding', 'gzip, deflate, br')
    htmlBytes = urllib.request.urlopen(req).read()
    file = open('./a.html', 'wb')
    file.write(htmlBytes)
    file.close()
    print('searched')
    return htmlBytes


def findPictureAndSave():
    htmlBytes = searchBing()
    soup = BeautifulSoup(htmlBytes.decode('utf-8'), "html.parser")
    imgs = soup.select('img.mimg')
    print('count: {}'.format(len(imgs)))
    for i, img in enumerate(imgs):
        print(img['src'])
        imgData = urllib.request.urlopen(img['src']).read()
        path = '{}/{}'.format(dir, str(i))
        print(path)
        imgFile = open(path, 'wb')
        imgFile.write(imgData)
        imgFile.close()


def convert2ASCIIAndSave():
    imgPaths = os.listdir(dir)
    for i, imgPath in enumerate(imgPaths):
        ascii = convert2ASCII('{}/{}'.format(dir, imgPath))
        txtFile = open('{}/txt_{}.txt'.format(dir, i), 'w')
        txtFile.write(ascii)
        txtFile.close()


def convert2ASCII(path):
    image = Image.open(path)
    
    newWidth = SCREEN_WIDTH
    (width, height) = image.size
    aspectRatio = float(height) / width
    newHeight = int(aspectRatio * newWidth)
    newImage = image.resize((newWidth, newHeight))
    newImage = newImage.convert("L")

    step = 256 / len(ASCII_CHARS)
    newImageData = newImage.getdata()
    newImageASCII = "".join([ASCII_CHARS[int(pixelValue / step)] for pixelValue in newImageData])
    ascii = [newImageASCII[i: i + newWidth] for i in range(0, len(newImageASCII), newWidth)]
    finalASCII = '\n'.join(ascii)
    asciiArts.append(finalASCII)

    image.close()

    return finalASCII


def drawASCII():
    global x
    x = 0
    index = 0
    ascii = asciiArts[index]
    ascii2 = asciiArts[index + 1]
    asciiList = ascii.split('\n')
    asciiList2 = ascii2.split('\n')
    while True:
        (scrHeight, scrWidth) = stdscr.getmaxyx()

        # maxHeight = len(asciiList) if len(asciiList) > len(asciiList2) else len(asciiList2)
        # maxHeight = maxHeight if maxHeight > scrHeight else scrHeight

        # print(len(asciiList))
        # print(len(asciiList2))
        # print(scrHeight)
        # print(maxHeight)

        stdscr.clear()
        for i in range(0, scrHeight - 1):
            leftLen = SCREEN_WIDTH + x
            rightLen = -x
            if (i < len(asciiList)):
                stdscr.addstr(i, 0, asciiList[i][-x:len(asciiList[i])])
            if (i < len(asciiList2)):
                stdscr.addstr(i, leftLen, asciiList2[i][0:rightLen])
            # print(asciiList[i][-x:len(asciiList[i])])
        stdscr.refresh()

        x = x - 1
        if x < -SCREEN_WIDTH:
            index = index + 1
            if index == len(asciiArts) - 1:
                break
            x = 0
            ascii = asciiArts[index]
            ascii2 = asciiArts[index + 1]
            asciiList = ascii.split('\n')
            asciiList2 = ascii2.split('\n')

        # time.sleep(0.2)
        time.sleep(30 / 1000)


def end():
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    init()
    findPictureAndSave()
    convert2ASCIIAndSave()
    drawASCII()
    end()
