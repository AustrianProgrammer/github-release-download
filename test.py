#!/usr/bin/env python3

from DownloadGit import *
from time import sleep

with ProgressBar(100, ['', '=', '>'], 'Loading', 0, True, True, True) as bar:
	for i in range(0, 100):
		bar.update(i)
		sleep(0.05)
