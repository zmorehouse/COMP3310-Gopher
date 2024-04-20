u7637337 - Zac Morehouse   

Running the program
The program is a simple script that only requires python to run. To run, please follow these steps :
1) Extract the folder to a location of your choice. (Which, if you're reading this, has already been done!)
2) Open terminal/powershell with administrative priviledges 
3) CD to the directory of the folder
4) Run the script with python connect.py 
5) Wait for the script to run and return the results
6) The script will automatically create a folder within it's parent directory named downloads, and two subfolders titled binary and text. These two folders will host any downloaded files. 

To modify the server the script connects to, you simply need to edit the script and change the variables under the __main__ function. 
Host - Changes the host the crawler connects to
Port - Changes the port the crawler connects to
Buffer Size - Changes the size of the response buffer (in bytes)
Timeout - Changes the duration of the program timeout (In seconds)

Wireshark Filtering
To initially recieve and filter traffic via Wireshark, I have done the following :
First, I located the IP address of the host using the nslookup command. This returned the following address : 170.64.166.99 
From here, we can simply filter both inbound/outbound wireshark traffic to this host using the following command : (ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70)
A screenshot of the programs initial response (before any logic has been applied) has been included in this folder. It is named  'Initial Response.png' 

Project Overview
The program is a script that connects to and crawls a gopher server. It will download any txt and binary files within the server, and crawl through any directories. It will ignore external servers however will log whether they are up and down. At the end, it will return  :

Edge Cases

Handling Mazes
As to not get stuck in a loop, my script will monitor 'visited directories'. By keeping track of these in a list, we can check if a directory has already been visited. If it has, we can ignore its.

Handling Long File Names
If a file name is too long (above 256 bytes) the programw ill shorten it with a hash.

Handling Large Files
If a file is too large, it will recursively request content from the file until it recieves all the content. 

Handling infinite files / unresponsive files.
If a file infinitely sends messages, or is unresponsive in it's sending, my program will timeout and throw an error message after the specified duration - moving onto the next file.



Todo :
Add scanning files size
    The contents of the smallest text file.
    The size of the largest text file.
    The size of the smallest and the largest binary files.
Add checking server uptime
Fix long names so that they are in the same file
Asdd number of unique invalid references

Identify any such situations you find on the gopher server in your
README or code comments, and how you dealt with each of them – being reasonably liberal in what you
accept and can interpret, or flagging what you cannot accept.
