import os
import socket

def get_gopher_response(host, port, selector):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(selector.encode('utf-8') + b"\r\n")
        return s.recv(4096).decode('utf-8')

def connect_and_return(host, port, selector):
    response = get_gopher_response(host, port, selector)
    print(response)

    # Directory is the directory of the script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    downloads_directory = os.path.join(script_directory, 'downloads')

    # Create the downloads directory if it doesn't exist
    if not os.path.exists(downloads_directory):
        os.makedirs(downloads_directory)

    # Split the response into lines
    lines = response.split('\n')


    for line in lines:
        if line.startswith('i'):
            print("Informational Line:" + line)
        elif line.startswith('0'):
            parts = [line[0]] + line[1:].split('\t')
            gopher_info = parts
            file_url = construct_file_url(gopher_info)
            output_path = os.path.join('downloads', os.path.basename(gopher_info[2]))
            download_file(file_url, output_path)
        elif line.startswith('1'):
            parts = [line[0]] + line[1:].split('\t')
            gopher_info = parts
            file_url = construct_file_url(gopher_info)
            


def construct_file_url(gopher_info):
    type = gopher_info[0]
    host = gopher_info[3]
    port = gopher_info[4].strip()
    selector = gopher_info[2]
    return f"{host}:{port}/{type}{selector}"

def download_file(file_url, output_path):
    host_port_selector = file_url.split('/')
    host_port = host_port_selector[0]
    selector = '/' + '/'.join(host_port_selector[2:])
    host, port = host_port.split(':')

    file_content = get_gopher_response(host, int(port), selector)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(file_content)


# This is the entry point of the script
if __name__ == "__main__":
    host = "comp3310.ddns.net"
    port = 70
    connect_and_return(host, port, "")
