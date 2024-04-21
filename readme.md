# Connecting to Gopher Server

This Python script is designed to connect to and crawl a Gopher server, downloading any text and binary files within it while navigating through directories. It ignores external servers but logs their status.

## Running the Program

1. Extract the folder to a location of your choice.
2. Open terminal/powershell with administrative privileges.
3. CD to the directory of the folder.
4. Run the script with `python connect.py`.
5. Wait for the script to run and return the results.
6. The script will automatically create a folder within its parent directory named `downloads`, with subfolders `binary` and `text` for downloaded files.

## Modifying The Server & Variables 

To modify the server the script connects to (alongside additional elements, such as the buffer size and time out) edit the variables under the `__main__` function:
- `host`: Changes the host the crawler connects to.
- `port`: Changes the port the crawler connects to.
- `buffer_size`: Changes the size of the response buffer (in bytes).
- `timeout`: Changes the duration of the program timeout (in seconds).

## Wireshark Filtering
To filter traffic via Wireshark:
- Use the IP address of the host obtained from `nslookup`.
`(ip.addr == 170.64.166.99 && tcp.port == 70) || (ip.dst == 170.64.166.99 && tcp.port == 70)`

## Crawling Directories and Counting Items

During the crawling process, the script uses counters `text_file_count`, `subdirectory_count`, and `binary_count` to keep track of the number of various items seen. These are incremented within the `directory_crawler` function as it navigates through directories and encounters files.

## Handling Errors and Invalid References

In addition to counting successful retrievals of files and directories, the script also tracks and reports any encountered errors. This includes invalid references, timeouts, and any other issues that may arise during the crawling process. 

## Returning File Sizes

Upon completion of the crawling process, the script provides information regarding the sizes of files encountered during the traversal. This includes the size of the largest and smallest text files, as well as the sizes of the largest and smallest binary files. 

## Handling Edge Cases

The script is equipped to handle various edge cases that may arise during the crawling process:
- **Handling Mazes**: To prevent the script from getting stuck in loops, it tracks visited directories and avoids revisiting them.
- **Handling Long File Names**: Files with excessively long names are shortened using a hashing mechanism to comply with system limitations.
- **Handling Large Files**: The script employs recursive retrieval mechanisms for large files.
- **Handling Infinite/Unresponsive Files**: Timeouts are enforced for unresponsive files.
- **Handling Incorrectly Constructed Directories**: The script gracefully manages directories with non-standard or incorrectly formatted structures.
- **Handling Other Gopher Types (Invalid References)**: The script intelligently processes and manages various Gopher types, including handling invalid references appropriately.

## Additional Functions

- `get_response`: Sends a request to the server and receives a response.
- `directory_crawler`: Navigates through directories and counts items.
- `downloader`: Downloads files, handles binary and text files differently.
- `packet_splitter`: Splits the packet into parts for processing.
- `construct_file_url`: Constructs the file URL from its parts.
- `generate_short_filename`: Generates a shorter filename for long filenames.
- `size_checker`: Checks the size of files in a directory.
- `check_server_status`: Checks the status of a server.
