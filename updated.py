import os
import socket
import time

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

def get_response(host, port, selector, decode_response=True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            final_url = f"{host}:{port}/{selector}"
            print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("Client-request:", final_url)
            s.settimeout(timeout)  # Set the timeout for the socket
            
            s.connect((host, port))
            s.sendall(selector.encode('utf-8') + b"\r\n")
            
            response = b""  # Initialize an empty byte string to accumulate the response
            total_received = 0  # Initialize a counter for total received bytes
            
            while True:
                chunk = s.recv(min(buffer_size, max_bytes - total_received) if max_bytes else buffer_size)  
                # Receive data in chunks, limiting the chunk size if max_bytes is specified
                
                if not chunk:  # If no more data is received, break the loop
                    break
                
                response += chunk  # Append the received chunk to the response
                total_received += len(chunk)  # Update the total received bytes
                
                if max_bytes and total_received >= max_bytes:  # If reached the maximum bytes, break the loop
                    break

            if decode_response:
                return response.decode('utf-8')
            else:
                return response
        except socket.timeout:
            print("Socket operation timed out.")
            return None
        finally:
            s.close()


def directory_crawler(host, port, selector):
    global subdirectory_count, visited_directories, text_files_list, binary_files_list, external_directories_count, external_directories, server_status_info, invalid_references  # Declare the variables as global
    response = get_response(host, port, selector, True)

    lines = response.split('\n')
    for line in lines:
        if line.startswith('i'):  # Informational Line, Ignore
            pass

        elif line.startswith('0'):  # Text File, Download
            file_name = downloader(line, False)


        elif line.startswith('1'):  # Subdirectory, Navigate to
            parts = packet_splitter(line)
            
            if len(parts) != 5:
                errored_directories[str(parts[1:])] = 'This directory item is malformed and cannot be crawled'
                continue

            if parts[3] != host or parts[4].strip() != str(port):  # Check if its on the current server
                external_url = construct_file_url(parts)
                if external_url not in external_directories:  # If not already in the list, add it
                    external_directories.append(external_url)
                    external_directories_count += 1
                    server_status_info[external_url] = check_server_status(parts[3], int(parts[4].strip()))
            else:  # If it is not on the server, check if it has already been visited (prevents getting stuck in loops)
                directory_url = construct_file_url(parts)
                if directory_url not in visited_directories:  # If a directory has not been visited, visit it
                    visited_directories.append(directory_url)  # Mark the directory as visited
                    subdirectory_count += 1
                    try:
                        directory_crawler(parts[3], int(parts[4].strip()), parts[2])
                    except Exception as e:
                        print(f"An error occurred while crawling directory {directory_url}: {e}")
        
        elif line.startswith('3'):  # Error Type
            invalid_references += 1
            pass

        elif line.startswith(('4', '5', '6', '7', '8')):  # Additional Types
            for prefix in ('4', '5', '6', '7', '8'):
                if line.startswith(prefix):
                    print("Line starts with type:", prefix)
                    break  # Stop looping once a match is found
            print("This script does not support this type and will add it to the invalid reference count.")
            invalid_references += 1
            pass


        elif line.startswith('9'): # Binary File, Download 
            file_name = downloader(line, True)


def packet_splitter(line):
    parts = [line[0]] + line[1:].split('\t')
    return parts

def downloader(line, is_binary=False):
    global errored_files, binary_count, text_file_count, invalid_references
    parts = packet_splitter(line) 
    file_url = construct_file_url(parts) 
    print(file_url + " is being downloaded")
    
    # Generate a unique, shorter file name if needed
    if len(parts[2]) > 50:
        output_filename = generate_short_filename(parts[2])
    else:
        output_filename = os.path.basename(parts[2])

    # Check if the file has the correct extension based on its type
    if is_binary:
        if '.' not in output_filename:
            output_filename += '.bin'
    else:
        if not output_filename.endswith('.txt'):
            output_filename += '.txt'

    output_directory = 'binary' if is_binary else 'text'
    output_path = os.path.join('downloads', output_directory, output_filename)

    host_port_selector = file_url.split('/')
    host_port = host_port_selector[0]
    selector = '/' + '/'.join(host_port_selector[2:])
    host, port = host_port.split(':')

    if is_binary:
        file_content = get_response(host, int(port), selector, False)
        if file_content is None:  # If response is None, it means the file timed out
            errored_files[output_filename] = 'The file timed out'
            file_content = 'This file timed out, there was an error downloading it'
            invalid_references += 1
        elif len(file_content) == max_bytes:
            errored_files[output_filename] = 'Exceeded maximum file size.'
            file_content = 'This file exceeds the maximum download size allowed. To download, increase the max_bytes variable'
            invalid_references += 1

        else:
            if len(file_content) == 0:
                errored_files[output_filename] = 'The file is empty.'
                invalid_references += 1
            else:
                binary_files_list.append(file_url)
                binary_count += 1
                with open(output_path, 'wb') as file: 
                    file.write(file_content)  
                return output_filename 

    else:
        file_content = get_response(host, int(port), selector, True)

        if file_content is None:  # If response is None, it means the file timed out
            errored_files[output_filename] = 'The file timed out.'
            file_content = 'This file timed out, there was an error downloading it'
            invalid_references += 1
        elif len(file_content) == max_bytes:
            errored_files[output_filename] = 'Exceeded maximum file size.'
            file_content = 'This file exceeds the maximum download size allowed. To download, increase the max_bytes variable'
            invalid_references += 1
        else:
            file_content = file_content[:-4]  # Remove the last two characters (period and newline)
            if len(file_content) == 0:
                errored_files[output_filename] = 'The file is empty.'
                invalid_references += 1
            else:
                text_files_list.append(file_url)
                text_file_count += 1
       
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(file_content.strip('\n'))  # Strip trailing newline characters before writing
        return output_filename  
    

def construct_file_url(parts):
    type = parts[0]
    host = parts[3]
    port = parts[4].strip()
    selector = parts[2]
    return f"{host}:{port}/{selector}"

def generate_short_filename(long_filename, counter=[0]):
    # Increment the counter for each call to ensure uniqueness
    counter[0] += 1
    
    # Extract the first 10 characters of the long filename
    short_part = long_filename[:10]
    
    # Replace slashes with underscores
    short_part = short_part.replace("/", "_").replace("\\", "_")
    
    # Append the counter value to ensure uniqueness
    short_filename = "largename_" + short_part + "_" + str(counter[0]) + ".txt"
    
    return short_filename

def size_checker(directory):
    file_sizes = {}  # Dictionary to store file sizes
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file not in errored_files:  # Exclude files listed in errored_files
                file_sizes[file_path] = os.path.getsize(file_path)  # Get file size and store it

    if file_sizes:  # If there are files in the directory after excluding errored files
        smallest_file = min(file_sizes, key=file_sizes.get)
        largest_file = max(file_sizes, key=file_sizes.get)
        smallest_size = file_sizes[smallest_file]
        largest_size = file_sizes[largest_file]
        return smallest_file, smallest_size, largest_file, largest_size
    else:
        return None, None, None, None

def check_server_status(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception as e:
        print(f"Error occurred while checking the status of {host}:{port}: {e}")
        return False

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

    host = "comp3310.ddns.net"
    port = 70
    buffer_size = 4096
    max_bytes = 100000 # Maximum bytes to download (100kB)
    timeout = 2

    directory_crawler(host, port, "")  # Start the directory crawler from the root directory
        
    # Call the size_checker function for both text and binary directories
    text_smallest_file, text_smallest_size, text_largest_file, text_largest_size = size_checker(text_directory)
    binary_smallest_file, binary_smallest_size, binary_largest_file, binary_largest_size = size_checker(binary_directory)

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
