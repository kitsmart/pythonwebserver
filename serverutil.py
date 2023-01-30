'''
This is the server utlities module that handles changes to settings, flushing the database and the starting of the server
'''
from datetime import date # Allows the server to do operations based on time, thus allowing the time between requests to be saved
import socket 
import process # This is the module that I wrote that actually handles the requests
import os # This is to delete files
import sqlite3
import random

class ServerOperations:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip # This sets all of the variables to then be used as arguments for the request handling
        self.port = port
        self.whitelist_on = False
        self.blacklist_on = False
        if not os.path.isfile('Connections.db'):
            self.connections = sqlite3.connect('Connections.db')
            c = self.connections.cursor()
            c.execute('''CREATE TABLE Whitelist
            (IPaddr text)''')
            self.connections.commit()
            c.execute('''CREATE TABLE Blacklist
            (IPaddr text)''')
            self.connections.commit()
            c.execute('''CREATE TABLE Connections
            (TimeOfConnection DATETIME,
            IPAddress text,
            Data_requested text)''')
            self.connections.commit()

        self.connections = sqlite3.connect('Connections.db')

    def change_admin_file(self):
        paswd = []
        chars = []
        for i in range(26):
            chars.append(chr(i+65))
            chars.append(chr(i+97))
        for i in range(12):    
            paswd.append(random.choice(chars))
        paswd = "".join(paswd)
        paswd = paswd+'.html'
        os.rename("admin.html")

    def start_server(self):
        print("Server currently running on port:", self.port, "and ip: ", self.server_ip)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so: # This sets the addressing family. For example, AF_INET accepts either a hostname or an IPv4 address. SOCK_STREAM is the type of socket 
            so.bind((self.server_ip, self.port))  # This binds the socket to the address of the server
            so.listen(5) # This starts listening for new connections, the argument supplied is the number of backlogged connections it will accept before it starts refusing new ones
            while True: # This allows the server to take more requests than just a single one
                connection, addr = so.accept() # This accepts the connection and the next line reads in 1024 bytes from the source that is sending the request into the data variable
                data = connection.recv(1024)
                
                pro = process.ProcessRequests(addr) # Instantiate the process class
                pro.get_ipaddr(connection, data, self.whitelist_on, self.blacklist_on, self.timeout_time) # Supplies all data from request and settings into the get_ipaddr() method in the process class

    def change_settings(self):

        '''
        Allows the user to change config settings in the server
        '''

        whitelist_choice = input("Would you like to turn on the whitelist? [y]: ")
        if whitelist_choice == 'y':
            self.whitelist_on = True
        blacklist_choice = input("Would you like to turn the blacklist on? [y]: ")
        if blacklist_choice == 'y':
            self.blacklist_on = True
        while True:
            try:
                self.timeout_time = int(input("Minimum time between requests: "))
                break
            except ValueError:
                print("Please enter a number: ")
        
    def add_ip_to_db(self, table_name, ip_addr):
        c = self.connections.cursor()
        c.execute('INSERT INTO {} VALUES (?);'.format(table_name),
        (ip_addr,))
        self.connections.commit()
    
    def return_connections(self):
        arr = []
        for row in self.connections.execute('SELECT * FROM Connections'):
            arr.append(row)
        self.connections.close()
        return arr

    def count_through_ips(self):
        bl_or_wl = input("Would you like to add to the Whitelist [1] or the Blacklist [2]: ")
        start_ip = input("What IP would you like to start from?: ")
        end_ip = input("What IP would you like to end on?: ")
        if bl_or_wl == '1':
            bl_or_wl = 'Whitelist'
        elif bl_or_wl == '2':
            bl_or_wl = 'Blacklist'

        ip_start = start_ip.split(".")
        ip_end = end_ip.split(".")

        start_ip_long = (int(ip_start[0]) << 24) + (int(ip_start[1]) << 16) + (int(ip_start[2]) << 8) + int(ip_start[3])
        end_ip_long = (int(ip_end[0]) << 24) + (int(ip_end[1]) << 16) + (int(ip_end[2]) << 8) + int(ip_end[3])

        while start_ip_long <= end_ip_long:
            '.'.join([str(start_ip_long >> (i << 3) & 0xFF) for i in range(4)[::-1]])
            self.add_ip_to_db(bl_or_wl, '.'.join([str(start_ip_long >> (i << 3) & 0xFF) for i in range(4)[::-1]]))
            start_ip_long += 1

    def flush_db(self):
        self.connections.close()
        os.remove('Connections.db') # To flush the database, it just deletes the file, a new one will be created in the process class

    def manage_admin_page(self):
        files = os.listdir("admin/")
        file = [string for string in files if '.html' in string]
        fname = []
        chars = []
        for i in range(26):
            chars.append(chr(i+65))
            chars.append(chr(i+97))
        for i in range(12):    
            fname.append(random.choice(chars))
        fname = "".join(fname)
        fname = 'admin/'+fname+'.html'
        file = 'admin/'+file[0]
        os.rename(file, fname)
