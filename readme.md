# COMP3310 - A2 - Gopher Indexing Assignment
## Zac Morehouse | u7637337 

This is a small python script that is designed to crawl a gopher server, listing information about it and downloading any text files or binary files it comes across. 

============================================

## Running The Program
1. Extract the submitted folder to a location of your choice.
2. Open terminal/powershell with **administrative privileges.**
3. CD to the directory of the folder.
4. Run the script with `python connect.py`.
5. Wait for the script to run and return the results.
6. The script will automatically create a folder within its parent directory named `downloads`, with subfolders `binary` and `text` for the various downloaded files.

## Modifying The Server & Variables 
The program contains a handful of variables that can be changed to easily modify the scripts functionality. These are found in the ``__main__`` function.
- `host`: Changes the host the crawler connects to.
- `port`: Changes the port the crawler connects to.
- `buffer_size`: Changes the size of the response buffer (in bytes).
- `max_bytes`: Changes the maximum bytes to download before a file times out.
- `timeout`: Changes the duration of the program timeout (in seconds).

## Wireshark Filtering
To filter traffic via Wireshark:
- Use the IP address of the host obtained from `nslookup`.
`(ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70)`

============================================

# Program Logic and Explanation

## Creating Download Folders
When the program is initialised, the program creates a 'downloads' folder with relevant subdirectories. This is handled within the ``__main__`` function and is why the script should be run with administrative privileges.

## Returning a Response
The ``__main__`` function then calls the ``get_response()`` function. This function uses the socket library to connect to the specified server, and return a response. 
Within said function, some additional things happen. These include :
- Logging the timestamp and URL the script is connecting too. 
- Setting a ``timeout``. If the file does not download within the given time, it raises an error. This was implemented later on, as it allows the script to deal with files such as **tarpit.txt** and **godot.txt**. These files are malicious, sending data that is never able to be recieved by the client. Timing the response out allows the script to prevent getting stuck on these files.
- Keeping track of ``max_bytes``. Similarly, if a file is larger than allowed, we can return an error. This helps handle files such as **firehose.txt**, which sends information infinitely. 
- Encoding and Decoding Response. By specifying ``decode_response`` we can return the response in either UTF-8 encoding (useful for text files) or raw data (useful for binary). This was implemented to help deal with **encabulator.jpeg** as it corrupts if the data is written in UTF-8.

## The Crawler Function
Using the response specified, we can begin crawling it. Understanding the gopher rfc, we can split the response into relevant lines and apply different actions based off the first character of each line.
- If the line begins with i, it is informational. We can ignore.
- If the line begins with 0, it is a text file. We can run the ``downloader()`` function
- If the line begins with 1, it is a subdirectory. We can determine it's peices (host, port, selector, etc.) with ``packet_splitter()``, then use this information with ``construct_file_url()``. From here, we can do a number of things - outlined under the next subheading. 
- If the line begins with 3, it is an error type. We can raise an error and continue.
- If the line begins with 4-8, it is a valid gopher reponse however the script is not equipped to handle it. We can raise an error and continue.
- If the line begins with 9, it is a binary file. We can run the ``downloader()`` function.

## Handling Subdirectories & Recursion
In order to prevent getting stuck in loops, the script must work its way through the directories - keeping track of where it's already been. 
Every time a subdirectory is visited, it's URL is appended to ``visited_directories``. If a directory is found, it is first checked against ``visited_directories`` to ensure it hasn't already been visited in the past. From here, the program calls ``directory_crawler()`` (the current function) which in turn calls ``get_response()`` and the crawler continues. If we haven't visited it, we can also iterate our ``subdirectory_count``. 

Because of this, ``visited_directories`` must include the 'homepage' before the program starts - as otherwise it is possible the script crawls the homepage twice. 

