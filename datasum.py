import matplotlib.pyplot as plt
from matplotlib import image
from datetime import *
import serverutil
import numpy as np
import requests
import time
import json
import csv

class DataSummary:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_util = serverutil.ServerOperations(self.host, self.port)
        self.conns = self.server_util.return_connections()

    def edit_last_update(self):
        with open('last_update.txt', 'w') as f:
            current_date = datetime.now().strftime("%Y-%m-%d, %H:%M")
            f.write(str(current_date)+str(" GMT"))

    def format_connections(self):
        all_cnn = self.conns
        now = datetime.now()
        first_connection = all_cnn[0][0]
        first_conn_day = datetime.strptime(first_connection, '%Y-%m-%d %H:%M:%S.%f')
        first_conn_day = first_conn_day.day
        now = now.day 
        self.number_days = now-first_conn_day
        hour_each = []
        for row in all_cnn:
            t = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
            hour_each.append(t.hour)

        return hour_each
    
    def count_conn_hour(self):
        raw_lst_conn = self.format_connections()
        no_of_conns = []
        for i in range (24):
            no_of_conns.append(raw_lst_conn.count(i))

        return no_of_conns

    def plot_graph(self):
        arr = self.count_conn_hour()
        try:
            x_axis_items = []
            for i in range (24):
                x_axis_items.append(i)
            y_pos = np.arange(len(x_axis_items))
            plt.bar(y_pos, arr, align='center', alpha=1)
            plt.xticks(y_pos, x_axis_items)
            plt.ylabel('Number of connections')
            plt.xlabel('Hours')
            plt.title("Number of connections per hour")
            plt.savefig('admin/barchart_admin.png')
            plt.clf()
            for  i in range(len(arr)):
                arr[i] /= self.number_days
            plt.bar(y_pos, arr, align='center', alpha=1)
            plt.xticks(y_pos, x_axis_items)
            plt.ylabel('Number of connections')
            plt.xlabel('Hours')
            plt.title("Number of connections per hour avrg. over thirty days")
            plt.savefig('graphs/barchart.png')
            plt.clf()
        except IndexError:
            pass
        
    def make_pie_chart(self):
        lst = self.conns
        if not self.conns:
            return 0
        resources = []
        pages = []
        arr = []
        arr_lab = []
        other_tot = 0
        for i in lst:
            pages.append(i[2])
        for i in pages:
            if i[-5:] == '.html':
                resources.append(i)
        pages_non_unique = resources
        resources = set(resources)
        resources = list(resources)
        total_items = len(pages_non_unique)
        data_values = []
        for i in resources:
            data_values.append(pages_non_unique.count(i))
        
        for i in range (3):
            biggest_i = data_values.index(max(data_values))
            arr_lab.append(resources[biggest_i])
            arr.append(data_values[biggest_i])
            del data_values[biggest_i]
            del resources[biggest_i]

        for i in range (len(data_values)):
            other_tot += data_values[i]

        arr_lab.append('Other')
        arr.append(other_tot)

        for i in range(len(arr)):
            arr[i] = (arr[i]/total_items)*100

        try:
            explode = (0, 0.1, 0, 0)
            fig1, ax1 = plt.subplots()
            ax1.pie(arr, explode=explode, labels = arr_lab, autopct = '%1.1f%%', shadow=True, startangle = 90)
            ax1.axis('equal')
            plt.savefig('graphs/piechart.png')
            plt.clf()
        except IndexError:
            pass

    def geo_ip(self):
        ip_addrs = []
        for i in self.conns:
            ip_addrs.append(i[1])
        continents_used = []
        countries = []
        ip_addrs = set(ip_addrs)
        ip_addrs = list(ip_addrs)
        ip_addrs = ip_addrs[-3:]
        for i in range(3):
            try:
                r = requests.get('https://ipapi.co/'+ip_addrs[i]+'/json/')
                loc_data = json.loads(r.text)
                continent = loc_data["continent_code"]
                country = loc_data["country_name"]
                time.sleep(2)
            except KeyError:
                continent = 'Unknown'
                country = 'Unknown'

            continents_used.append(continent)
            countries.append(country)
        
        continents = {'AF': '2000, 1000', 'AS': '2750, 700', 'EU': '2000, 500', 'NA': '600, 600', 'OC': '3600, 1625', 'SA': '1100, 1400', 'Unknown': '0, 0'}

        with open("admin/last_three_countries.txt", 'w') as f:
            for item in countries:
                f.write(item+' ')

        for i in range(len(continents_used)):
            continents_used.append(continents.get(continents_used[i]))
        
        del continents_used[:3]
        img = image.imread("map.png")
        for i in range (len(continents_used)):
            country = continents_used[i].split(', ')
            coord_1 = country[0]
            coord_2 = country[1]
            plt.plot(int(coord_1), int(coord_2), marker='o', color='red')
        plt.imshow(img)
        plt.savefig('graphs/map.png')
        plt.clf()
    
    def show_individual_requests(self):
        content_req = []
        conns = self.conns
        for i in conns:
            content_req.append(tuple((i[1], i[2])))
        
        with open('admin/requests.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for item in content_req:
                writer.writerow(item)
            


