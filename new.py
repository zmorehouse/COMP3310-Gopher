import os
import socket

text_file_count = 0
subdirectory_count = 0
binary_count = 0
visited_directories = []  # List to store visited directories
text_files_list = []  # List to store names of simple text files
binary_files_list = []  # List to store names of binary files

def get_response(host, port, selector, type, decode_response=True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        full_selector = type + selector
        if not selector:  
            full_selector = str(type)
        final_url = f"{host}:{port}/{full_selector}"
        print("Final URL:", final_url)
        s.connect((host, port))
        s.sendall(full_selector.encode('utf-8') + b"\r\n")
        response = s.recv(4096)
        if decode_response:
            return response.decode('utf-8')
        else:
            return response
        
def connect_and_return(host, port, selector, type):
    global text_file_count, subdirectory_count, visited_directories, text_files_list, binary_count, binary_files_list  # Declare the variables as global
    response = get_response(host, port, selector, type)
    print(response)
    # Split the response into lines
    lines = response.split('\n')

    for line in lines:
        if line.startswith('i'):
            pass
        elif line.startswith('0'):
            text_file_count += 1  # Tally a text file
            file_name = file_downloader(line)  # Download the file
            text_files_list.append(file_name)  # Add the file name to the list
            
        elif line.startswith('1'):
            subdirectory_count += 1
            parts = packet_splitter(line)
            print(parts)
            if parts[3] != 'comp3310.ddns.net' or parts[4].strip() != '70':
                print('We not going here')
            else:
                directory_url = construct_file_url(parts)
                if directory_url not in visited_directories:  # Check if the directory has been visited
                    visited_directories.append(directory_url)  # Mark the directory as visited
                    connect_and_return(parts[3], int(parts[4].strip()), parts[2], "")

        elif line.startswith('9'):
            print('BINARY FILE')
            binary_count += 1
            file_name = binary_downloader(line)
            binary_files_list.append(file_name)

    print("Number of text files: ", text_file_count)
    print("Number of subdirectories: ", subdirectory_count)
    print("Number of binary files: ", binary_count)

    print("List of simple text files:")
    for file_name in text_files_list:
        print(file_name)

    print("List of binary files:")
    for file_name in binary_files_list:
        print(file_name)

def packet_splitter(line):
    parts = [line[0]] + line[1:].split('\t')
    return parts

def binary_downloader(line):
    parts = packet_splitter(line) 
    file_url = construct_file_url(parts) 
    print("This binary file " + file_url + " is being downloaded")

    output_filename = os.path.basename(parts[2])

    # Check if the file has an extension, if not, assign a default one
    if '.' not in output_filename:
        output_filename += '.bin'

    output_path = os.path.join('downloads', output_filename)

    host_port_selector = file_url.split('/')
    host_port = host_port_selector[0]
    selector = '/' + '/'.join(host_port_selector[2:])
    host, port = host_port.split(':')

    file_content = get_response(host, int(port), selector, "", decode_response=False)

    with open(output_path, 'wb') as file:  # 'wb' mode for writing binary data
        file.write(file_content)  # Write binary data directly

    return output_filename  # Return the name of the downloaded binary file


def file_downloader(line):
    parts = packet_splitter(line) 
    file_url = construct_file_url(parts) 
    print("This file " + file_url + " is being downloaded")
    
    # Generate a unique, shorter file name
    if len(parts[2]) > 50:
        output_filename = generate_short_filename(parts[2])
    else:
        output_filename = os.path.basename(parts[2])

    # Check if the file has a .txt extension
    if not output_filename.endswith('.txt'):
        output_filename += '.txt'

    output_path = os.path.join('downloads', output_filename)

    host_port_selector = file_url.split('/')
    host_port = host_port_selector[0]
    selector = '/' + '/'.join(host_port_selector[2:])
    host, port = host_port.split(':')

    file_content = get_response(host, int(port), selector, "")

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(file_content)

    return output_filename  # Return the name of the downloaded file

def construct_file_url(parts):
    type = parts[0]
    host = parts[3]
    port = parts[4].strip()
    selector = parts[2]
    full_selector = type + selector
    if not selector:  
        full_selector = str(type)
    return f"{host}:{port}/{full_selector}"

def generate_short_filename(long_filename):
    # Generate a unique, shorter filename
    short_filename = "largename" + str(hash(long_filename)) + ".txt"
    return short_filename

if __name__ == "__main__":
    # Directory is the directory of the script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    downloads_directory = os.path.join(script_directory, 'downloads')

    # Create the downloads directory if it doesn't exist
    if not os.path.exists(downloads_directory):
        os.makedirs(downloads_directory)

    host = "comp3310.ddns.net"
    port = 70
    connect_and_return(host, port, "", "")
