#! /usr/bin/env python3
import json
from time import sleep
from urllib import request
from getDimensions import get_terminal_size

class DownloadGitRelease:
    def __init__(self, username, repo_name):
        self.username = username
        self.repo_name = repo_name
        self.dimensions = get_terminal_size()
        self.status = "waiting...".ljust(self.dimensions[0])
    def __checkFile(self, whitelist, filename):
        if whitelist != []:
            for whiteListedFile in whitelist:
                if whiteListedFile[0] == filename:
                    return True
        return False
    def __getFileMode(self, whitelist, filename):
        if self.__checkFile(whitelist, filename):
            for whiteListedFile in whitelist:
                if whiteListedFile[0] == filename:
                    return whiteListedFile[1]
    def __downloadFile(self, url):
        url = url.replace(' ', '%20')
        response = request.urlopen(url)
        return response.read()
    def __downloadJson(self, url):
        return json.loads(self.__downloadFile(url))
    def download(self, releaseTag='', whitelist=[], statusMsg=False):
        self.dimensions = get_terminal_size()
        self.status = 'Downloading... 0% completed'.ljust(self.dimensions[0])
        if statusMsg:
            print(self.status, end='\r')
            sleep(0.3)
        if not releaseTag == '':
            releaseList = self.__downloadJson('https://api.github.com/repos/'  + self.username + '/' + self.repo_name + '/releases')
            latest = False
        else:
            latest = True
            releaseList = self.__downloadJson('https://api.github.com/repos/'  + self.username + '/' + self.repo_name + '/releases/latest')
        tmp = 0
        self.status = 'Searching...'.ljust(self.dimensions[0])
        if statusMsg:
            print(self.status, end='\r')
            sleep(0.3)
        fileList = {}
        totalSize = 0
        if not latest:
            for release in releaseList:
                if release["tag_name"] == releaseTag:
                    for file in release["assets"]:
                        if self.__checkFile(whitelist, file["name"]):
                            fileList.update({file["name"]: [file["browser_download_url"], int(file["size"])]})
                            totalSize += file["size"]
                        self.status = ('Searching... ' + str(round((tmp/(len(release["assets"])+1)*100))) + "% completed").ljust(self.dimensions[0])
                        if statusMsg:
                            print(self.status, end='\r')
                            sleep(0.3)
                        tmp += 1
        else:
            for file in releaseList["assets"]:
                if self.__checkFile(whitelist, file["name"]):
                    fileList.update({file["name"]: [file["browser_download_url"], int(file["size"])]})
                    totalSize += file["size"]
                self.status = ('Searching... ' + str(round((tmp/(len(releaseList["assets"])+1)*100))) + "% completed").ljust(self.dimensions[0])
                if statusMsg:
                    print(self.status, end='\r')
                    sleep(0.3)
                tmp += 1
        downloadedSize = 0
        self.status = ('Downloading... ' + str(downloadedSize/totalSize*100) + '% done.').ljust(self.dimensions[0])
        if statusMsg:
            print(self.status, end='\r')
            sleep(0.3)
        for file in fileList.keys():
            self.status = ("Downloading File " + file).ljust(self.dimensions[0])
            if statusMsg:
                print(self.status, end='\r')
                sleep(0.3)
            content = self.__downloadFile(fileList[file][0])
            f = open(file, self.__getFileMode(whitelist, file))
            f.write(content)
            f.close()
            downloadedSize += fileList[file][1]
            self.status = ('Downloading... ' + str(round(downloadedSize/totalSize*100, 3)) + '% done.').ljust(self.dimensions[0])
            if statusMsg:
                print(self.status, end='\r')
                sleep(0.3)
        self.status = "waiting...".ljust(self.dimensions[0])
        if statusMsg:
            print(self.status, end='\r')
            sleep(0.3)

if __name__ == '__main__':
    downloadClient = DownloadGitRelease('AustrianProgrammer', 'mySecretCodingMethods')
    downloadClient.download(whitelist=[['code.zip', 'wb'], ['install.exe', 'wb']], statusMsg=True)
