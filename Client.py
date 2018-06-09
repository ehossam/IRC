import socket,select,sys
import Utilities as ut

if len(sys.argv)>=3:
	host=sys.argv[1]
	port=sys.argv[2]
	server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    	server_connection.connect((host, int(port)))
else:
	print("Usage is to type python Client.py followed by the IP address for host followed by the port number to listen to\n")
	sys.exit(1)

socket_list = [sys.stdin, server_connection]

while True:
	rdsc,wrsc,errsck=select.select(socket_list, [], [])
	for s in rdsc:
		if s is server_connection:	#message is coming
			msg=s.recv(4096)
			if msg:
                		if msg == ut.QUIT_STRING:	#terminating msg
                    			sys.stdout.write('See u Later Dude\nHope you enjoyed our chat\n')
                    			sys.exit(2)
                		else:
                    			sys.stdout.write(msg)
                    		if 'Can we know your name?' in msg:
                        		msg_prefix = 'name: ' # prefix to the name of user
                    		else:
                        		msg_prefix = ''
                    		sys.stdout.write('>')	#for the input style
				sys.stdout.flush()
			else:	#server crashed
				print("It seems like server is not up now!\nPlease try soon\n")
				sys.exit(2)
		else:	#outgoing
            		msg = msg_prefix+sys.stdin.readline()
            		server_connection.sendall(msg)
	for sock in errsck: # check the error sockets
       		 sock.close()
        	 socket_list.remove(sock)
			
