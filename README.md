# CPSC471-group-project

## Table of Contents

1. [Team Members](#team-members)
2. [Technologies](#technologies)
3. [Instructions](#instructions)

## Team Members

- Evan Heidebrink: heidebrinkevan@csu.fullerton.edu
- Angel Armendariz: angelarmendariz@csu.fullerton.edu
- Jared Olalde: jolalde@csu.fullerton.edu
- Trung Tran: trungqt2@csu.fullerton.edu
- Brandon Struble: brandonstruble@csu.fullerton.edu

## Technologies

- Language: Python
- Version Control: Git / GitHub
- Communication: Discord

## Instructions

Dependencies:

```bash
pip install bcrypt
```

Start server:

```bash
python3 server.py <port>
```

_Example: python3 server.py 12000_

Start client:

```bash
python3 client.py <IP address> <port>
```

_Example: python3 client.py 127.0.0.1 12000_

For admin access:

- Username: `admin`
- Password: `admin`

For user access:

- Username: `user1`
- Password: `password1`

### FTP Client Commands

Download a file from the server

```bash
ftp> get <filename>
```

Upload a file to the server

```bash
ftp> put <filename>
```

List files on the server

```bash
ftp> ls
```

Disconnect from the server and exit

```bash
ftp> quit
```
