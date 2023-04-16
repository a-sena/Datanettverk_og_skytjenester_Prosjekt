import argparse # the argparse module is imported
import socket # the socket module is imported
import time # the time module is imported
import re # the re module is imported
import threading # the threading module is imported
import sys #sys module is imported
import ipaddress #ipaddress module is imported

#------------------------CHECK_IP FUNCTION STARTS HERE----------------------------------

#got help from https://github.com/safiqul/2410/blob/main/argparse-and-oop/ip_check.py
def check_ip(address):#checks dotted decimal notation
    #check if an address is a valid IP address
    try:
        val = ipaddress.ip_address(address)
        print("The IP address is valid")
        return str(val)
    except ValueError: #if address is not valid print error message
        raise argparse.ArgumentTypeError("The IP adress {} is not valid".format(address))
#------------------------CHECK_IP FUNCTION ENDS HERE----------------------------------

#------------------------CHECK_PORT FUNCTION STARTS HERE----------------------------------
#got help from https://github.com/safiqul/2410/blob/main/argparse-and-oop/optional-arg.py
def check_port(val):# checks port ranges and if port is in the correct format
    try: #check if the entered value is a integer
        value = int(val)
    except ValueError:#if user do not enter an integer value
        raise argparse.ArgumentTypeError("ERROR: Please enter an integer") #print error message
    if (value <= 0):#if the value is 0 and smaller than 0
        print("It is not a valid port") #print error message
        sys.exit() 
    elif 1024 <= value <= 65535: #If the value entered on the command line is within this range
        return value #Return the value entered in the command line
    raise argparse.ArgumentTypeError("The port number must be between 1024 and 65535")#if not print error message
#------------------------CHECK_PORT FUNCTION ENDS HERE----------------------------------

############### DEFINE_FLAGS FUNCTION STARTS HERE #######################################

def define_flags():#Function will parse flags to be entered on the command line
    #create the parser
    parser = argparse.ArgumentParser(description='Simpleperf:simplified version of iperf')
#I created mutually exclusive group here, either client or server can exist but not both at the same time
# I used this source here:
#https://stackoverflow.com/questions/59773946/argparse-required-add-mutually-exclusive-group-parameters-list-as-optional
    invoke_server_client = parser.add_mutually_exclusive_group(required=True)
    invoke_server_client.add_argument('-s', '--server', action='store_true', help='Allows to invoke server mode')
    invoke_server_client.add_argument('-c', '--client', action='store_true', help='Allows to invoke client mode')
# ------mutually exclusive group is finished------
#  I added arguments defined in portfolio1 here
# I specify the default values in the portfo1 description using "default"
#I specified the name of the attribute to be added to the object returned by parse_args() with the "dest"
# Flags are explained with the "help".
# I defined the type of arguments using "type="
 #But to check if the IP is valid with the "check_ip function", I typed the name of the function in the "type".
    parser.add_argument('-b', '--bind', type=check_ip, default='127.0.0.1', help='Allows to select the ip address of the server’s interface')
 # And I wrote the function name in type a to check if the port is in the specified range using the "check_port function"
    parser.add_argument('-p', '--port', type=check_port, default=8088, help='Allows to use select port number on which the server should listen')
    parser.add_argument('-f', '--format', type=str, default='MB', choices=['B', 'KB', 'MB','M'], help='Allows  to choose the format of the summary of results')
    parser.add_argument('-I', '--serverip', type=str, default='127.0.0.1', help='IP address of server')
    parser.add_argument('-t', '--time', type=int, default=25, help='The total duration in seconds for which data should be generated')
    parser.add_argument('-i', '--interval', type=int, help='Print statistics per z seconds', default=None)
# p value should be between 1 and 5, I specified it with the expression choices=range(1,6).
    parser.add_argument('-P', '--parallel', dest="no_of_conn", type=int, default=1, choices=range(1, 6), help='Allows to select the number of parallel connections')
    parser.add_argument("-n", "--num", dest="no_of_bytes", type=str, help="Allows to transfer number of bytes specfied ", default=0)
   #return parsed arguments
    return parser.parse_args()


############### HANDLE_CLIENT FUNCTION STARTS HERE #######################################

