'''
Welcome to a basic web server implementation written in  Python. You can edit the blacklist and whitelist files to change the
allowed and not allowed ip addresses, but make sure you change the settings each time you load up the server.

You can also 'flush' the database to clear all records, this can be done whenever you want but you are 
advised to do it once a week or once a day depending on the amount of traffic you get.
'''
import socket # The socket module completes all of the networking portion for the server
import serverutil # This module is written by myself and deals with starting the server and changing the server settings
import os
import datasum

class Main:
    '''
    This class is the main class will contain the methods that will run the whole server
    '''
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname()) # This line sets the ip address that the server will run on, 
                                                               # this will automatically set the value to the ip address of the machine that the server is running on
        self.port = 8080 # The server will use port 8080 which is the alternate http port
        self.datasum = datasum.DataSummary(self.host, self.port)
        self.serverutilities = serverutil.ServerOperations(self.host, self.port) # Instantiate the ServerOperations class with the ip and the port

    def main_menu(self):
        print("""
  __  __                      _                                    
 |  \/  |                    | |                                   
 | \  / |_   _  __      _____| |__    ___  ___ _ ____   _____ _ __ 
 | |\/| | | | | \ \ /\ / / _ \ '_ \  / __|/ _ \ '__\ \ / / _ \ '__|
 | |  | | |_| |  \ V  V /  __/ |_) | \__ \  __/ |   \ V /  __/ |   
 |_|  |_|\__, |   \_/\_/ \___|_.__/  |___/\___|_|    \_/ \___|_|   
          __/ |                                                    
         |___/                                                     
""")
        print("Welcome to your web server, prototype version\n")
        self.serverutilities.manage_admin_page()
        self.datasum.show_individual_requests()
        pages = os.listdir('admin/')
        for page in pages:
            if page[-5:] == '.html':
                admin_page = str(page)
                break
        print("Current admin page located at: /admin/"+admin_page)
        # The menu below allows the user to select which options they need from the list
        while True:
            option = input("Would you like to start the server [1], Change the settings [2], Flush the database [3], Add an ip to the whitelist or black list [4] exit [5]: ")
            if option == '1':
                self.serverutilities.start_server()
            elif option == '2':
                self.serverutilities.change_settings()
            elif option == '3':
                self.serverutilities.flush_db()
            elif option == '4':
                self.serverutilities.count_through_ips()
            elif option == '5':
                exit()
        
mainfunc = Main()
mainfunc.main_menu()
    
