''' COMP3310 - A2 - Gopher Indexing Assignment
 Zac Morehouse | u7637337 
 This script is a Gopher client that connects to a Gopher server and downloads text and binary files. For more information, please see the readme.md file included in this folder. '''

# Import Necessary Libraries
import os
import socket
import time

# Establish Initial Variables
text_file_count = 0
subdirectory_count = 0
binary_count = 0
invalid_references = 0
visited_directories = []  
text_files_list = []  
binary_files_list = [] 
external_directories = []  
external_directories_count = 0  
server_status_info = {}  
errored_files = {}
errored_directories = {}


# Sends a request to a specified gopher server and return a response.
def get_response(host, port, selector, decode_response=True):

    # Establish a socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
        try:
            final_url = f"{host}:{port}/{selector}" 

            # Print the current time and file being requested to STDOUT
            print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) #
            print("Client-request:", final_url)

            # Set a specified timeout amount
            s.settimeout(timeout)  
            
            s.connect((host, port))
            s.sendall(selector.encode('utf-8') + b"\r\n")


            response = b""  
            total_received = 0  
            
            while True:
                chunk = s.recv(min(buffer_size, max_bytes - total_received) if max_bytes else buffer_size)  
                # Receive data in chunks, limiting the chunk size if max_bytes is specified
                
                if not chunk:  # If no more data is received, break the loop
                    break
                
                response += chunk  # Append the received chunk to the response
                total_received += len(chunk)  # Update the total received bytes
                
                if max_bytes and total_received >= max_bytes:  # If reached the maximum bytes, break the loop
                    break
            
            # If the response is to be decoded, decode it as utf-8 before returning. Otherwise, return the raw response.
            if decode_response:

                return response.decode('utf-8')
            else:

                return response

            # If the socket operation times out, print a message and return None.
        except socket.timeout:
            return None
        finally:
            s.close()




# Our primary crawler function. This crawls through a gopher server's directories and downloads text and binary files.
def directory_crawler(host, port, selector):
    global subdirectory_count, visited_directories, text_files_list, binary_files_list, external_directories_count, external_directories, server_status_info, invalid_references  # Declare the variables as global
    
    # Get a response from the server
    response = get_response(host, port, selector, True)

    # Split the response into lines and iterate through them
    lines = response.split('\n')

    for line in lines:
        if line.startswith('i'):  # Informational Line - We can ignore it.
            pass

        elif line.startswith('0'):  # Text File - We should download it. 
            downloader(line, False)

        elif line.startswith('1'):  # Subdirectory - We should do something with it. 
            parts = packet_splitter(line) # Split the response to discover the parts of the packet (Host, Port, etc.)
            
            if len(parts) != 5: # If the packet is malformed, add it to the errored directories list and continue to the next line. 
                errored_directories[str(parts[1:])] = 'This directory item is malformed and cannot be crawled'
                invalid_references += 1
                continue

            if parts[3] != host or parts[4].strip() != str(port):  # If the host or port are not the same as the server, add it to the external directories list.
                external_url = construct_file_url(parts) # Construct the URL of the external server, and check if it has already been visited.
                if external_url not in external_directories:  
                    external_directories.append(external_url) # Mark the directory as visited.
                    external_directories_count += 1
                    server_status_info[external_url] = check_server_status(parts[3], int(parts[4].strip())) # If it has not already been visited. Check the server status and add it to the server status info list.
            else:  # If the directory is internal, check if it has already been visited. If not, visit it.
                directory_url = construct_file_url(parts)
                if directory_url not in visited_directories: 
                    visited_directories.append(directory_url)  # Mark the directory as visited.
                    subdirectory_count += 1
                    try: # Recursively call the directory crawler function to crawl the directory.
                        directory_crawler(parts[3], int(parts[4].strip()), parts[2])
                    except Exception as e: 
                        print(f"An error occurred while crawling directory {directory_url}: {e}")
        
        elif line.startswith('3'):  # Error Type - We should add it to the invalid reference count.
            errored_directories[f"{host}:{port}/{selector}"] = 'An error type 3 was raised here'
            invalid_references += 1
            pass

        elif line.startswith(('4', '5', '6', '7', '8')):  # Additional Types - While these aren't invalid, our script cannot do anything with them. Hence, raise an error and increment the invalid reference count. 
            for prefix in ('4', '5', '6', '7', '8'): 
                if line.startswith(prefix):
                    print("Line starts with type:", prefix)
                    break  
            print("This script does not support this type and will add it to the invalid reference count.")
            invalid_references += 1
            pass


        elif line.startswith('9'): # Binary File - We should download it.
            downloader(line, True)