def handle_client(clientSocket, clientAddress, args): #takes clientSocket, clientAddress , args parameters in

    amount_of_bytes_received = 0 #This is a counter, it is put to keep track of amount of bytes received
    start_time = time.time() #time before starting to receive data

    while True:
        data = clientSocket.recv(1000) #receives data in the chunks of 1000 bytes
        if not data: #If amount_of_bytes_received is empty, break out of the loop.
            break

        if b'BYE'in data: #Break out the loop if the received data contains the message "BYE" 
            break

        amount_of_bytes_received += len(data) #add received data to amount_of_bytes_received counter
  
    end_time = time.time() #save current time when data retrieval completed.
    total_duration = end_time - start_time #receiving data is finished, calculate total duration
    #args.format is used to detect the unit specified by the user
    if args.format == "B": #if the user specified the format as Bytes 
        transfer_size = amount_of_bytes_received
    elif args.format == "KB":#if the user specified the format as Kilobytes 
        transfer_size = amount_of_bytes_received / 1000
    else: #If the user has specified the format as Megabytes(MB or M)
        transfer_size = amount_of_bytes_received / 1000000

   
    rate_server = (transfer_size * 8) / total_duration #calculate transfer rate on server side
    #Outputs to be printed on the server page
    print("{:<25} {:<10} {:<15} {:<15}".format("ID", "Interval", "Received", "Rate"))
    print("{0}:{1:<15} 0.0 - {2:.0f}       {3:.0f} {4:<2}      {5:.2f} Mbps".format(clientAddress[0], clientAddress[1], total_duration, transfer_size, args.format, rate_server))

    clientSocket.send(b"ACK: BYE") # message to client that indicates receiving data is finished
    clientSocket.close() #close the socket

############### SERVER FUNCTION STARTS HERE #######################################
def server(args):
    
    #create server socket
    #socket() method is used to create socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create a socket object
    ADDR=(args.bind,args.port)
    serverSocket.bind(ADDR) # binds socket to the specified IP address and port
    #After the socket is connected to a certain address, the listen() method is used to listen for requests from the specified port:
    serverSocket.listen(1)#allows 1 simultaneous connection

    print("-" * 60)
    #Prints a short message on which port the server is listening on
    print("A simpleperf server is listening on port {}".format(args.port))
    print("-" * 60)

    while True:

        try:
            clientSocket, clientAddress = serverSocket.accept() #Accept client connections

            print("-" * 60)
            #Prints a short message that the connection is established
            print("A simpleperf client with {}:{} is connected with {}:{}".format(clientAddress[0], clientAddress[1], args.bind, args.port))
            print("-" * 60)
            
            
            #Depending on how many clients are connected to the server, one or more threads are started.
            #handle_client function is specified as the target
            # used sources: 
            #https://stackoverflow.com/questions/47089723/socket-threading-thread-args-takes-exactly-1-argument-2-given
            t = threading.Thread(target=handle_client, args=(clientSocket, clientAddress, args)) 
            t.start() 

        except KeyboardInterrupt:#if user press Ctrl+C
            print("The server is stopping by the user.")
            break
    serverSocket.close()# close socket

#To write try-except I used this source:
#https://yasar11732.github.io/python/soket-socket-2.html
    
 ############### PARSE_SIZE FUNCTION STARTS HERE #######################################


def parse_size(val):
    unit_type = {'B': 1, 'KB': 1000, 'MB': 1000000,'M': 1000000} #define unit type
    # copied from portfolio-guidelines.pdf, side 30
    match = re.match(r"([0-9]+)([a-z]+)", val, re.I) 
    number, unit = match.groups()
    number = int(number) # converts string type to integer type.
    unit = unit.upper() # accept both mb and MB, b and B, kb and KB
    
    if unit in unit_type: # Checks if the unit value exists in the unit_type 
        return number * unit_type[unit]#After separating the number from the unit, the number is multiplied by 1, 1000 or 1000000.
    #if the unit value does not exist in unit_type, print error message
    else:
        
        raise ValueError(" ERROR: Please write an valid unit! {} is  invalid!! ".format(unit))
 #Used source:
 #https://stackoverflow.com/questions/2240303/separate-number-from-unit-in-a-string-in-python


############### CLIENT FUNCTION STARTS HERE #######################################
def client(args):
    def handle_single_connection():
        
