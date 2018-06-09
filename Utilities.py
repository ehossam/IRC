#The design is based on a Hall->Room->Cleints structure

import socket,pdb

max_list=100
QUIT_STRING = '<$quit$>'

def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#TCP/IP connection
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(max_list)	#max number of incoming connections
    print("Host is set to listen at", address)
    return s


class Hall:
	def __init__(self):
		self.room_list={}	#the list of rooms	# {room_name: Room}
		self.room_map={}	#the list of players within each room	 # {playerName: roomName}
	
	def hello_msg(self,new_player):	#set a welcome message 
		new_player.socket.sendall('Welcome to Samanoudy Chat\nCan we know your name?\n')

	def list_rooms(self,player):
		if len(self.room_list)==0:	#let's make a new room
			msg='There are currently no active rooms in the chat\n' \
			   +'Please use <join> room_name to create a new room\n'
			player.socket.sendall(msg)
		else:
			msg='Listing all the rooms...\n'
			for room in self.room_list:	#list the rooms with the number of player each
				msg+=room+ ": " + str(len(self.room_list[room].players)) + " player(s)\n"
			player.socket.sendall(msg)
	def crash_handle(self,player):		#handle any crashes from the client side
		try:		
			if len(self.room_map[player.name].rooms)>=0:					
				for room in self.room_map[player.name].rooms:
					self.room_list[room].remove_player(player)
			del self.room_map[player.name]
        		print("Player: " + player.name + " has left\n")
		except:
			print("Player attempted to input a non-string value")
	def msg_handle(self,player,msg):
		instructions = 'Instructions:\n' + '[<manual>] to show instructions\n' +'[<listroom>] to list all rooms\n' + '[<join> room_name(s)] to join/create to a room\n' + '[<send> number_of_rooms list_of_room_names ur message] to send a message\n'+ '[<priv> user_name] to send a private message to a roomate\n'+'[<listplayers> room_name] to list all the players in a specific room\n'+'[<quit> room_name] to quit\n'+'\n'
		
		print("message from", player.name,":", msg)	#reflect on the server
		
		if "name:" in msg:	#new connection is coming
           	 	name = msg.split()[1]
          	  	player.name = name
			if player.name in self.room_map: #somewhere in the list
				player.socket.sendall(QUIT_STRING)
			else:
                       		self.room_map[name] = player
           			print("New connection from:", player.name)
           			player.socket.sendall(instructions) 
		
		elif "<join>" in msg:	#wants to join/create a room

			if len(msg.split()) <2: 	#used incorrectly
				player.socket.sendall('Usage is <join> followed by room_names seperated by a space each\n')
			else:
				index=1
				while index<len(msg.split()):
					room_change= True								
					room_name=msg.split()[index]
					index=index+1
					if player.name in self.room_map: #somewhere in the list
						for room in self.room_map[player.name].rooms:						
							if room == room_name:	#already there room
                        					player.socket.sendall('You are already in room: ' + room_name)
		                        			room_change = False
                   			
					if room_change:
						if not room_name in self.room_list: # new room:
                       				 	new_room = Room(room_name)
                       				 	self.room_list[room_name] = new_room
						self.room_list[room_name].players.append(player)
                    				self.room_list[room_name].hello_msg(player)
                  				self.room_map[player.name].rooms.append(room_name)
		elif "<listroom>" in msg:	#list room request
			self.list_rooms(player)
		elif "<listplayers>" in msg:	#list players within specified room
			if len(msg.split()) <2: 	#used incorrectly
				player.socket.sendall('Usage is <listplayers> followed by the room_name \n')
			else:
				room_name=msg.split()[1]
				if room_name in self.room_list:	#exists
					self.room_list[room_name].list_players(player)						
				else:						
					player.socket.sendall('It looks like you entered an invalid room name\n.Please try again\n')
		elif "<manual>" in msg:	#list instructions
			player.socket.sendall(instructions)
		elif "<quit>" in msg:	#quit the client
			done= False			
			if len(msg.split()) <2: 	#used incorrectly
				player.socket.sendall('Usage is <quit> followed by room_name\n')
			else:
				room_name=msg.split()[1]
				if len(self.room_map[player.name].rooms)==0:
					player.socket.sendall('No room to quit from\n')
				else:
					if len(self.room_map[player.name].rooms)==1:
						player.socket.sendall(QUIT_STRING)
					for room in self.room_map[player.name].rooms:
						if room is room_name:
	          					self.remove_player(player,room_name)
							done= True
					if not done:
						player.socket.sendall('You not in this room to quit\n')
		elif "<priv" in msg: #a private message
			if len(msg.split()) <2: 	#used incorrectly
				player.socket.sendall('Usage is <priv> followed by the name of the player who must be in the same room \n')
			else:
				flag=False
				dst=msg.split()[1]
				index=2			
				mesg=''	
				while index<len(msg.split()):
					mesg=mesg+msg.split()[index]+' '
					index=index+1			
				mesg=mesg+'\n'
				for room in self.room_map[player.name].rooms:
					if not flag:
						flag=self.room_list[room].private(player,dst,mesg)
				if not flag:
					player.socket.sendall('You should only use a valid name who is in one of ur rooms \n')
						
		elif "<send>" in msg:	#a message for the chat
			if len(msg.split()) <3: 	#used incorrectly
				player.socket.sendall('Usage is <msg> followed by number of rooms to sent to followed by room_names seperated by a space each \n')
			else:
				index=2
				num=index+int(msg.split()[1])
				i=num
				mesg=''	
				while i<len(msg.split()):
					mesg=mesg+msg.split()[i]+' '
					i=i+1
				mesg=mesg+'\n'
				while index <= num:								
					room_name=msg.split()[index]
					index=index+1
					if player.name in self.room_map: #somewhere in the list
						for room in self.room_map[player.name].rooms:						
							if room == room_name:	#already there room         		
								self.room_list[room].broadcast(player, mesg)
		else: #he sends random stuff without <send>
				if player.name in self.room_map: #somewhere in the list			
					if len(self.room_map[player.name].rooms)==1:
						self.room_list[self.room_map[player.name].rooms[0]].broadcast(player, msg)
					else:	
						errmsg='You have to specify which rooms to send your message to\n'+instructions
						player.socket.sendall(errmsg)	
				else:	#he has no rooms
               				errmsg ='You are currently not in any room!\n'
					errmsg=errmsg+instructions
                		 	player.socket.sendall(errmsg)
	def remove_player(self, player, room_name):	#method to remove the player from both roommap and roomlist
		if player.name in self.room_map:
			self.room_list[room_name].remove_player(player)
			for room in self.room_map[player.name].rooms:
				if room is room_name:
					self.room_map[player.name].rooms.remove(room)
			if len(self.room_map[player.name].rooms)==0:			
				del self.room_map[player.name]
        	print("Player: " + player.name + " has left\n")