# Basic function to split a line into it's parts. 
def packet_splitter(line):
    parts = [line[0]] + line[1:].split('\t')
    return parts

# A function to download our text and binary files. 
def downloader(line, is_binary=False):
    global errored_files, binary_count, text_file_count, invalid_references

    # Construct the file URL and its individual parts
    parts = packet_splitter(line) 
    host = parts[3]
    port = parts[4].strip()
    selector = parts[2]
    file_url = construct_file_url(parts) 
    print(file_url + " is being downloaded")
    
    # Generate a unique, shorter file name if needed
    if len(parts[2]) > 50:
        output_filename = generate_short_filename(parts[2])
    else:
        output_filename = os.path.basename(parts[2])

    # Check if the file has an extension. If not, assign one. 
    if is_binary:
        if '.' not in output_filename:
            output_filename += '.bin'
    else:
        if not output_filename.endswith('.txt'):
            output_filename += '.txt'

    # Construct the output path to download them to
    output_directory = 'binary' if is_binary else 'text'
    output_path = os.path.join('downloads', output_directory, output_filename)

    if is_binary: # If the file is binary, get the response and download it as a binary file.
        file_content = get_response(host, int(port), selector, False)

        # Error handling for binary files. 
        if file_content is None: # If response is None, it means the file timed out
            errored_files[output_filename] = 'The file timed out'
            file_content = 'This file timed out, there was an error downloading it'
            invalid_references += 1
        elif len(file_content) == max_bytes: # If the response equals the maximum download size, we know it must be too big.
            errored_files[output_filename] = 'Exceeded maximum file size.'
            file_content = 'This file exceeds the maximum download size allowed. To download, increase the max_bytes variable'
            invalid_references += 1
        else:
            if len(file_content) == 0: # If the length of the response is 0, it must be empty
                errored_files[output_filename] = 'The file is empty.'
                invalid_references += 1
            
            else: # If the response is valid, write it to a file and increment the binary count.
                binary_files_list.append(file_url)
                binary_count += 1
                with open(output_path, 'wb') as file: 
                    file.write(file_content)  
                return output_filename 

    else: # If the file is text, get the response and download it as a text file.
        file_content = get_response(host, int(port), selector, True)

        # Error handling for text files.
        if file_content is None:  # If response is None, it means the file timed out
            errored_files[output_filename] = 'The file timed out.'
            file_content = 'This file timed out, there was an error downloading it'
            invalid_references += 1
        elif len(file_content) == max_bytes: # If the response equals the maximum download size, we know it must be too big.
            errored_files[output_filename] = 'Exceeded maximum file size.'
            invalid_references += 1
        elif not file_content.endswith('.\r\n'):  # Check if the file content doesn't end with ".\n"
            errored_files[output_filename] = 'Is not a correctly formatted Gopher text response (Doesnt end in a period on a new line)'
            invalid_references += 1
        else:
            file_content = file_content[:-5]  # Remove the last two characters (period and newline)
            if len(file_content) == 0:        # If the length of the response is 0, it must be empty
                errored_files[output_filename] = 'The file is empty.'
                invalid_references += 1

            else: # If the response is valid, write it to a file and increment the binary count.
                text_files_list.append(file_url)
                text_file_count += 1
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(file_content.strip('\n'))  # Strip trailing newline characters before writing
            return output_filename  
    
# Function to construct a file URL from its parts
def construct_file_url(parts):
    type = parts[0]
    host = parts[3]
    port = parts[4].strip()
    selector = parts[2]
    return f"{host}:{port}/{selector}"

# Function to generate a short filename for long filenames
def generate_short_filename(long_filename, counter=[0]):
    counter[0] += 1 # Increment a counter for each call to ensure uniqueness
    short_part = long_filename[:10] # Extract the first 10 characters of the long filename
    short_part = short_part.replace("/", "_").replace("\\", "_")
    short_filename = "largename_" + short_part + "_" + str(counter[0]) + ".txt" # Append the counter value to ensure uniqueness
    return short_filename