#Creates socket in order to connect server 
#socket() method is used to create client socket
        ADDR=(args.serverip,args.port)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# create a socket object
        try:
            clientSocket.connect(ADDR)
            clientAddress = clientSocket.getsockname()

            print("Simpleperf client connecting to server {0}, port {1}".format(ADDR[0], ADDR[1]))

            start_time = time.time() #Start time when client connects to server

            amount_of_bytes_sent = 0 #This is a counter, it is put to keep track of amount of bytes sent
            print("-" * 60)
            print("ID                        Interval   Transfer        Bandwidth")#Prints headers
            
            # Num (-n) flag 
            #If the user specifies the size of data to be sent:
            if args.no_of_bytes:
                #data_size_entered:data size written on the command line
                data_size_entered = parse_size(args.no_of_bytes)
                #The loop continues until the amount_of_bytes_sent value reaches the data size written on the command line
                while amount_of_bytes_sent < data_size_entered:
                    data = bytes(1000) #send data in the chunks of 1000 bytes
                    clientSocket.sendall(data)
                    amount_of_bytes_sent += len(data) #add amount of sent data to amount_of_bytes_sent counter
            
            else:
                #interval flag
                if args.interval:
                    interval_start_time = start_time #define interval start time
                    interval_bytes_sent = 0 #track the amount of bytes sent at each interval
    #for i in range(start, stop , step)
    #https://stackoverflow.com/questions/60131021/understanding-interval-function-and-its-parameters-in-python-hetlands-book-exam
    #https://www.softwaretestinghelp.com/python-range-function/

                    for i in range(args.interval, args.time + args.interval, args.interval):#continues until the specified t value is passed, step is equal to the value of the entered i flag
                        
    #Data will be sent until the specified i value has passed
                        while time.time() - interval_start_time <= args.interval: 
                            data = bytes(1000) # send data in the chunks of 1000 bytes
                            clientSocket.sendall(data)
                            amount_of_bytes_sent += len(data) #add amount of sent data to amount_of_bytes_sent counter
                            interval_bytes_sent += len(data) #add amount of sent data to interval_bytes_sent counter
                        duration=args.interval #duration is args.interval
                        rate_client = (interval_bytes_sent * 8) / (duration * 1000000) #Calculate the transfer rate for each interval
                        #print 0-5, 5-10, 10-15, 15-20, 20-25
                        #sending data at regular intervals takes place on the terminal page we invoked the client
                        print("{:<25} {:<10} {:<15} {:.2f} Mbps".format("{}:{}".format(clientAddress[0], clientAddress[1]), "{}-{}".format(i - args.interval, i), "{:.1f} MB".format(interval_bytes_sent / 1000000), rate_client))
                        interval_bytes_sent = 0
                        interval_start_time = time.time()
                ##if n or i flag is not defined in the command line
                else: 
                    while time.time() - start_time <= args.time: #Data will be sent until the specified t value has passed, and the sending will stop after t time has passed.
                        data = bytes(1000 )# send data in the chunks of 1000 bytes
                        clientSocket.sendall(data)
                        amount_of_bytes_sent += len(data)#add amount of sent data to amount_of_bytes_sent counter
            #data sending is completed and the client sends the message "BYE" to the server 
            clientSocket.sendall(b'BYE')

            while True:
                data = clientSocket.recv(1000)
                if b"ACK: BYE" in data: #If client receives acknowledgment from server, break
                    break
                
    #the client receives the acknowledgment from the server and the socket is closed
            clientSocket.close()

            
        
    #client calculates statistics and prints the statistics on the client page.
            end_time = time.time() #current time when transfer is finished
            total_duration_client = end_time - start_time #the differance will give duration
            total_size = amount_of_bytes_sent / 1000000 #calculate total_size
            rate_client = (total_size * 8 ) / total_duration_client #calculate bandwidth 
            print("-" * 60)
            #print measurements
            print("{:<25} {:<10} {:<15} {:.2f} Mbps".format("{}:{}".format(clientAddress[0], clientAddress[1]), "0-{:.1f}".format(int(total_duration_client)), "{:.1f} MB".format(total_size), rate_client))

        except Exception as e:
            print("Can't connect! An error occurred while connecting: {}".format(e))
            return #returns error message
    # When parallel connections are requested on the client side
    threadList = []  #every thread started will be stored in this list

    if args.no_of_conn > 1:  # if the value of "-P flag" is bigger than 1
        for i in range(args.no_of_conn):  #The loop is started as many as the number of "P" values entered.
    # I get help from this page to write this section:
     # https://www.activestate.com/blog/how-to-manage-threads-in-python/ 
            thread = threading.Thread(target=handle_single_connection)#I defined the thread and targeted the handle_single_connection function
            thread.start() #Start thread 
            threadList.append(thread)#After a thread is started, it is added to the threads list
            time.sleep(1) #1 second waiting time

        successful_connections = 0 #This is a counter, it is put to keep track of the number of successful connections
        for thread in threadList:
            thread.join()# prevents another thread from running before the thread has finished.
            successful_connections += 1 #number of successfull_connections is increased by 1 when each connection is successful
    else:  # if P is 1
        handle_single_connection()

#I used those sources in order to write thread-section https://superfastpython.com/join-a-thread-in-python/ 
# and https://stackoverflow.com/questions/33470760/python-threads-object-append-to-list


if __name__ == '__main__':
    args = define_flags() #calls the define_flags function
    if args.server: #checks if the user specified the -s flag in the command
        server(args)# "if True, calls server(args)" function 

    elif args.client: #checks if the user specified the -c flag in the command
        client(args) #if True, calls "client(args)"