class Room:
    	def __init__(self, name):
       		 self.players = [] # a list of connected players within a room
       		 self.name = name #name of the room

   	def hello_msg(self, from_player):
       		 msg = "Let's welcome "+from_player.name+ " into room "+self.name+' \n'        
	 	 for player in self.players:	#broadcast it to all users
            		player.socket.sendall(msg)
    
        def broadcast(self, from_player, msg):	#method to broadcast messages between users
        	msg = from_player.name + ": " + msg
        	for player in self.players:
            		player.socket.sendall(msg)
	
	def private(self,from_player,dst,msg):	#send a private message method
		msg = from_player.name + ": " + msg		
		for player in self.players:
			if dst==player.name:
            			player.socket.sendall(msg)				
				return True
    	def list_players(self,from_player):
		msg=''
		if len(self.players)==0:
			from_player.socket.sendall('Empty Room\n')				
		else:
			for player in self.players:					
				msg=msg+player.name+'\n'
			from_player.socket.sendall(msg)
    	def remove_player(self, player):
        	self.players.remove(player)
		msg = player.name+ " has left the room \n"        
		for player in self.players:	#broadcast it to all users that he left 
            		player.socket.sendall(msg)
class Player:
    	def __init__(self, socket, name = "new"):
        	socket.setblocking(0)
        	self.socket = socket
        	self.name = name
		self.rooms=[] #list of all rooms

    	def fileno(self):
        	return self.socket.fileno()					
