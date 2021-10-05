# -*- coding: utf-8 -*-
######################################################################################################################################################
"""
Created on Wed Aug 21 14:58:07 2019
@author: Emi_Valmed

Modified on Wed Oct 09 11:08:25 2019 by Emi_Valmed
Modifications : 
    -Add line 34. Removing all the leading and trailing whitespace characters.
    -Solve the problem "Error tokenizing data" (line 63): stations without measurements at the beginning of the series.

"""
######################################################################################################################################################
# LIBRERIES
######################################################################################################################################################
import os
import sys
import requests
import pandas as pd
import tkinter as tk
import scipy.io as sio
from bs4 import BeautifulSoup
from tkinter import filedialog
from datetime import datetime, date
######################################################################################################################################################

######################################################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Open file with catchment code 
#-----------------------------------------------------------------------------------------------------------------------------------------------------
root    = tk.Tk()
entrada = filedialog.askopenfile(mode='r')
root.destroy()
if (entrada == None):
    #Exit = tk.raw_input('\tInput file not selected. \n\t\tPress enter to exit.\n')
    sys.exit()
pathname = os.path.dirname(entrada.name)                                       # Define the working path equal to that of the input file
os.chdir(pathname)                                                             # Change your work path.

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Pick all ids from the stations and put them in a list
#-----------------------------------------------------------------------------------------------------------------------------------------------------
Content = entrada.read().split("\n")                                           
content_lineStation = [String.strip()  for String in Content]
#content_lineStation.remove('')                                                                        
print(content_lineStation, "\n")

SurfaceBV = []
destination_folder_path = './'

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Web scraping MDDELCC data
#-----------------------------------------------------------------------------------------------------------------------------------------------------
for station in content_lineStation:
    urls = ['https://www.cehq.gouv.qc.ca/depot/historique_donnees/fichier/'+ station + '_Q.txt']
    text = station+ '_Q'
    lista = ['body']
    
    
    with open(str(text) +'.txt', 'w', encoding='utf-8') as outfile:
        for url in urls:
            website = requests.get(url)
            soup = BeautifulSoup(website.content, 'lxml') 
            tags = soup.find_all(lista)
            text = [''.join(s.findAll(text=True)) for s in tags]
            
            text_len = len(text)
            for item in text:
                print(item, file=outfile)               
                temp2 = open(str(station) + '_Q.txt','r').readlines()          # Getting all lines from file                
                temp3 =  temp2[6].split(' ')
                Surface = float(temp3[2])
                SurfaceBV.append(Surface)
                open(str(station) + '_Q.csv','w').writelines(temp2[42:])
                Data = pd.read_csv(str(station) + '_Q.csv',  delim_whitespace=True, skip_blank_lines  = True, na_filter=True)
                del Data['Remarque']
                Data.columns = ['Station', 'Date', 'Q','Remarque'] 
                           
                # Setting the Date
                Data['Date'] = pd.to_datetime(Data['Date'])  
                Data['Date'] = Data['Date'].apply(datetime.toordinal)
                
                #Setting Q (Qmm <- Qm3s*86.4/BasinArea)
                Data['Q'] = Data['Q']* 86.4 /Surface
                
                # Exporting .mat file
                Data = Data[['Date','Q']]                                        
                sio.savemat(os.path.join(destination_folder_path,str(station) + '_Q'), {name: col.values for name, col in Data.items()})
                print('Done! Your file was saved with success')
                           
                
    # Removing the .txt file #and .csv files
    os.remove(str(station) + '_Q.txt')
    #os.remove(str(station) + '_Q.csv')

# Exporting surfaces
Surfaces = pd.DataFrame(list(zip(content_lineStation,SurfaceBV)), columns = ['Station','Surface'])                
sio.savemat(os.path.join(destination_folder_path,'SurfaceBVs'), {name: col.values for name, col in Surfaces.items()}) 


sio.savemat(os.path.join(destination_folder_path,'SurfaceBVs'), Surfaces) 
                             
