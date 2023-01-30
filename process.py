'''
This module handles taking the request data, interpreting it and sending the correct response back
'''
from datetime import date, datetime
import sqlite3
import os
from sqlite3.dbapi2 import Connection, connect
import datasum

class ProcessRequests:
    def __init__ (self, addr):
        self.address = addr
        self.connections = sqlite3.connect('Connections.db')
        self.datasum = datasum.DataSummary(1, 1)
        with open("admin/admin_ip.txt", 'r') as f:
            self.admin_ip = f.read()

    # This method saves simply just the ip address of the node that made the request along with the time of the request
    def save_connection(self, ip, data_req):
        now = datetime.now()
        self.connections.execute('INSERT INTO Connections VALUES (?, ?, ?);',
                                (now, ip, data_req,))
        self.connections.commit()
    
    # This takes two datetime datatypes and works out the difference between the two of them 
    def check_time_diff(self, time1, time2):
        datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        diff = datetime.strptime(str(time1), datetimeFormat) - datetime.strptime(str(time2), datetimeFormat)
        return diff

    # This takes the arguments from the server utilities and then uses them to perform the request given to it 
    def get_ipaddr(self, connection, request_info, whitelist_on, blacklist_on, timeouttime):
        self.ipaddr = self.address[0] # Takes the origin address from the tuple that stores the address and the port the request came from
        log_file = "logs\log-"+str(date.today())+".txt"
        print("Connection from:", self.ipaddr)
        connect_line = "Connection from: "+str(self.ipaddr)
        f = open(log_file, "a")
        f.write(connect_line)
        f.write("\n"+str(request_info)+"\n")
        self.complete_request(connection, request_info, whitelist_on, blacklist_on, timeouttime) # This completes the request from the data supplied to it by the other methods

    def form_request(self, connection, requested_page):
        # This specifically interprets the request and sends back the appropriate response
        if requested_page == '/': # If no data is supplied in the URI, a / will be sent, this clause allows the server to point towards the index page is no data is supplied 
            requested_page = 'index.html'
        else:
            requested_page = requested_page[1:len(requested_page)] # This takes the / off the start of the request and sets the requested_page var equal to the page in the request

        if not os.path.isfile(requested_page):
            requested_page = '404.html'
        
        if requested_page[0:4] == 'logs/':
            requested_page = 'index.html'
        
        if requested_page[0:6] == 'admin/' and requested_page[-4:] == '.csv' and self.ipaddr != self.admin_ip:
            requested_page = 'index.html'

        if requested_page == 'last_three_countries.txt':
            requested_page = 'index.html'

        if requested_page == 'graphs.html':
            self.datasum.edit_last_update()
            self.datasum.plot_graph()
            self.datasum.make_pie_chart()
            self.datasum.geo_ip()

        with open(requested_page, 'rb') as p: # Otherwise it will set the response body to the html that is inside whichever page was requested
            response_body = p.read()

        response_line = b"HTTP/1.1 200 OK \r\n" # The response line will be the HTTP version and a 200. 200 is the HTTP code for a successful reqeuest
        http_headers = b"".join([b"Server: HTTP server\r\n", b"Content-Type: text/html\r\n\r\n"]) # Tells the client to receive the data as HTML so that the browser can show the webpage
        request = b"".join([response_line, http_headers, response_body]) # Joins all of the parts of the system together to create a full request
        connection.sendall(request) # Sends the request back to the client
        return requested_page

    def read_request(self, request):
        request = str(request).split('\r\n') # This will split the given HTTP request into it's separate lines that will allow it to be read, piece by piece
        index_page = 'index.html' # This will set the default page that will be returned on an errored request
        first_part = request[0]
        first_part_lst = first_part.split(" ") # This takes the first line which will be the request type, the URI and then the HTTP version and splits that into a smaller list
        try:
            requested_page = first_part_lst[1] # This tries to read the URI and return the name of the page requested
            return requested_page
        except IndexError: # If a URI can't be found, the index page will be set as the default page requested
            return index_page

    def complete_request(self, connection, request_info, whitelist_on, blacklist_on, timeouttime):
        '''
        This method puts all of the other methods into use to actually complete the request
        '''
        self.whitelist_on = whitelist_on
        self.blacklist_on = blacklist_on
        lessthanallowedtime = False
        self.allowed_ip = True

        if self.whitelist_on:
            self.allowed_ip = False
            for row in self.connections.execute('SELECT * FROM Connections WHERE IPAddress = ?', (self.ipaddr,)):
                diff = self.check_time_diff(datetime.now(), row[0])
                if diff.days > 0 or diff.seconds > timeouttime:
                    lessthanallowedtime = False
                else:
                    lessthanallowedtime = True

            for row in self.connections.execute('SELECT * FROM Whitelist WHERE IPaddr = ?', (self.ipaddr,)):
                self.allowed_ip = True
                break
                    
        # This does the same function as the whitelist, except the other way round
        if self.blacklist_on:
            self.allowed_ip = True
            for row in self.connections.execute('SELECT * FROM Connections WHERE IPAddress = ?', (self.ipaddr,)):
                diff = self.check_time_diff(datetime.now(), row[0])
                if diff.days > 0 or diff.seconds > timeouttime:
                    lessthanallowedtime = False
                else:
                    lessthanallowedtime = True

            for row in self.connections.execute('SELECT * FROM Blacklist WHERE IPaddr = ?', (self.ipaddr,)):
                self.allowed_ip = False
                break
         
        # If the IP address is not making requests too fast, is in the whitelist (if turned on) and is not in the blacklist (if turned on) then the server will carry out the request
        if not lessthanallowedtime and self.allowed_ip:
            page_to_send = self.read_request(request_info)
            req_page = self.form_request(connection, page_to_send)
            print("Request completed")
            self.save_connection(self.ipaddr, req_page)
        else:
            connection.sendall(b"Slow down")




        