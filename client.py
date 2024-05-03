import socket
import select

# Server IP and port for the control connection
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12000

# Function to authenticate the user with the server
def authenticate(control_socket):
    # Receive and print the prompt for the username, then send the input username
    print(control_socket.recv(1024).decode(), end="")
    username = input()
    control_socket.send(username.encode())
    
    # Receive and print the prompt for the password, then send the input password
    print(control_socket.recv(1024).decode(), end="")
    password = input()
    control_socket.send(password.encode())
    
    # Receive and print the server's authentication response
    response = control_socket.recv(1024).decode()
    print(response, end="")
    
    # Return True if authentication was successful, False otherwise
    return "successful" in response

# Function to send a file to the server
def send_file(control_socket, file_name, server_ip, port):
    try:
        # Open the file to be sent and create a new socket for the data connection
        with open(file_name, 'rb') as file:
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((server_ip, int(port)))  # Connect to the server using the provided port
            while chunk := file.read(1024):
                data_socket.send(chunk)  # Send file content in chunks
            print("File has been sent successfully.")
    except FileNotFoundError:
        print("File not found.")  # File not found in the client's directory
    finally:
        data_socket.close()  # Ensure the data socket is closed after the operation

# Function to receive a file from the server
def receive_file(control_socket, file_name, server_ip, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((server_ip, int(port)))  # Connect to the server using the provided port
    with open(file_name, 'wb') as file:
        while True:
            data = data_socket.recv(1024)
            if not data:
                break  # End of file transfer
            file.write(data)  # Write received content to file
    print("File has been received successfully.")
    data_socket.close()  # Ensure the data socket is closed after the operation

def handle_commands(control_socket):
    while True:
        command = input("ftp> ").strip()  # Prompt for input
        if not command:
            continue  # Skip empty commands

        if command.lower() == "quit":  # Handle quit command to close the connection
            print("Disconnecting...")
            control_socket.close()
            break

        control_socket.send(command.encode())  # Send command to the server
        
        # Read and process the full response for the current command
        full_response = ""
        while True:
            ready = select.select([control_socket], [], [], 0.5)  # Check if data is ready to be read
            if ready[0]:
                part = control_socket.recv(4096).decode()
                full_response += part
                if len(part) < 4096:  # Less data might indicate end of message
                    break
            else:
                # No more data to read for this command
                break

        # Handle the response based on its type or content
        if "PORT" in full_response:  # Server response contains the port for the data connection
            _, port = full_response.split()
            if command.startswith("get "):
                file_name = command.split(" ", 1)[1]
                receive_file(control_socket, file_name, SERVER_IP, int(port))
            elif command.startswith("put "):
                file_name = command.split(" ", 1)[1]
                send_file(control_socket, file_name, SERVER_IP, int(port))
        else:
            print(full_response, end="")  # Print response for non-file transfer commands

        # Clear any residual data in the buffer after processing the response
        clear_residual_data(control_socket)

def clear_residual_data(control_socket):
    """Function to clear any residual data from socket buffer."""
    control_socket.setblocking(0)  # Set non-blocking mode
    try:
        while True:
            if control_socket.recv(4096):
                continue  # Keep reading if data is present
            break  # Exit if no data is present
    except BlockingIOError:
        # No more data to read
        pass
    finally:
        control_socket.setblocking(1)  # Reset to blocking mode

# Main function to start the client and handle authentication and command processing
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as control_socket:
        control_socket.connect((SERVER_IP, SERVER_PORT))  # Connect to the server control port
        if authenticate(control_socket):  # Proceed if authentication is successful
            handle_commands(control_socket)  # Enter the command handling loop
        else:
            print("Authentication failed. Exiting...")  # Exit if authentication fails

if __name__ == "__main__":
    main()
