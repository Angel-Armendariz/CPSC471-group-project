import socket
import os
import threading
import logging
import bcrypt

# Setting up advanced logging for the server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hardcoded users dictionary for authentication purposes
users = {"user1": b'$2b$12$YtfrR5J4rcKVIhvZQVrKhu/XaB804ntd7OQNnHCBEawH5ldWj8zPe', 
         "admin": b'$2b$12$Y6m45ZdH9pNrTk.lkQjIv.rr9d3r/oQnzaMSIZ6K3i43BlYcfZFiO'}

# Function to authenticate users based on the 'users' dictionary
def authenticate(connection):
    connection.send(b"Username: ")
    username = connection.recv(1024).decode().strip()
    connection.send(b"Password: ")
    password = connection.recv(1024).decode().strip()
    
    # Checking if the provided credentials match any in the 'users' dictionary
    if username in users and bcrypt.checkpw(password.encode(), users[username]):
        connection.send(b"Authentication successful.\n")
        return True
    else:
        connection.send(b"Authentication failed.\n")
        return False
    
# Function to send file data to the client
def send_file_data(control_conn, file_name):
    try:
        # Attempt to open and read the requested file
        with open(file_name, 'rb') as file:
            # Creating a temporary data socket for file transfer
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Binding to an ephemeral port selected by the OS
            data_socket.bind(('', 0))  
            port = data_socket.getsockname()[1]
            data_socket.listen(1)
            # Sending the ephemeral port number to the client
            control_conn.send(f"PORT {port}".encode())
            conn, _ = data_socket.accept()
            control_conn.send(b"Starting file transfer.\n")
            # Reading and sending the file content in chunks
            while chunk := file.read(1024):
                conn.send(chunk)
            control_conn.send(b"File transfer completed successfully.\n")
            conn.close()
            data_socket.close()
    except FileNotFoundError:
        control_conn.send(b"ERROR: File not found.\n")
    except PermissionError:
        control_conn.send(b"ERROR: Permission denied.\n")
    except Exception as e:
        logging.error(f"Error sending file: {e}")
        control_conn.send(f"ERROR: {str(e)}\n".encode())

# Function to receive file data from the client
def receive_file_data(control_conn, file_name):
    try:
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(('', 0))
        port = data_socket.getsockname()[1]
        data_socket.listen(1)
        control_conn.send(f"PORT {port}".encode())
        conn, _ = data_socket.accept()
        control_conn.send(b"Ready to receive file.\n")
        with open(file_name, 'wb') as file:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                file.write(data)
        control_conn.send(b"File received successfully.\n")
        conn.close()
        data_socket.close()
    except Exception as e:
        logging.error(f"Error receiving file: {e}")
        control_conn.send(f"ERROR: {str(e)}\n".encode())

# Function to list the contents of the current directory on the server
def list_directory_contents(control_conn):
    try:
        files = "\n".join(os.listdir('.'))
        control_conn.send(f"{files}\n".encode())
    except Exception as e:
        logging.error(f"Error listing directory: {e}")
        control_conn.send(f"ERROR: {str(e)}\n".encode())

# Enhanced function to change the current working directory on the server
def change_directory(control_conn, path):
    try:
        os.chdir(path)
        current_path = os.getcwd()  # Get the current directory after change
        response_message = f"Directory changed successfully. New directory: {current_path}\n"
        control_conn.send(response_message.encode())
    except FileNotFoundError:
        error_msg = "ERROR: Directory not found.\n"
        control_conn.send(error_msg.encode())
        logging.error(error_msg.strip())
    except PermissionError:
        error_msg = "ERROR: Permission denied.\n"
        control_conn.send(error_msg.encode())
        logging.error(error_msg.strip())
    except Exception as e:
        error_msg = f"ERROR: {str(e)}\n"
        control_conn.send(error_msg.encode())
        logging.error(f"Unhandled error changing directory: {e}")

# Main function to handle incoming client connections and commands
def handle_client(connection):
    if not authenticate(connection):
        connection.close()
        return

    while True:
        try:
            command = connection.recv(1024).decode()
            if not command:
                break
            logging.info(f"Received command: {command}")

            args = command.split()
            cmd = args[0].lower()
            if cmd == 'get' and len(args) == 2:
                send_file_data(connection, args[1])
            elif cmd == 'put' and len(args) == 2:
                receive_file_data(connection, args[1])
            elif cmd == 'ls':
                list_directory_contents(connection)
            elif cmd == 'cd' and len(args) == 2:
                change_directory(connection, args[1])
            elif cmd == 'quit':
                break
            else:
                connection.send(b"ERROR: Unknown command.\n")
        except Exception as e:
            logging.error(f"Unhandled error: {e}")
            connection.send(f"ERROR: {str(e)}\n".encode())
    
    connection.close()

# Function to start the FTP server and listen for incoming connections
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)
    logging.info(f"FTP Server started on port {port}. Waiting for connections...")

    try:
        while True:
            connection, addr = server_socket.accept()
            logging.info(f"Connected by {addr}")
            thread = threading.Thread(target=handle_client, args=(connection,))
            thread.start()
    except KeyboardInterrupt:
        logging.info("Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    PORT = 12000
    start_server(PORT)
