# COMP3310 - A2 - Gopher Indexing Assignment
## Zac Morehouse | u7637337 

This is a python script that is designed to crawl a gopher server, listing information about it and downloading any text files or binary files it comes across. 

============================================

## Running The Program
1. Extract the folder to a location of your choice.
2. Open terminal/powershell with **administrative privileges.**
3. CD to the directory of the folder (your_path/ZM_Gopher_Program).
4. Run the script with `python connect.py`.
5. Wait for the script to run and return the results.
6. The script will automatically create a folder within its parent directory named `downloads`, with subfolders `binary` and `text` to contain the various downloaded files.

## Modifying The Server & Variables 
The program contains a handful of variables that can be changed to easily modify the scripts functionality. These are found in the ``__main__`` function.
- `host`: Changes the host the crawler connects to.
- `port`: Changes the port the crawler connects to.
- `buffer_size`: Changes the size of the response buffer (in bytes). 
- `max_bytes`: Changes the maximum bytes to download before it is refused. Files larger than this file size will be timed out. 
- `timeout`: Changes the duration of the timeout period (in seconds).

## Wireshark Filtering
To filter traffic via Wireshark:
- Use the IP address of the host obtained using `nslookup`.
- Filter using `(ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70)`
- A screenshot of the program connecting to the COMP3310 server can be found in the program folder. It is titled 'Wireshark Socket Connection'

============================================

# Program Logic and Explanation
## Creating Download Folders
When the program is initialised, the program creates a 'downloads' folder with relevant subdirectories. This is handled within the ``__main__`` function and is why the script should be run with administrative privileges.  

## Returning a Response
The ``__main__`` function then calls the ``get_response()`` function. This function uses the socket library to connect to the specified server, initialise a byte stream, and return a response. 
Here, ``buffer_size`` is used to control the size of the chunks, with ``max_bytes`` controlling the maximum size the final response is allowed to be.  

Within said function, some additional things happen. These include :
- Logging the current timestamp and path the script is connecting to. 
- Setting a ``timeout``. If the file does not download within the given time, it raises an error. This was implemented to deal with files such as **tarpit.txt** and **godot.txt**. These files are malicious, sending data that is never able to be recieved by the client. Timing the response out allows the script to prevent getting stuck on these files. 
- Keeping track of ``max_bytes``. Similarly, if a file is larger than allowed, we can return an error. This helps handle files such as **firehose.txt**, which sends information infinitely. 
- Encoding and Decoding Response. By specifying ``decode_response`` we can return the response in either UTF-8 encoding (useful for text files) or raw data (useful for binary). This was implemented to help deal with **encabulator.jpeg** as it corrupts if the data is written in UTF-8.

## The Crawler Function
Using the response specified, we can begin crawling it. Understanding the gopher rfc, we can split the response into relevant lines and apply different actions based off the first character of each line.
- If the line begins with i, it is informational. We can ignore.
- If the line begins with 0, it is a text file. We can call the ``downloader()`` function
- If the line begins with 1, it is a subdirectory. We can determine it's peices (host, port, selector, etc.) with ``packet_splitter()``, then use this information with ``construct_file_url()``. From here, we can do a number of things - outlined under the next subheading. 
- If the line begins with 3, it is an error type. We can raise an error, log it in our ``errored_directories`` and continue.
- If the line begins with 4-8, it is a valid gopher reponse however the script is not equipped to handle it. We can raise an error and continue.
- If the line begins with 9, it is a binary file. We can call the ``downloader()`` function.

## Handling Subdirectories & Recursion
In order to prevent getting stuck in loops, the script must work its way through the directories - keeping track of where it's already been. 
Every time a subdirectory is visited, it's URL is appended to ``visited_directories``. If a directory is found, it is first checked against ``visited_directories`` to ensure it hasn't already been visited in the past. From here, the program calls ``directory_crawler()`` (the current function) which in turn calls ``get_response()`` and the crawler continues. If we haven't visited it, we can also increment our ``subdirectory_count``. 

Because of this, ``visited_directories`` must include the 'homepage' before the program starts - as otherwise it is possible the script crawls the homepage twice. Similarly, we must begin by incrementing the ``subdirectory_count`` by 1 to include the home directory. 

Moreover, the script must also ensure the directory being visited is on the current server. If the host or port is different (which can be determined by checking the original ``host`` and ``port``  against the ``parts[]`` array) we do not run ``directory_crawler()``. Rather, we call ``check_server_status()`` which will connect to the server, without crawling it's contents. This will tell us if the server is up or not - which is then added to a dictionary ``server_status_info`` for reference later on. 

Finally, the script also needs to ensure the directory is correctly formed. This is how we handle **/misc/malformed1/file** which does not provide a host or port to connect to. We can see this is malformed, as ``parts[]`` does not contain the correct number of values (5). From here, an error is raised and we log its data to the ``errored_directories`` dictionary.

## Downloading files
When downloading text files we call the ``downloader()`` function. Similarly to before, this first establishes the URL of the file with ``packet_splitter()`` and  ``construct_file_url()``. By specifying  ``is_binary=False`` /  ``is_binary=True`` we can manage a few things - including whether the response should be encoded, what the extension should be and where to download the file. 

Once the file URL has been constructed we can then check if we need to generate a shorter filename. This is to handle files such as **loooooo...ng.txt** as the script will break if a file name is too long. If the filename is over 50 characters long, the ``generate_short_filename()`` function will be called. This function takes the first 10 letters of the name and renames it accordingly.

The name of the file is then checked, to see if it already contains a file extension. If it does not contain one, an extension (.bin / .txt) is assigned. Then, a download directory is specified and ``get_response()`` is called. 

