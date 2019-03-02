#! /usr/bin/env python3
import json, os
from time import sleep, time
from urllib import request
from math import floor

class ProgressBar:
	def __init__(self, maxValue=None, char=['', '#', ''], msg='', endMessage="", barLength=0, showPercent=False, showRemainingTime=False, showRemaining=False):
		self.maxValue = maxValue
		self.char = char
		self.barLength = barLength
		self.showPercent = showPercent
		self.showRemaining = showRemaining
		self.showRemainingTime = showRemainingTime
		self.endMessage = endMessage
		if msg != '':
			msg += ': '
		self.pattern = msg + '[%s]'
		self.update(0)
	def __enter__(self):
		self.starttime = time() * 1000
		return self
	def __exit__(self, excpetion_type, expetion_val, trace):
		term_size = os.get_terminal_size()
		if self.endMessage == '':
			print(('Finished after ' + str(round((time()*1000 - self.starttime)/1000, 3)) + ' s').ljust(floor(term_size.columns)))
		else:
			print((self.endMessage + ' after ' + str(round((time()*1000 - self.starttime)/1000, 3)) + ' s').ljust(floor(term_size.columns)))
	def update(self, currentValue, maxValue=None):
		if maxValue != None:
			self.maxValue = maxValue
		if currentValue > self.maxValue:
			self.maxValue = currentValue
		term_size = os.get_terminal_size()
		currentPercent = currentValue/self.maxValue*100
		if currentPercent == 0:
			currentPercent = 1
		temp = ''
		if self.showRemaining:
			temp += (' ' + str(currentValue) + '/' + str(self.maxValue)).ljust(len(str(self.maxValue))*2)
		if self.showPercent:
			temp += (' ' + str(round(currentPercent, 2)) + "%%").ljust(4)
		if self.showRemainingTime and hasattr(self, 'starttime'):
			temp += ' ' + str(round((time() * 1000 - self.starttime)/currentPercent*(100-currentPercent)/1000, 3))
		currentPattern = self.pattern + temp
		currentPatternLength = len(currentPattern) - 2
		lenChar0 = len(self.char[0])
		lenChar1 = len(self.char[1])
		lenChar2 = len(self.char[2])
		temp = ''
		barLength = term_size.columns - currentPatternLength
		if self.barLength == 0:
			if barLength >= lenChar0 + lenChar1 + lenChar2:
				temp = self.char[0] + self.char[1] * floor((barLength-lenChar2-lenChar0)/lenChar1/100*currentPercent) + self.char[2]
			elif barLength >= lenChar1 + lenChar2:
				temp = self.char[1] * floor((barLength-lenChar2)/lenChar1/100*currentPercent) + self.char[2]
			elif barLength == lenChar1:
				temp = self.char[1] * (barLength/lenChar1)
		else:
			temp = self.char[0] + self.char[1]*floor((self.barLength-lenChar0-lenChar2)/lenChar1/100*currentPercent) + self.char[2]
		temp = temp.ljust(barLength)
		print(currentPattern % temp, end="\r")

class myProgressBar(ProgressBar):
	def update_to(self, currentBlocks, blockSize, totalSize):
		self.update(currentBlocks*blockSize, totalSize)

class DownloadGitRelease:
	def __init__(self, username, repo_name, downloadTo=None):
		self.username = username
		self.repo_name = repo_name
		if downloadTo == None:
			downloadTo = os.path.abspath('.')
		self.downloadTo = downloadTo
		term_size = os.get_terminal_size()
		self.dimensions = (int(term_size.columns), int(term_size.lines))
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
	def __downloadFileWithProgressBar(self, url, localDir, filesize):
		with myProgressBar(filesize, ['', '=', '>'], 'Loading', 'Downloaded "' + url + '" to "' + localDir + '"', 0, True, True, True) as bar:
			request.urlretrieve(url, filename=localDir, reporthook=bar.update_to)
	def __downloadJson(self, url):
		return json.loads(self.__downloadFile(url))
	def download(self, releaseTag='', whitelist=[], statusMsg=False):
		term_size = os.get_terminal_size()
		self.dimensions = (int(term_size.columns), int(term_size.lines))
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
				print(self.status, end='\n')
				sleep(0.3)
			if statusMsg:
				self.__downloadFileWithProgressBar(fileList[file][0], os.path.join(self.downloadTo, file), fileList[file][1])
			else:
				with open(os.path.join(self.downloadTo, file), 'w') as f:
					f.write(self.__downloadFile(fileList[file][0]))
			downloadedSize += fileList[file][1]
			self.status = ('Downloading... ' + str(round(downloadedSize/totalSize*100, 3)) + '% done.').ljust(self.dimensions[0])
			if statusMsg:
				print(self.status, end='\r')
				sleep(0.3)
		self.status = "waiting...".ljust(self.dimensions[0])
		if statusMsg:
			print(self.status, end='\r')
			sleep(0.3)

class DownloadGitFiles(DownloadGitRelease):
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
	def __downloadFileWithProgressBar(self, url, localDir, filesize):
		with myProgressBar(filesize, ['', '=', '>'], 'Loading', 'Downloaded "' + url + '" to ' + localDir + '"', 0, True, True, True) as bar:
			request.urlretrieve(url, filename=localDir, reporthook=bar.update_to)
	def __downloadJson(self, url):
		return json.loads(self.__downloadFile(url))
	def download(self, whitelist=[], statusMsg=False):
		term_size = os.get_terminal_size()
		self.dimensions = (int(term_size.columns), int(term_size.lines))
		self.status = 'Downloading... 0% completed'.ljust(self.dimensions[0])
		if statusMsg:
			print(self.status, end='\r')
			sleep(0.3)
		filelist = self.__downloadJson('https://api.github.com/repos/'  + self.username + '/' + self.repo_name + '/contents')
		fileList = {}
		tmp = 0
		totalSize = 0
		self.status = 'Searching...'.ljust(self.dimensions[0])
		if statusMsg:
			print(self.status, end='\r')
			sleep(0.3)
		print()
		print(fileList)
		print(len(fileList))
		print()
		for file in filelist:
			if self.__checkFile(whitelist, file["name"]):
				fileList.update({file["name"]: [file["download_url"], int(file["size"])]})
				totalSize += int(file["size"])
				print(tmp)
			self.status = ('Searching... ' + str(round(tmp/(len(fileList)+1)*100)) + "% completed").ljust(self.dimensions[0])
			if statusMsg:
				print(self.status, end='\r')
				sleep(0.3)
			tmp += 1
		downloadedSize = 0
		try:
			percent = downloadedSize/totalSize*100
		except:
			percent = 1
		self.status = ('Downloading... ' + str(percent) + '% done.').ljust(self.dimensions[0])
		if statusMsg:
			print(self.status, end='\r')
			sleep(0.3)
		for file in fileList.keys():
			self.status = ("Downloading File " + file).ljust(self.dimensions[0])
			if statusMsg:
				print(self.status, end='\n')
				sleep(0.3)
			if statusMsg:
				self.__downloadFileWithProgressBar(fileList[file][0], os.path.join(self.downloadTo, file), fileList[file][1])
			else:
				with open(os.path.join(self.downloadTo, file), 'w') as f:
					f.write(self.__downloadFile(fileList[file][0]))
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
	print("This is just a module")
