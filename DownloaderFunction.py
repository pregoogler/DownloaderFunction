
from bs4 import BeautifulSoup
from requests import get, exceptions, Session, adapters
from reportlab.pdfgen.canvas import Canvas
from multiprocessing import Pool, freeze_support, cpu_count
from signal import signal, SIGINT, SIG_IGN
from ping3 import ping
from sys import exit as terminate
from shutil import rmtree
from os import chdir, mkdir, walk, name
from os.path import join
from PIL.Image import open as IMGOPEN
from re import sub
from click import clear as ClearWindow
from random import choice
from urllib.parse import urlparse
from zipfile import ZipFile


class HostHeaderSSLAdapter(adapters.HTTPAdapter):
    
    def resolve(self, hostname):
        dnsList = [
            '1.1.1.1',
            '1.0.0.1',
        ]
        resolutions = {'hiyobi.me': choice(dnsList)}
        return resolutions.get(hostname)


    def send(self, request, **kwargs):
        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        result = urlparse(request.url)
        resolvedIP = self.resolve(result.hostname)

        if result.scheme == 'https' and resolvedIP:
            request.url = request.url.replace(
                'https://' + result.hostname,
                'https://' + resolvedIP,
            )
            connection_pool_kwargs['server_hostname'] = result.hostname 
            connection_pool_kwargs['assert_hostname'] = result.hostname
            request.headers['Host'] = result.hostname

        else:
            connection_pool_kwargs.pop('server_hostname', None)
            connection_pool_kwargs.pop('assert_hostname', None)

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)


s = Session()

s.mount('https://', HostHeaderSSLAdapter())


baseURL = "https://hiyobi.me"

hParser = 'html.parser'

infoBanner = "[Hiyobi-Downloader]"

header = {
    'User-agent' : 'Mozilla/5.0',
    'Referer' : baseURL,
}


PrintInfo = lambda info: print(f"\n{infoBanner} {info}\n")


def InitPool():
    signal(SIGINT, SIG_IGN)


def CheckInternet():
    try:
        if ping('8.8.8.8') == None:
            terminate('인터넷 연결 또는 서버가 내려갔는지 확인하세요.')
    except ( OSError ):
        terminate('리눅스 사용자는 root권한을 이용해주세요.')


def PrintBanner():
    print(
'''
마지막 수정 날짜 : 2020/01/15
제작자 : kdr (https://github.com/kdrkdrkdr/)
.-. .-..-..-.  .-..----. .----. .-.
| {_} || | \ \/ //  {}  \| {}  }| |
| { } || |  }  { \      /| {}  }| |
`-' `-'`-'  `--'  `----' `----' `-'
      Hiyobi Downloader by kdr
''')



def PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + ' ' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total: 
        print()


def GetIMGsSize(imgPath):
    while True:
        try:
            img = IMGOPEN(imgPath)
            return img.size
        except:
            continue



def MakePDF(ImageList, Filename, DirLoc):
    c = Canvas(Filename)
    mask = [0, 0, 0, 0, 0, 0]

    if len(ImageList) == 1: 
        IMGsSize = GetIMGsSize(ImageList[0])
    else:
        IMGsSize = GetIMGsSize(ImageList[1])

    iWidth = IMGsSize[0]
    iHeight = IMGsSize[1]

    c.setPageSize((iWidth, iHeight))

    for i in range(len(ImageList)):
        pageNum = c.getPageNumber()
        c.drawImage(ImageList[i], x=0, y=0, width=iWidth, height=iHeight, mask=mask)
        c.showPage()

    c.save()
    rmtree(DirLoc, ignore_errors=True)


def MakeZIP(directory, ZipName):
    JPGPath = []
    for root, directories, files in walk(directory):
        for filename in files:
            filepath = join(root, filename)
            JPGPath.append(filepath)
    
    with ZipFile(ZipName, 'w') as z:
        for jpg in JPGPath:
            z.write(jpg)

    rmtree(directory, ignore_errors=True)



def GetSoup(url):
    while True:
        try:
            html = s.get(url, headers=header, ).text
            if 'cloudflare' in str(html).lower():
                continue
            else:
                return BeautifulSoup(html, hParser)

        except (exceptions.ChunkedEncodingError, exceptions.SSLError, exceptions.Timeout, exceptions.ConnectionError):
            pass
    


def FileDownload(filename, url):
    while True:
        try:
            with open(f"{filename}", 'wb') as f:
                resp = s.get(url, headers=header, ).content
                f.write(resp)
                break

        except ( exceptions.ChunkedEncodingError, 
                 exceptions.Timeout,
                 exceptions.ConnectionError ):
            continue



def MakeDirectory(DirPath):
    try:
        mkdir(DirPath)
    except FileExistsError:
        rmtree(DirPath, ignore_errors=True)
        mkdir(DirPath)
    finally:
        chdir(DirPath)
        
        

if __name__ == "__main__":
    freeze_support()
    if cpu_count() == 1:
        Pool(1, InitPool)
    else:
        Pool(cpu_count() - 1, InitPool)
