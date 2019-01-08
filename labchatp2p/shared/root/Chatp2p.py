#!/usr/bin/python

# -*- coding: utf-8 -*-


from socket import *
from select import *
from sys import *
import re
port = 1664
id=824




def Start(s,username):

	msg = str(id+1000) + "\001" + "START\043" + username + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )

def Hello(s,username):

	msg = str(id+2000) + "\001" + "HELLO\043" + username + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )

####fonctions necessaires 	
def List_str(msglist):
	tmp_str=",".join(msglist)
	ip="("+tmp_str+")"
	return ip
	
def Str_list(msglist):
	lst_tmp=msglist[1:-1]
	lst=lst_tmp.split(",")
	if lst[0]=='':
		return []
	else:
		return lst
####	
def Ips(s,ipsList):
	msg = str(id+3000) + "\001" + "IPS\043" + List_str(ipsList) + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )


#affiche le nickname de la personne connecter et les adresse ip disponible sur le chat
def Receive_nickname_ips(s,datas,nick_sock):
	global iprecu
	global ipsList
	t_data=datas.split("\r\n")[:-1]

	for data in t_data :
		if data[:data.index('\001')] == str( id+2000 ):
			print "\033[32m"+data[data.index("\001")+1:]+"\033[0m"
			user=data[data.index("\043")+1:]
			nick_sock[user]=s
				
		if data[:data.index('\001')] == str( id+3000 ):
			print "\033[32m"+data[data.index('\001'):]+"\033[0m"
			ipsList = Str_list(data[data.index("\043")+1:])
			iprecu=True

#affiche le nickname de la personne connecter 
def Receive_nickname(s,data,nick_sock):
	global n
	if data[:data.index('\001')] == str( id+2000 ):
		print "\033[32m"+data[data.index("\001")+1:data.index('\r')]+"\033[0m"
		user=data[data.index("\043")+1: data.index('\r')]
		nick_sock[user]=s
		n=True
	
####Separateur : \001 pour separer  le code du messsage du data
####Separateur : \043 pour separer le nickname et le  message du data
def Send_nickname_ips(t,data,nick_sock,username):
	global ipsList
	#envoie le nickname et la liste des ips sur lequel on connecter  si on recoit un start
	if data[:data.index("\001")]==str(id+1000):
		print "\033[32m"+data[data.index("\001"): data.index('\r')]+"\033[0m"
		Hello(t, username )
		ipsList=getIps(nick_sock)		
		Ips(t, ipsList ) 
		username_peer = data[data.index("\043")+1 : data.index('\r')] 
		nick_sock[username_peer] = t
   #envoie le nickname si  on recoit un hello   					
	elif data[:data.index("\001")]== str(id+2000):
		print "\033[32m"+data[data.index("\001"):data.index('\r')]+"\033[0m"
		Hello( t, username )
		username_peer = data[data.index("\043")+1 : data.index('\r')] 
		nick_sock[username_peer] = t
	#else:
	#	print data[ data.index('\001')+1: data.index('\r')]
		#TO DO ..... TU traites les code id+4000  et id+5000

#afficher le message recu selon le cas bm ou pm
def Receive_pm_bm(data):
	if data[:data.index("\001")]==str(id+4000):
		print "\033[34m[PRIVATE]\033[0m"+data[data.index("\043"): data.index('\r')]					
	elif data[:data.index("\001")]== str(id+5000):
		print "\033[34m[BROADCAST]\033[0m"+data[data.index("\043"): data.index('\r')]


#envoyer un message unicast				
def Pm(data,nick_sock,banList,username):
	dataspl = data.split(" ")
	nick_destination = dataspl[1]
	if VerifNickname(nick_destination,nick_sock) and (not InBanList( nick_destination, banList )):
		datae=" ".join(dataspl[2:])
		msg = str( id + 4000 ) + "\001" + "PM\043" + username + "\043" + datae + "\r\n"
		nick_sock[nick_destination].send( msg.encode('utf-8') )


#envoyer un message en broadcast
def Bm( data, nick_sock,banList, nickname):
	dataspl = data[data.index(" ")+1:]
	datae = str( id + 5000) + "\001" + "BM\043" + nickname + "\043" + dataspl + "\r\n"

	for user,sock in nick_sock.items():
		if user not in banList:
			sock.send( datae.encode('utf-8') )
#ban user
def Ban( data,banList):

	dataspl = data.split(" ")
	nick = dataspl[1]
	banList.append(nick)
	print nick+" \033[34mIS BANNED !\033[0m"


