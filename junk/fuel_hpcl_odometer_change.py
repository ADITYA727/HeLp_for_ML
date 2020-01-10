
import os,sys
import pandas as pd
import tqdm
from datetime import datetime

path='/home/stealth/Desktop/fueldata/hpcl/'


def ordered_preprocess(data):
    product = list(data)
    product = ','.join(p for p in product)
    return product

def preprocessing(data):
    product = list(set(data))
    product = ','.join(str(p) for p in product)
    return product

def odometer_reading(data):
    flag=1
    # print(data['Odometer Reading'])
    reading=list(data['Odometer Reading'])
    missing_count=reading.count('-')
    missing_per=(missing_count/len(reading))*100
    if '-' in reading:
        distance_covered = 0
        change = 'reading_missing'
    else:
        if data.shape[0] == 1:
            distance_covered = 0
            change = 'one_reading'
        else:
            distance_covered=int(data['Odometer Reading'].head(1))-int(data['Odometer Reading'].tail(1))
            for i in range(0,data.shape[0]-1):
                if (int(data['Odometer Reading'][i])-int(data['Odometer Reading'][i+1]))<=0:
                        flag=0
            if flag==0:
                change='Negative'
            else:
                change='Positive'
    return distance_covered, change, missing_count, missing_per

def get_df_and_data_dict(df,value,filter):
    data_dict = dict()
    if filter == 'Account':
        df_sub = df[df[' Account Number'] == value]
        df_sub = df_sub.reset_index(drop=True)

        data_dict['Vehicle_Number'] = preprocessing(df_sub[' Vehicle Number'])
        data_dict['Account_Number'] = value

        vh_split = len(data_dict['Vehicle_Number'].split(','))
        if vh_split > 1:
            data_dict['Multi_Vehicle'] = 'Y'
        else:
            data_dict['Multi_Vehicle'] = 'N'
        df = df.drop(df[df[' Account Number'] == value].index)
        df = df.reset_index(drop=True)

    else:
        df_sub = df[df[' Vehicle Number'] == value]
        df_sub = df_sub.reset_index(drop=True)

        data_dict['Account_Number'] = preprocessing(df_sub[' Account Number'])
        data_dict['Vehicle_Number'] = value

        acc_split = len(data_dict['Account_Number'].split(','))
        if acc_split > 1:
            data_dict['Multi_Account'] = 'Y'
        else:
            data_dict['Multi_Account'] = 'N'
        df = df.drop(df[df[' Vehicle Number'] == value].index)
        df = df.reset_index(drop=True)

    return df_sub,data_dict,df

def get_data_fields(data_dict,df_sub, month):
    data_dict['Month'] = month
    data_dict['Total_Amount'] = df_sub['Amount(Rs.)'].sum()
    data_dict['Product'] = preprocessing(df_sub['Product'])
    data_dict['Odometer_Reading'] = ordered_preprocess(df_sub['Odometer Reading'])
    data_dict['Transaction_Date'] = ordered_preprocess(df_sub['Transaction Date'])
    data_dict['Transaction_Type'] = preprocessing(df_sub['Transaction Type'])
    data_dict['Currency'] = preprocessing(df_sub['Currency'])
    data_dict['Distance_Covered'], data_dict['Odometer_Change'], data_dict['Reading_Missed'], data_dict['RM_Percentage'] = odometer_reading(df_sub)
    data_dict['Merchant_Name']=preprocessing(df_sub[" Merchant"])
    try:
        vn = data_dict['Vehicle_Number'].split('G')[1]
    except Exception as e:
        print(data_dict['Vehicle_Number'])
        vn = 'U'

    if len(data_dict["Product"].split(','))>1:
        #print(data_dict["Product"])
        if vn != 'U':
            if int(vn) > 3200:
                data_dict['Product_Category'] = 'PETROL'
            else:
                data_dict['Product_Category'] = 'DIESEL'

        else:
            data_dict['Product_Category'] = 'U'
    else:
        data_dict['Product_Category'] = data_dict['Product']


    if data_dict['Product_Category'] == 'DIESEL':
        if data_dict['Total_Amount'] > 20000:
            data_dict["Limit_Exceeds"] = "Y"
        else:
            data_dict["Limit_Exceeds"] = "N"

    elif data_dict['Product_Category'] == 'PETROL':
        if data_dict['Total_Amount'] > 5000:
            data_dict["Limit_Exceeds"] = "Y"
        else:
            data_dict["Limit_Exceeds"] = "N"
    else:
        data_dict["Limit_Exceeds"] = "U"


    temp=df_sub['Price']

    if '-' in list(temp):
        temp=temp[temp!='-']
    data_dict['Price'] = (temp.astype(float)).mean()
    temp=df_sub['Volume(Ltr.)']
    if '-' in list(temp):
        temp = temp[temp != '-']
    data_dict['Volume'] = (temp.astype(float)).sum()

    if ('PETROL' in data_dict['Product']) and ('DIESEL' in data_dict['Product']):
        data_dict['Multi_Product'] = 'Y'
    else:
        data_dict['Multi_Product'] = 'N'
    return data_dict


