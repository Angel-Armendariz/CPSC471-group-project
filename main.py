import argparse
import socket
import asyncio

arg_parser = argparse.ArgumentParser(description="FTP Client")

arg_parser.add_argument_group("Authentication")

arg_parser.add_argument("--src_addr", help="Local server IP/Address", default="127.0.0.1")
arg_parser.add_argument("--src_port", type=int, help="Local server port number", default=12000)

arg_parser.add_argument("--server", help="Enable server mode for local server to serve file", action="store_true")
arg_parser.add_argument("--daemon", help="Run the server in daemon mode", action="store_true")

arg_parser.add_argument("--dest_addr", help="Destination server IP/Address")
arg_parser.add_argument("--dest_port", type=int, help="Destination server port number")

# Username and password

arg_parser.add_argument("--user", type=str, help="Username for authentication")
arg_parser.add_argument("--pass", type=str, help="Password for authentication")

arg_parser.add_argument("--auth", help="Use with --server to add user and password from a file for authentication", type=str)

cmd_parser = arg_parser.add_subparsers(dest="command", help="Commands to execute")

{
    "cd": cmd_parser.add_parser("cd", help="Change directory")
        .add_argument("path", help="Path to change to"),

    "lcd": cmd_parser.add_parser("lcd", help="Change local directory")
        .add_argument("path", help="Path to change to"),

    "ls": cmd_parser.add_parser("ls", help="List directory contents"),
    "lls": cmd_parser.add_parser("lls", help="List local directory contents"),

    "get": cmd_parser.add_parser("get", help="Download file")
        .add_argument("file", help="File to download"),

    "put": cmd_parser.add_parser("put", help="Upload file")
        .add_argument("file", help="File to upload"),

    "delete": cmd_parser.add_parser("delete", help="Delete file")
        .add_argument("file", help="File to delete"),

    "rename": cmd_parser.add_parser("mv", help="Move/Rename file")
        .add_argument("old", help="Old path/name")
        .add_argument("new", help="New path/name"),

    "mkdir": cmd_parser.add_parser("mkdir", help="Create directory")
        .add_argument("path", help="Directory path to create"),

    "rmdir": cmd_parser.add_parser("rmdir", help="Remove directory")
        .add_argument("path", help="Directory path to remove"),
}

async def main():
    args = arg_parser.parse_args()

    # control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # control_socket.connect((args.dest_addr, args.dest_port))

    # Maybe merge client.py and server.py together

if __name__ == "__main__":
    asyncio.run(main())