#unban user	
def Unban( data,banList ):

	dataspl = data.split(" ")
	nick = dataspl[1]
	print nick+" IS UNBANNED !"
	banList.remove(nick)



def VerifNickname( nick, nick_sock ):
	
	if nick in nick_sock:
		return True
	else:
		print nick+"\033[34m IS UNKNOWN !\033[0m"
		return False
    
#verifie si l utilisateur et bannie ou paq
def InBanList( nick, banList ):

	if nick in banList:
		print " YOU CAN'T MESSAGE "+nick+" , HE IS BANNED !"
		return True
    
	return False

#gerer les entrees clavier
def Input(data,nick_sock,banList,username) :
	global chat
	if data[:4] == "quit":
		chat = False
	elif data[:3] == "ban":
		Ban(data,banList)
	elif data[:5] == "unban":
		Unban(data,banList)
	elif data[:2] == "pm":
		Pm(data,nick_sock,banList,username)
	elif data[:2] == "bm":
		Bm(data,nick_sock,banList,username)
	elif data[:4] == "help":
		HELP()
	else:
		print " WRONG COMMANDE !"


#methode qui permer de connecter a un autre pc		
def Connexion(username,ipDestination,nick_sock):
	s = socket()
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
	s.connect( (ipDestination, port) )
	Start(s,username)
	global iprecu 
	iprecu=False
	global ipsList
	ipsList=[]
	
	while not iprecu:
		datas=s.recv(1024).decode('utf-8')
		if datas:
			Receive_nickname_ips(s,datas,nick_sock)

	
	if len(ipsList)<>0:
		for ipp in ipsList: 
			sk = socket()
			sk.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
			sk.bind(("0.0.0.0", port))
			sk.connect( (ipp, port) )
			Hello( sk, username )
			global n
			n=False
			while not n:
				datas=sk.recv(1024).decode('utf-8')
				if datas:
					Receive_nickname(sk,datas,nick_sock)
					


#recupere la liste des ips apartir de la list des sockets connectees a notre machine	
def getIps(nick_sock):
	
	ips = []
	for sock in nick_sock.values():
		ip, prt= sock.getpeername()
		ips.append(ip)
	return ips



#methode qui permet d ecouter les connexion entrante ansi que l entree clavier

def Listening(s,username,nick_sock):
	global chat
	global ipsList
	global banList

	s.bind(('0.0.0.0', port))
	s.listen(4)
	socks=list(nick_sock.values())
	banList=[]
	evenements=socks
	evenements.append(stdin)
	evenements.append(s)
	chat=True

	while chat:
		try:
			lin,lout,lerr=select(evenements,[],[],0.05)
		except error:
			pass
		for t in lin :
			if t ==s :
				(c,addr)=t.accept()
				socks.append(c)
				#ipsList.append(addr[0])	
		    		
		
			elif t==stdin :
				data = stdin.readline().strip("\n")
				Input(data,nick_sock,banList,username)

			else: # someone is speaking
				data = t.recv(1024).decode('utf-8')
				if data:
					Send_nickname_ips(t,data,nick_sock,username)
					Receive_pm_bm(data)

			
								
	for soc in evenements:
		soc.close()
	print "------goodBye------"

def isIp4(adr):
    return re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", adr)		    		
def HELP():
	print "---------------------------------"
	print "quit pour clore toutes les connexions et quitter l application \r\n"
	print "pm nic msg pour envoyer a  nic le message msg \r\n"
	print "bm msg pour envoyer le message 'msg'  en broadcast \r\n"
	print "ban nic pour inscrire 'nic' dans la liste des bannis \r\n"
	print "unban nic pour sortir 'nic' de la liste des bannis.\r\n"
	

def USAGE():
	print " '"+argv[0]+ "' : listen for a connexion"
	print " '"+argv[0]+ " IP ': join a chat"


def Main():
	if len(argv)>2:
		USAGE()
		exit(1)
	
	s = socket()
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
	nick_sock={}
	#ipsList=[]

	username = raw_input( "Saisir votre Nickname >  " )
	

	if (len(argv) == 2) :
		if isIp4(argv[1]):
			ipDestination=argv[1]
			Connexion(username,ipDestination,nick_sock)
		else :
			print "WRONG FORMAT IP ADRESSE  !"
			exit(1)

	Listening(s,username,nick_sock)
Main()