# Function to check the status of a server
def check_server_status(host, port):
    try: # Attempt to connect to the server and check if the connection was successful
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            return result == 0 # Return True if the connection was successful, False otherwise.
    except Exception as e:
        print(f"Error occurred while checking the status of {host}:{port}: {e}")
        return False

# Function to check the size of files in a directory. This runs after the script has finished crawling
def size_checker(directory):
    file_sizes = {}  # Dictionary to store file sizes
    for root, _, files in os.walk(directory): # Walk through the directory and get the size of each file
        for file in files:
            file_path = os.path.join(root, file)
            if file not in errored_files:  # Exclude files listed in errored_files
                file_sizes[file_path] = os.path.getsize(file_path)  # Get file size and store it

    if file_sizes:  # If there are files in the directory, get the smallest and largest files
        smallest_file = min(file_sizes, key=file_sizes.get)
        largest_file = max(file_sizes, key=file_sizes.get)
        smallest_size = file_sizes[smallest_file]
        largest_size = file_sizes[largest_file]
        return smallest_file, smallest_size, largest_file, largest_size # Return the smallest and largest files and their sizes
    else:
        return None, None, None, None # If there are no files, return None

if __name__ == "__main__": # This function runs when the script is run within the terminal. 

    # Create a downloads directory within the programs folder 
    script_directory = os.path.dirname(os.path.realpath(__file__))
    downloads_directory = os.path.join(script_directory, 'downloads')
    if not os.path.exists(downloads_directory):
        os.makedirs(downloads_directory)

    # Within this downloads folder, create text and binary directories to sort files.
    text_directory = os.path.join(downloads_directory, 'text')
    binary_directory = os.path.join(downloads_directory, 'binary')

    for directory in [text_directory, binary_directory]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Set the initial variables for the script
    host = "comp3310.ddns.net"
    port = 70
    buffer_size = 4096
    max_bytes = 100000 # Maximum bytes to download (100kB)
    timeout = 2

    visited_directories.append(f"{host}:{port}/") # Add the root directory to the visited directories list
    directory_crawler(host, port, "")  # Start the directory crawler from the root directory
        
    # Call the size_checker function for both text and binary directories
    text_smallest_file, text_smallest_size, text_largest_file, text_largest_size = size_checker(text_directory)
    binary_smallest_file, binary_smallest_size, binary_largest_file, binary_largest_size = size_checker(binary_directory)

    # Print the results of the script
    print("")
    print("-------------------------------------")
    print("")
    print("The program has finished running on " + host + " at port " + str(port) + ".")
    print("Here are it's findings.")
    print("")
    print("-------------------------------------")
    print("Number of internal Gopher directories found:", subdirectory_count)
    print("-------------------------------------")
    print("Number of unique text files:", text_file_count)
    print("-------------------------------------")
    print("List of text files found:")
    for file_name in text_files_list:
        if file_name not in errored_files:
            print(file_name)
    print("-------------------------------------")
    print("Number of unique binary files:", binary_count)
    print("-------------------------------------")
    print("List of binary files found:")
    for file_name in binary_files_list:
            if file_name not in errored_files:
                print(file_name)
    print("-------------------------------------")
    print("Smallest & Largest Summary")
    print("Smallest Text File:", os.path.basename(text_smallest_file), "Size:", text_smallest_size, "bytes")
    print("Largest Text File:", os.path.basename(text_largest_file), "Size:", text_largest_size, "bytes")
    print("Smallest Binary File:", os.path.basename(binary_smallest_file), "Size:", binary_smallest_size, "bytes")
    print("Largest Binary File:", os.path.basename(binary_largest_file), "Size:", binary_largest_size, "bytes")
    print("-------------------------------------")
    print("Contents of the smallest text file:")
    with open(text_smallest_file, 'r') as file:
        print(file.read())
    print("-------------------------------------")
    print("Number of invalid references: " + str(invalid_references))
    print("-------------------------------------")
    print("Errored Files:")
    for file_name, error_msg in errored_files.items():
        print(f"{file_name}: {error_msg}")
    print("-------------------------------------")
    print("Errored Directories:")
    for directory_name, error_msg in errored_directories.items():
        print(f"{directory_name}: {error_msg}")
    print("-------------------------------------")
    print("List of external servers and their status :")
    for url, status in server_status_info.items():
        print(f"Server: {url} Status: {'Online' if status else 'Offline'}")
    print("-------------------------------------")
