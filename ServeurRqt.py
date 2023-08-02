# --------------------------------------------------------------------------------
# Script:               srv_standalone.py
# Author:               SCH
# Review :              SCH
# Compatibility (1):    Python 3.7.9
# Compatibility (2):    
# Dependencies (1):     
# Dependencies (2):     
# --------------------------------------------------------------------------------

import socket, select, queue
import sys, os, platform, time, random
import requests
import json
from requests.auth import HTTPBasicAuth
STX = "\x02"
ETX = "\x03"

##################URL disponible#######################
url1 = r'https://'
    #Previsionnel
    #Liste des aménagements : 
        #Aussois : AUSSOH  Debit prévisionnel
        #Combe d’Avrieux : C.AVRH debit prévisionnel

url2 = r'https://'
	#Cote retenue Plan d’Aval : AUSSOHB03RE01mLH02NivVEGA
	#Turbiné Aussois G1/G2/G3 : AUSSOHG01TU01mDbtTb / AUSSOHG02TU02mDbtTb / AUSSOHG03TU03mDbtTb
	#Turbiné Combe d’Avrieux : C.AVRHS12CO01mDbtTbTot
	#Débit influencé horaire de l'Arc à Bramans : ORELLHB01RE01mDbtEntAm
	#Débit influencé horaire de l'Arc à Pont de Saint Gobain : AVRIEHB07RE01mDbtRivAmDTG

url3 = r'https://'
url4 = r'https://'
    #Liste des points 
        # Station Bramans
        #     Turbidité : 0000002145.0001
        # Station Aussois
        #     Turbidité : 0000002012.0001
        # Station secours Aussois
        #     Turbidité : 0000002201.0001
        # Station Avrieux
        #     Turbidité : 0000002144.0001
        # Station Pont de Saint Gobain
        #     Turbidité : 0000002205.0001
        # Oxygène Dissous : 0000002205.0002
        
url5 = r'https://'

Username = r'???'
Password = r'???'