def data_based_on_filter(df,month, filter):

    data_dict_list = list()
    # primary key is account
    if filter=='Account':
        filter_option=df[' Account Number'].unique()
    else:
    #primary key is vehicle number
        filter_option=df[' Vehicle Number'].unique()
    for value in tqdm.tqdm(filter_option):
        # to get the subdataframe and dropped rows from dataframe df
        df_sub,data_dict,df= get_df_and_data_dict(df,value,filter)

        # get the common datafields
        data_dict=get_data_fields(data_dict, df_sub, month)
        data_dict_list.append(data_dict)
    return data_dict_list








"""
def data_based_on_vehicle_no(df,month):
    data_vehicle_list = list()

    veh_no = df[' Vehicle Number'].unique()
    for vehicle in tqdm.tqdm(veh_no):
        data_vehicle = dict()
        df_sub = df[df[' Vehicle Number'] == vehicle]
        df_sub = df_sub.reset_index(drop=True)
        data['Month']=month
        data_vehicle['Vehicle_Number'] = vehicle
        data_vehicle['Total_Amount'] = df_sub['Amount(Rs.)'].sum()
        data_vehicle['Product'] = preprocessing(df_sub['Product'])
        data_vehicle['Account_Number'] = preprocessing(df_sub[' Account Number'])
        data_vehicle['Transaction_Type'] = preprocessing(df_sub['Transaction Type'])
        data_vehicle['Currency'] = preprocessing(df_sub['Currency'])
        data_vehicle['Odometer_Reading'] = ordered_preprocess(df_sub['Odometer Reading'])
        acc_split=len(data_vehicle['Account_Number'].split(','))
        data_vehicle['Distance_Covered'], data_vehicle['Odometer_Change'], data_vehicle['Reading_Missed'] = odometer_reading(df_sub)
        if ('PETROL' in data_vehicle['Product']) and ('DIESEL' in data_vehicle['Product']):
            data_vehicle['Multi_Product'] = 'Y'
        else:
            data_vehicle['Multi_Product'] = 'N'
        if acc_split>1:
            data_vehicle['Multi_Account']='Y'
        else:
            data_vehicle['Multi_Account']='N'
        data_vehicle_list.append(data_vehicle)
        df = df.drop(df[df[' Vehicle Number'] == vehicle].index)
        df = df.reset_index(drop=True)
    return data_vehicle_list
"""
"""
def get_price_and_update_data(df, data_list):
    print('recursion')
    if df.shape[0]==1 or df.shape[0]==0:
        print('end')
        return data_list
    else:
        data_vehicle = dict()
        print(df.shape)
        df_sub = df[df[' Account Number'] == df[' Account Number'][0]]
        data_vehicle[' Account Number']=df[' Account Number'][0]
        data_vehicle['Total Amount']=df_sub['Amount(Rs.)'].sum()
        data_vehicle['Product']= preprocessing(df_sub['Product'])
        data_vehicle[' Vehicle Number'] = preprocessing(df_sub[' Vehicle Number'])
        data_vehicle['Transaction Type']=preprocessing(df_sub['Transaction Type'])
        data_vehicle['Currency']=preprocessing(df_sub['Currency'])
        data_list.append(data_vehicle)
        df=df.drop(df[df[' Account Number'] == df[' Account Number'][0]].index)
        df = df.reset_index(drop=True)
        get_price_and_update_data(df,data_list)
        return data_list
"""
data_account=[]
data_vehicle=[]
for filename in os.listdir(path):
    print(filename)
    if '#' not in filename and 'csv' in filename:

        data=pd.read_csv(path+filename, delimiter=',')
        month=filename.split('_')[1].split('.')[0]
        if month=='jan':
            mon=1
        elif month=='feb':
            mon=2
        elif month=='march':
            mon=3
        elif month=='april':
            mon=4
        col=data.columns
 
        data_account.extend(data_based_on_filter(data, mon,'Account'))
        data_vehicle.extend(data_based_on_filter(data, mon,'Vehicle'))
account = pd.DataFrame(data_account)
account = account.sort_values('Month')
account = account.reset_index(drop=True)
vehicle = pd.DataFrame(data_vehicle)
vehicle = vehicle.sort_values('Month')
vehicle = vehicle.reset_index(drop=True)

# df_list.append(account)
# diesel_vehicle=account[(account['Total_Amount']>20000) & account['Product'].str.contains('DIESEL')]
# diesel_vehicle=diesel_vehicle.reset_index(drop=True)

# petrol_vehicle=account[(account['Product'].str.contains('PETROL'))]
# petrol_vehicle=petrol_vehicle.reset_index(drop=True)
