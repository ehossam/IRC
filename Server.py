import socket, select, sys, pdb
import Utilities as ut

if len(sys.argv)>=3:
	host=sys.argv[1]
	port=sys.argv[2]
else:
	print("Usage is to type python Server.py followed by the IP address for host followed by the port number to listen to\n")
	sys.exit(1)

listen_soc=ut.create_socket((host, int(port)))	#create the socket with the specified paramaters

connection_list = [sys.stdin]
connection_list.append(listen_soc)

hall=ut.Hall()
Player=ut.Player
Room=ut.Room

while True:
	rdpl, wrtpl, errsck = select.select(connection_list, [], [])	#read,write,error sockets
	for player in rdpl:
        	if player is listen_soc: # newly connected player
           		new_socket, add = player.accept()
            		new_player = Player(new_socket)
            		connection_list.append(new_player)
            		hall.hello_msg(new_player)
		elif player is sys.stdin: #Disconnect from clients	
			if "<quits>" in sys.stdin.readline():
				i=2				
				while i<len(connection_list):
					connection_list[i].socket.sendall(ut.QUIT_STRING)
					i=i+1				
				sys.exit(2)	
	        else: # new message	        
			msg = player.socket.recv(4096) #I set the reading buffer to this value whuch is suitable for messages
            		if msg:
                		hall.msg_handle(player, msg)
            		else:	#a client crashed
				hall.crash_handle(player)
                		player.socket.close()
                		connection_list.remove(player)
   	for sock in errsck: # check the error sockets
       		 sock.close()
        	 connection_list.remove(sock)
