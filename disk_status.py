#!/usr/bin/python
# -*- coding: utf-8 -*-

from shell import *
import re

DD_DEFAULT_SIZE = 500

RE_HDPARM_CACHED	= r'Timing cached reads:.+?= ([0-9.]+) (\w\w/sec)'
RE_HDPARM_BUFFERED	= r'Timing buffered disk reads:.+?= ([0-9.]+) (\w\w/sec)'
# DD Constants
RE_DD				= r'([0-9.,]+) (\w\w/s)'
# Smart Constants
RE_SMART_HEALTH		= r'SMART overall-health self-assessment test result: (\w+)'

def emptyFN(*args):
	pass

def printFN(arg):
	print arg


def status_hdparm(device, progressFN=emptyFN):
	progressFN(' Start: HDPARM')
	result = call(['hdparm', '-tT', device])
	# TODO: assertions
	cached = re.search(RE_HDPARM_CACHED, result).groups()
	buffered = re.search(RE_HDPARM_BUFFERED, result).groups()
	progressFN('Finish: HDPARM')
	return {
		'buffered_read' : inByte(*buffered),
		'cached_read' : inByte(*cached),
	}


def status_dd(path, testfile_mb=1000, progressFN=emptyFN):
	progressFN(' Start: DD')
	if os.path.exists(path):
		raise Exception('Path already exists: '+path)
	# Starting write
	progressFN(' Start: DD WRITE')
	result_write = shell('dd if=/dev/zero of={filename} bs=1M count={filesize} 2>&1'.format(filename=path, filesize=testfile_mb))
	progressFN('Finish: DD WRITE')
	#Starting read
	progressFN(' Start: DD READ')
	result_read = shell('dd if={filename} of=/dev/null 2>&1'.format(filename=path, filesize=testfile_mb))
	progressFN('Finish: DD READ')
	# Parsing reults
	speed_write = re.search(RE_DD, result_write).groups()
	speed_read = re.search(RE_DD, result_read).groups()
	rm_rf(path)
	progressFN('Finish: DD')
	return {
		'read' : inByte(*speed_read),
		'write' : inByte(*speed_write),
	}


def status_smart(device, progressFN=emptyFN):
	progressFN(' Start: SMART')
	result = call(['smartctl', '-H', device])
	status_txt = re.search(RE_SMART_HEALTH, result).groups()[0]
	progressFN('Finish: SMART')
	healthy = status_txt == 'PASSED'
	return {
		'healthy' : healthy,
		'status_string' : status_txt
	}


## Helper

UNIT_MAP = {
	'K' : 1000**1,
	'M' : 1000**2,
	'G' : 1000**3,
	'T' : 1000**4
}

def inByte(value, unit):
	# maybe value is a string? (It is. It is a string.)
	if type(value) == str or type(value) == unicode:
		value = float(value.replace(',', '.'))
	return value * UNIT_MAP[unit[0]]


import argparse

def main():
	parser = argparse.ArgumentParser(description='Test your drives n stuff')
	parser.add_argument('--hdparm',	metavar='device')
	parser.add_argument('--dd',		metavar='testfile,MB')
	parser.add_argument('--smart',	metavar='device')
	args = parser.parse_args()

	if args.hdparm:
		print status_hdparm(args.hdparm, printFN)

	if args.dd:
		path = None
		size = DD_DEFAULT_SIZE
		if args.dd.find(',') > 0:
			path, size = args.dd.split(',')
		else:
			path = args.dd
		path = path.strip()
		size = int(size)
		print status_dd(path, size, printFN)

	if args.smart:
		print status_smart(args.smart, printFN)

if __name__ == '__main__':
	main()
