# portfo1
I implemented a simple network throughput measurement tool called simpleperf. This tool sends and receives packets between a client and a server using sockets.
When run in server mode, simpleperf receives TCP packets and tracks how much data was received from the connected clients; it calculates and displays the bandwidth based on how much data was received and how much time passed during the connection.
When simpleperf is invoked in a client mode, it establishs a TCP connection with the simpleperf server and send data in chunks of 1000 bytes for t seconds specified with -t or –time flag. Calculate the total
of the number of bytes sent. After the client finishes sending its data, it sends a finish/bye message and wait for an acknowledgement before exiting the program. Simpleperf calculates and display the bandwidth based on how much data was sent in the elapsed time

To run simpleperf in server mode with the default options, you should invoke with "python3 simpleperf.py -s".
To invoke the client, you can enter the command "python3 simpleperf -c -I <server_ip> -p <server_port> -t <time>".
If you try to run simpleperf without using the c and s flags, you will get an error message.
So make sure to use the s and c flags, but not on the same command line
You will also get an error message if you enter the c and s flags on the same command line 


 If the measurements are to be taken in a certain unit type, the "-f" flag should be used and the unit type should be entered next to it. 
 The -f flag can be used both when invoking the server and invoking the client. 
 For example, if you want to get the output in KB, a command like "python3 simpleperf.py -c -I '127.0.0.1' -p 8088 -t 25 -f KB" should be written. 
 Thus, the measurements to be printed on the client page are printed in KB format. 
 If the f flag is not specified on the command line, the measurements are printed in MB format. 
 Accepted format types are KB,B,MB,M. If any other format is specified, an error message will be printed.
  
If you want to run the tests, you should first open virtualbox. You must have downloaded mininet in order to run the tests. 
After downloading Mininet, clone this code file containing simpleperf and portfolio-topology to virtualbox. 
When this is done, open terminal in Virtualbox and open the file containing simpleperf and portfolio-topology with the command "cd" and enter the command "sudo python3 portfolio-topology.py". 
If you get an error message, enter the command " sudo fuser -k 6653/tcp". 
And run "sudo python3 portfolio-topology.py" again. 
After the process is complete, there should be a line that says "mininet>" where you can enter input. 
Enter the hosts you will test here with the "xterm" command. For example "xterm h1 h4". 
When you enter this command, 2 more terminal windows named Node: h1 and Node: h4 will open. 
Now you can run your tests!