Moreover, the script must also ensure the directory being visited is on the current server. If the host or port is different (which can be determined by checking the original ``host`` and ``port``  against the ``parts[]`` array) we do not run ``directory_crawler()``. Rather, we call ``check_server_status()`` which will connect to the server, without crawling it's contents. This will tell us if the server is up or not - which is then added to a dictionary ``server_status_info`` for reference later on. 

Finally, the script also needs to ensure the directory is correctly formed. This is how we handle **/misc/malformed1/file** which does not provide a host or port to connect to. We can see this is malformed, as ``parts[]`` does not contain the correct number of values (5). From here, an error is raised and we log its data to the ``errored_directories`` dictionary.

## Downloading files
When downloading text files we call the ``downloader()`` function. Similarly to before, this first establishes the URL of the file with ``packet_splitter()`` and  ``construct_file_url()``. By specifying  ``is_binary=False`` /  ``is_binary=True`` we can manage a few things - including whether the response should be encoded, what the extension should be and where to donwload the file. 

Once the file URL has been constructed we can then check if we need to generate a shorter filename. This is to handle files such as **loooooo...ng.txt** as the script will break if the name is too long. If the filename is over 50 characters long, the ``generate_short_filename()`` function will be called. This function takes the first 10 letters of the name and renames it accordingly.

The name of the file is then checked, to see if it already contains a file extension. If it does not contain one, an extension (.bin / .txt) is assigned. Then, a download directory is specified and ``get_response()`` is called. 

## Downloading Text Files

If the file is a text file, ``get_response`` is called with ``decode_response=true``. We recieve the response in UTF-8 encoding, strip the period and newline (as per the rfc) and add it to a text file using ``file.write(w)``. We also increment our ``text_file_count`` and add the file name to our list of text files (``text_files_list``)

Depending on the response the script also performs other actions.

- If the response is None, we can assume the file timed out. 
- If the length of the response is equal to max_bytes, we can assume the file timed out because it was too large.
- If the length of the response (minus the period and new line characters) is zero, we know the file is empty. This is to handle **empty.txt**

If any of these cases occur, we create the file with the relevant error message, log it to the ``errored_files`` dictionary and increment our error counter (``invalid_references``).

## Downloading Binary Files 
Binary files work exactly the same, however are written to their respective files with ``file.write(wb)``. Here, ``binary_count`` and ``binary_files_list`` are used instead of the text file ones.

## Specific errored files and how they were dealt with. 
As outlined there were a number of edge cases / files that needed to be dealt with. These were :

| File Name | Error Description | How It Was Handled |
| ----------- | ----------- | ----------- |
| empty.txt | The file is empty. | Empty files are not included in the final txt file count and are considered errored files. This is handled by checking if the size of the file is = 0. |
| malformed2.txt | The file is not concluded per the rfc gopher standard. (period, newline) | The contents of the file are written, however it is considered an errored file. This is handled by checking if the end of the response contains period, newline. |
| firehose.txt | The file infinitely sends information. | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if it becomes larger than the specified maximum file size. |
| tarpit.txt | The file responds extremely slowly. | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if the information has still not been recieved after a specified  duration.  |
| godot.txt | The file reponse is never recieved  | This is an issue as the program will get stuck and never finish. The script considers this an errored file and is handled by timing out the file if the information has still not been recieved after a specified  duration. |

## Returning Results
To return the results of the script, the tracked variables (such as the list of text files, binary files, and counts) are outputted with a print statement. Errored files are also counted and listed **seperately** within their own section - with their relevant errors being displayed. We must also call ``size_checker()`` to determine the largest and smallest binary/text files. This function simply navigates and crawls the downloaded files, checking their sizing and returning the min/max. Using this information, we can also use ``file.read()`` to read the data of the smallest file to the console. Finally, we can print the ``server_status_info`` dictionary to show the various external servers and whether they were online.    

============================================

# Program Final Output

TODO 
Fix malformed file and error it 
Check logic for buffer size
Redo wireshark screenshot
More detail in error messages
Paste in program final output