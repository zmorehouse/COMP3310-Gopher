u7637337 - Zac Morehouse   

Running the program
The program is a simple script that only requires python to run. To run, please follow these steps :
- Extract the folder to a location of your choice. (Which, if you're reading this, has already been done!)
- Open terminal/powershell with administrative priviledges 
- CD to the directory of the folder
- Run the script with python connect.py 
- Wait for the script to run and return the results
- The script will automatically create a folder within it's parent directory named downloads, and two subfolders titled binary and text. These two folders will host any downloaded files. 
- To modify the server the script connects to, you simply need to edit the script and change the variables under the __main__ function. This can take up to four variables - Host, Port, Selector and Type and will automatically construct the respective URL based on these values. 

Wireshark Filtering
To initially recieve and filter traffic via Wireshark, I have done the following :
First, I located the IP address of the host using the nslookup command. This returned the following address : 170.64.166.99 
From here, we can simply filter both inbound/outbound wireshark traffic to this host using the following command : (ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70)
A screenshot of the programs initial response (before any logic has been applied) has been included in this folder. It is named  'Initial Response.png' 

Project Overview

Tracking Amounts and Totals

Downloading Files (Text)

Downloading Files (Binary)

Handling Mazes

Handling Long File Names

Handling Deeply Nested Directories

Handling Empty Files

Handling Empty Folders

Handling Other Ports

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