### Function handle data
def handle_data(data):
    messages = []
    socket_buffer = ""

    while (data):
        # STX - search for start of message
        msg_start = data.find(STX)
        if (msg_start < 0):
            print ("incomplete message, no STX:", repr(data))
            socket_buffer = ""
            break

        # ETX - search for end of message
        msg_end = data.find(ETX)

        if (msg_end < 0):
            print ("incomplete message, no ETX:", repr(data))
            socket_buffer = data[msg_start:]


        # wrong ordered STX/ETX
        if msg_end < msg_start:
            print ("invalid message, ETX before STX:", repr(data))
            data = data[msg_start:]
            continue

        # protocol seems legit, look into playload/message
        message = data[msg_start+1:msg_end]     # "\x02TEST\x03\x02test" --> "TEST"
        data = data[msg_end+1:]                 # "\x02test"
        socket_buffer = data
        messages.append(message)
    #end while

    return_to_sender = ""

    for message in messages:

        # Message: <STX>Command:Parameters<ETX>     # STX/ETX removed
        cmd_and_param = message.split(":")          # example: GETVAR:1,2,800
        if len(cmd_and_param) < 2:
            print ("\nSyntax error: malformed protocol, no colon found:", cmd_and_param)
            return_to_sender += STX + "NACK" + ETX
            continue

        command = cmd_and_param[0]              
        param = cmd_and_param[1]                

        # Command:      GET_VALUE
        # Parameter:    unused
        # IN:           <STX>GET_VALUE:<ETX>
        # OUT:          <STX>GET_VALUE:<0-9><ETX>
        if (command == "GET_VALUE"):
            
            try :
                r1 = requests.get(url1,auth=HTTPBasicAuth(Username, Password),timeout=25)
                #r = requests.get(url,headers=headers, timeout=10)
                requestString1 = str(r1.text)
                #print (requestString1)
                
                requestJson1 = json.loads(requestString1)  #Request
                reqAussoh1 = requestJson1['items'][0]['programmes']['DcoT'][0]['value']
                if str(reqAussoh1) == "" : reqAussoh1 = "-1"
                #print ("Debit previsionnel Aussois = " + str(reqAussoh1))
                
                reqCombeAvrieux = requestJson1['items'][1]['programmes']['DcoT'][0]['value']
                if str(reqCombeAvrieux) == "" : reqCombeAvrieux = "-1"
                #print ("Debit previsionnel Combe Avrieux = " + str(reqCombeAvrieux))
                       
            except :
                reqAussoh1 = -1;
                reqCombeAvrieux = -1;
                print ("Fail on 1st URL, error code = 2")
                errorCode=2
          
            try:
                r2 = requests.get(url2,auth=HTTPBasicAuth(Username, Password), timeout=25)
                requestString2 = str(r2.text)
                #print(requestString2)
                
                requestJson2 = json.loads(requestString2)
                
                
                reqURL2CoteDeau = requestJson2['items'][0]['value']
                if str(reqURL2CoteDeau) == "" : reqURL2CoteDeau = "-1"
                #print ("Hauteur d'eau ="  + str(reqURL2CoteDeau))
                
                reqURL2TurbineG1 = requestJson2['items'][1]['value']
                if str(reqURL2TurbineG1) == "" : reqURL2TurbineG1 = "-1"
                #print ("Turbine G1 = " + str(reqURL2TurbineG1))
                
                reqURL2TurbineG2 = requestJson2['items'][2]['value']
                if str(reqURL2TurbineG2) == "" : reqURL2TurbineG2 = "-1"
                #print ("Turbine G2 = " + str(reqURL2TurbineG2))
                
                reqURL2TurbineG3 = requestJson2['items'][3]['value']
                if str(reqURL2TurbineG3) == "" : reqURL2TurbineG3 = "-1"
                #print ("Turbine G3 = " + str(reqURL2TurbineG3))
                
                reqURL2TurbineAvrieux = requestJson2['items'][4]['value']
                if str(reqURL2TurbineAvrieux) == "" : reqURL2TurbineAvrieux = "-1"
                #print ("Turbine Combe d'avrieux = " + str(reqURL2TurbineAvrieux))
               
                
                reqURL2debitArcBramans = requestJson2['items'][6]['value']
                if str(reqURL2debitArcBramans) == "" : reqURL2debitArcBramans = "-1"
                #print ("Debit Arc bramans = " + str(reqURL2debitArcBramans))
                
                reqURL2debitArcStGobain = requestJson2['items'][5]['value']
                if str(reqURL2debitArcStGobain) == "" : reqURL2debitArcStGobain = "-1"
                #print ("Debit Arc St Gobains = " + str(reqURL2debitArcStGobain))
                
            except : 
                reqURL2CoteDeau = -1
                reqURL2TurbineG1 = -1
                reqURL2TurbineG2 = -1
                reqURL2TurbineG3 = -1
                reqURL2TurbineAvrieux = -1
                reqURL2debitArcBramans = -1
                reqURL2debitArcStGobain = -1
                print ("Fail on 2nd URL, error code = 2")
                errorCode=2
          
            try:
                r4 = requests.get(url4,auth=HTTPBasicAuth(Username, Password), timeout = 25)
                requestString4 = str(r4.text)
                print (requestString4)
                
                requestJson4 = json.loads(requestString4)  #Request
                
                reqURL4TurbiBramans = requestJson4['items'][3]['items'][0]['valeur']
                if str(reqURL4TurbiBramans) == "" : reqURL4TurbiBramans = "-1"
                #print ("Turbi St Bramans = " + str(reqURL4TurbiBramans))  
                
                reqURL4TurbiAussois = requestJson4['items'][4]['items'][0]['valeur']
                if str(reqURL4TurbiAussois) == "" : reqURL4TurbiAussois = "-1"
                #print ("Turbi Aussois = " + str(reqURL4TurbiAussois)) 
                
                reqURL4TurbiAussoisSec= requestJson4['items'][1]['items'][0]['valeur']
                if str(reqURL4TurbiAussoisSec) == "" : reqURL4TurbiAussoisSec = "-1"
                #print ("Turbi Aussois sec = " + str(reqURL4TurbiAussoisSec)) 
                
                reqURL4TurbiAvrieux = requestJson4['items'][0]['items'][0]['valeur']
                if str(reqURL4TurbiAvrieux) == "" : reqURL4TurbiAvrieux = "-1"
                #print ("Turbi Avrieux = " + str(reqURL4TurbiAvrieux)) 
                
                reqURL4TurbiStGob= requestJson4['items'][5]['items'][0]['valeur']
                if str(reqURL4TurbiStGob) == "" : reqURL4TurbiStGob = "-1"
                #print ("Turbi St Gob = " + str(reqURL4TurbiStGob)) 
                
                reqURL4OxyStGob= requestJson4['items'][2]['items'][0]['valeur']
                if str(reqURL4OxyStGob) == "" : reqURL4OxyStGob = "-1"
                #print ("Oxy St Gob = " + str(reqURL4OxyStGob)) 
            
            ######ODRE !!!!  ###########
            #Turbi avrieux       -0000002144.0001
            #turbi sec aussois   -0000002201.0001
            #oxy dissous         -0000002205.0002
            #Turbi bramans       -0000002145.0001
            #turbi aussois       -0000002012.0001
            #turbi saint gobain  -0000002205.0001
            
            except: 
                reqURL4TurbiBramans = -1
                reqURL4TurbiAussois = -1
                reqURL4TurbiAussoisSec = -1
                reqURL4TurbiAvrieux = -1
                reqURL4TurbiStGob = -1
                reqURL4OxyStGob = -1
                
                print ("Fail on 4rd URL, error code = 2")
                errorCode=2
                
                
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            
         
            return_to_sender += STX + "GET_VALUE:" + str(reqAussoh1) + ETX \
                + STX + "a" + str(reqCombeAvrieux) + ETX \
                + STX + "b" + str(reqURL2CoteDeau)+ ETX \
                + STX + "c" + str(reqURL2TurbineG1) + ETX \
                + STX + "d" + str(reqURL2TurbineG2)+ ETX \
                + STX + "e" + str(reqURL2TurbineG3)+ ETX \
                + STX + "f" + str(reqURL2TurbineAvrieux)+ ETX \
                + STX + "g" + str(reqURL2debitArcBramans)+ ETX \
                + STX + "h" + str(reqURL2debitArcStGobain)+ ETX \
                + STX + "i" + str(reqURL4TurbiBramans)+ ETX \
                + STX + "j" + str(reqURL4TurbiAussois)+ ETX \
                + STX + "k" + str(reqURL4TurbiAussoisSec)+ ETX \
                + STX + "l" + str(reqURL4TurbiAvrieux)+ ETX \
                + STX + "m" + str(reqURL4TurbiStGob)+ ETX \
                + STX + "n" + str(reqURL4OxyStGob)+ ETX
                                            
            
            print ("Sending to client at ", current_time)  #Renvoi data
            continue
        #end Befehl GET_STATE

        # unknown command
        else:
            print ("Unknown command:", repr(message))
            return_to_sender += STX + "NACK" + ETX
            continue
        #end else
    #end for message

    return return_to_sender, socket_buffer
