
# Import Necessary Libraries
import os
import socket
import time

# Sends a request to a specified gopher server and return a response.
def get_response(host, port, selector):

    # Establish a socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 

            final_url = f"{host}:{port}/{selector}" 

            # Print the current time and file being requested to STDOUT
            print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) #
            print("Client-request:", final_url)


            
            s.connect((host, port))
            s.sendall(selector.encode('utf-8') + b"\r\n")
            response = s.recv(5000)
        
            return response
            s.close()

if __name__ == "__main__": # This function runs when the script is run within the terminal. 



    # Set the initial variables for the script
    host = "comp3310.ddns.net"
    port = 70
    buffer_size = 4096
    max_bytes = 100000 # Maximum bytes to download (100kB)
    timeout = 2

    get_response(host, port, "")  # Start the directory crawler from the root directory
        