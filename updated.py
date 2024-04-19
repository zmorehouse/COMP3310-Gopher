import os
import socket
import time

text_file_count = 0
subdirectory_count = 0
binary_count = 0
visited_directories = []  
text_files_list = []  
binary_files_list = []  

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
    global text_file_count, subdirectory_count, visited_directories, text_files_list, binary_count, binary_files_list  # Declare the variables as global
    response = get_response(host, port, selector, True)

    lines = response.split('\n')

    for line in lines:
        if line.startswith('i'): # Informational Line, Ignore
            pass

        elif line.startswith('0'): # Text File, Download
            text_file_count += 1
            file_name = downloader(line, False)
            if file_name:
                text_files_list.append(file_name)

        elif line.startswith('1'): # Subdirectory
            parts = packet_splitter(line)
            if parts[3] != 'comp3310.ddns.net' or parts[4].strip() != '70': # Check if its on the server
                print('This is an external link, we will not visit it')
            else: # If it is not on the server, check if it has already been visited (prevents getting stuck in loops)
                directory_url = construct_file_url(parts)
                if directory_url not in visited_directories:  # If a directory has not been visited, visit it
                    visited_directories.append(directory_url)  # Mark the directory as visited
                    subdirectory_count += 1
                    try:
                        directory_crawler(parts[3], int(parts[4].strip()), parts[2])
                    except Exception as e:
                        print(f"An error occurred while crawling directory {directory_url}: {e}")

        elif line.startswith('9'):
            print('This is a binary file, downloading...')
            binary_count += 1
            file_name = downloader(line, True)
            if file_name:
                binary_files_list.append(file_name)
def packet_splitter(line):
    parts = [line[0]] + line[1:].split('\t')
    return parts

def downloader(line, is_binary=False):
    parts = packet_splitter(line) 
    file_url = construct_file_url(parts) 
    print("This file " + file_url + " is being downloaded")
    
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
        with open(output_path, 'wb') as file: 
            file.write(file_content)  
        return output_filename 

    else:
        file_content = get_response(host, int(port), selector, True)
        
        if file_content is None:  # If response is None, it means the file timed out
            print('This file timed out, there was an error downloading it')
            file_content = 'This file timed out, there was an error downloading it' 
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(file_content)
        return output_filename  


def construct_file_url(parts):
    type = parts[0]
    host = parts[3]
    port = parts[4].strip()
    selector = parts[2]
    return f"{host}:{port}/{selector}"

def generate_short_filename(long_filename):
    # Generate a unique, shorter filename
    short_filename = "largename" + str(hash(long_filename)) + ".txt"
    return short_filename


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
    max_bytes = 150000
    timeout = 5

    directory_crawler(host, port, "")  # Start the directory crawler from the root directory

    print("=====================================")
    print("Numerical Summary")
    print("Number of text files: ", text_file_count)
    print("Number of subdirectories: ", subdirectory_count)
    print("Number of binary files: ", binary_count)
    print("=====================================")
    print("List of text files found:")
    for file_name in text_files_list:
        print(file_name)
    print("=====================================")
    print("List of binary files found:")
    for file_name in binary_files_list:
        print(file_name)
    print("=====================================")
 