#end handle_data



###############################################################################
#            MAIN IS HERE
###############################################################################

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 4712))
server_socket.listen(1)
print("Server started & listening")
read_list = [server_socket]
write_list = []        
send_msg_queues = {}   
recv_msg_queues = {}   

while read_list: # is not empty

    readable, writable, errored = select.select(read_list, write_list, [], 0)

    # 1 readable
    for socket in readable:
        # Server Socket?
        if socket is server_socket:
            client_socket, address = server_socket.accept()
            client_socket.setblocking(0)
            
            read_list.append(client_socket)
            send_msg_queues[client_socket] = queue.Queue() 
            recv_msg_queues[client_socket] = queue.Queue()

            print (">> Connection established.")
            print ("Connected clients:", len(read_list)-1) # server socket included -> -1

        # Client Socket?
        else:
            data = ""
            try:
                data = socket.recv(4096).decode()
            except:
                data = ""

            # Client Socket: 
            if data:

                # buffer + new data
                previous_data = ""
                while ( not recv_msg_queues[socket].empty() ):
                    previous_data += recv_msg_queues[socket].get_nowait()
                data = str(previous_data) + str(data)

                # handle data
                send_data, previous_data = handle_data(data)

                # data to buffer
                if previous_data:
                    recv_msg_queues[socket].put(previous_data)

                # no response if 'send_data' is None/Empty
                if send_data:
                    send_msg_queues[socket].put(send_data)
                    if socket not in write_list:
                        write_list.append(socket)

            # Client Socket & No data: client has closed connection
            else:
                if socket in write_list:
                    write_list.remove(socket)
                if socket in read_list:
                    read_list.remove(socket)
                if socket in send_msg_queues:
                    del send_msg_queues[socket]
                if socket in recv_msg_queues:
                    del recv_msg_queues[socket]
                socket.close()			
                print ("<< Connection closed.")
                print ("Connected clients:", len(read_list)-1)
            #end else
        #end else
    #end for


    # 2 writeable
    for socket in write_list:
        while not send_msg_queues[socket].empty():
            msg = send_msg_queues[socket].get_nowait()
            try:
                if msg:
                    socket.sendall(str(msg).encode('utf8'))
            except:
                print ("Error on send:", socket)
                break
        #end while
        write_list.remove(socket)
    #end for


    # 3 errored, unused
    for socket in errored:
        print ("Errored:", socket)
        if socket in read_list:
            read_list.remove(socket)
        if socket in write_list:
            write_list.remove(socket)    
        del recv_msg_queues[socket]
        del send_msg_queues[socket]
        socket.close()


    #time.sleep(0.01)
    #print ("Sleeping for a while...")
    print("", end = '') #debug display cmd
    time.sleep(0.5)
        
#end while read_list
	