## Downloading Text Files
If the file is a text file, ``get_response`` is called with ``decode_response=true``. We recieve the response in UTF-8 encoding, strip the period and newline (as per the rfc) and add it to a text file using ``file.write(w)``. We also increment our ``text_file_count`` and add the file name to our list of text files (``text_files_list``)

Depending on the response the script also performs other actions.

- If the response is "Timeout with Data", we know the file has timed out and contains data. We can assume this means the file had more data to send, but wasn't able to complete sending in the timeout period.
- If the response is "Timeout without Data", we know the file has timed out and doesn't contain data. We can assume this means the response was not able to reach the client during the timeout period. 
- If the length of the response is equal to max_bytes, we can assume the file timed out because it was too large.
- If the length of the response (minus the period and new line characters) is zero, we know the file is empty. 
- If the response does not contain a period and newline character, such as **malformed2.txt**, we know the file has been incorrectly written per the rfc standards. 

If any of these cases occur, we create the file with what data we **do** have (being liberal in what we accept), log it to the ``errored_files`` dictionary and increment our error counter (``invalid_references``).

## Downloading Binary Files 
Binary files work exactly the same, however are written to their respective files with ``file.write(wb)``. Here, ``binary_count`` and ``binary_files_list`` are used instead of the text file ones.

## Specific errored files and how they were dealt with. 
As outlined there were a number of edge cases / files that needed to be dealt with. These were :

| File Name | Error Description | How It Was Handled |
| ----------- | ----------- | ----------- |
| empty.txt | The file is empty. | Empty files are not included in the final txt file count and are considered errored files. This is handled by checking if the size of the file is = 0. |
| malformed2.txt | The file is not concluded per the rfc gopher standard. (period, newline) | The contents of the file are written, however it is considered an errored file. This is handled by checking if the end of the response contains period, newline. |
| firehose.txt | The file infinitely sends information. | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if it becomes larger than the specified maximum file size. |
| tarpit.txt | The file responds extremely slowly. | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if the full amount of information has not been recieved after a timeout period.|
| godot.txt | The file reponse is never recieved  | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if no information has been recieved during the timeout period. |

## Counting totals and what they include. 
``subdirectory_count`` - The subdirectory count **DOES NOT** include errored directories. These may be either malformed, OR have returned an error type of 3. This **DOES** include empty directories, as they are still valid. 
``text_file_count`` & ``text_files_list`` - The text file count and list **DO NOT** included errored files. While the script still attempts to download these files, they are excluded from the results.
``binary_count`` & ``binary_files_list`` - The binary count and list **DO NOT** include errored files.
``invalid_references`` - The invalid references count **DOES** include directories that returned an error type 3, files with errors AND malformed directories.
Smallest & Largest Summaries - The smallest and largest summaries **DO NOT** include any errored files. 

## Returning Results
To return the results of the script, the tracked variables (such as the list of text files, binary files, and counts) are outputted with a print statement. Errored files are also counted and listed **seperately** within their own section - with their relevant errors being displayed. We must also call ``size_checker()`` to determine the largest and smallest binary/text files. This function simply navigates and crawls the downloaded files, checking their sizing and returning the min/max. Using this information, we can also use ``file.read()`` to read the data of the smallest file to the console. Finally, we can print the ``server_status_info`` dictionary to show the various external servers and whether they were online.    

============================================

# Program Final Output Per 26/04 @ 12:52pm
```
-------------------------------------

The program has finished running on comp3310.ddns.net at port 70.
Here are it's findings.

-------------------------------------
Number of internal Gopher directories found: 39
-------------------------------------
Number of unique text files: 10
-------------------------------------
List of text files found:
comp3310.ddns.net:70/rfc1436.txt
comp3310.ddns.net:70/acme/about
comp3310.ddns.net:70/acme/products/anvils
comp3310.ddns.net:70/acme/products/pianos
comp3310.ddns.net:70/acme/products/paint
comp3310.ddns.net:70/acme/contact
comp3310.ddns.net:70/maze/statuette
comp3310.ddns.net:70/maze/floppy
comp3310.ddns.net:70/misc/nestz
comp3310.ddns.net:70/misc/loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong
-------------------------------------
Number of unique binary files: 2
-------------------------------------
List of binary files found:
comp3310.ddns.net:70/misc/binary
comp3310.ddns.net:70/misc/encabulator.jpeg
-------------------------------------
Smallest & Largest Summary
Smallest Text File: nestz.txt Size: 6 bytes
Largest Text File: rfc1436.txt Size: 38289 bytes
Smallest Binary File: binary.bin Size: 253 bytes
Largest Binary File: encabulator.jpeg Size: 45584 bytes
-------------------------------------
Contents of the smallest text file:
Hello!
-------------------------------------
Number of invalid references (including errored files and directories): 8
-------------------------------------
Errored Files:
empty.txt: The file is empty.
malformed2.txt: The response is not a correctly formatted gopher text response.
firehose.txt: The response exceeded the maximum file size and was timed out.
tarpit.txt: The contents of the file was unable to be fully downloaded within the timeout period.
godot.txt: No response was recieved from the server within the timeout period.
-------------------------------------
Errored Directories:
comp3310.ddns.net:70/acme/products/traps: Item type 3, a gopher error, was received at this address.
comp3310.ddns.net:70/misc/nonexistent: Item type 3, a gopher error, was received at this address.
['1', 'Some menu - but on what host???', '/misc/malformed1/file', '\r']: The structure of this directory item is malformed.
-------------------------------------
List of external servers and their status :
Server: gopher.floodgap.com:70 Status: Online
Server: comp3310.ddns.net:71 Status: Offline
-------------------------------------
```