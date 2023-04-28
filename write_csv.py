#!/usr/bin/env python3
import csv
import os
import datetime as dt

BASE_ADDR = '/media/ossila-chamber/'
DATA = [
    ['1','20','24'],
    ['2','21','25'],
    ['3','22','26'],
    ['4','23','27'],
]

def find_usb():
    if os.path.exists('/dev/sda') and os.path.ismount('/mnt') == False:
        #os.system('sudo mount /dev/sda1 /mnt')
        return True
    
    else:
        return False

def write_csv():
    global DATA

    usb_path = str(os.listdir(BASE_ADDR)[0]) + '/'
    #print('usd drive list ' + str(usb_drive_name))

    csv_name = dt.datetime.now().strftime('%m-%d-%Y_%H-%M-%S') + ".csv"

    with open(("/media/ossila-chamber/"+ usb_path + csv_name), 'w', newline='') as file:
        writer = csv.writer(file, dialect="excel")
        writer.writerow(['Time', 'RH', 'Temp. (C)'])
        for row in DATA:
            writer.writerow(row)


def main():
    if find_usb():
        write_csv()
    else:
        print("No usb found")

if __name__ == "__main__":
    main()