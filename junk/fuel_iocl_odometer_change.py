"""

Acocunt iocl data

"""



import os,sys
import pandas as pd
import tqdm
from datetime import datetime

path='/home/stealth/Desktop/fueldata/iocl1/'


"""

Index(['SNo.', ' Terminal ID', ' Merchant Name ', ' Location',
       ' Customer ID/Card PAN', ' Vehicle No.', ' Txn Date', ' Txn Type',
       ' Product', ' Currency ', ' RSP', ' Quantity', ' Amount', ' Balance',
       'Entitled CashBack', ' Odometer', ' Status'],
      dtype='object')


"""

def ordered_preprocess(data):
    product = list(data)
    product = ','.join(str(p) for p in product)
    return product

def preprocessing(data):
    product = list(set(data))
    product = ','.join(str(p) for p in product)
    return product

def odometer_reading(data):
    flag=1
    # print(data['Odometer'])
    reading=list(data[' Odometer'])
    missing_count=reading.count('0')
    if '0' in reading or '-' in reading:
        distance_covered = '0'
        change = 'reading_missing'
    else:
        if data.shape[0] == 1:
            distance_covered = 0
            change = 'one_reading'
        else:
            distance_covered=int(data[' Odometer'].head(1))-int(data[' Odometer'].tail(1))
            for i in range(0,data.shape[0]-1):
                if (int(data[' Odometer'][i])-int(data[' Odometer'][i+1]))<=0:
                        flag=0
            if flag==0:
                change='Negative'
            else:
                change='Positive'
    return distance_covered, change, missing_count

def get_df_and_data_dict(df,value,filter):
    data_dict = dict()
    if filter == 'Account':
        df_sub = df[df[' Customer ID/Card PAN'] == value]
        df_sub = df_sub.reset_index(drop=True)

        data_dict['Vehicle_Number'] = preprocessing(df_sub[' Vehicle No.'])
        data_dict['Account_Number'] = value

        vh_split = len(data_dict['Vehicle_Number'].split(','))
        if vh_split > 1:
            data_dict['Multi_Vehicle'] = 'Y'
        else:
            data_dict['Multi_Vehicle'] = 'N'
        df = df.drop(df[df[' Customer ID/Card PAN'] == value].index)
        df = df.reset_index(drop=True)

    else:
        df_sub = df[df[' Vehicle No.'] == value]
        df_sub = df_sub.reset_index(drop=True)

        data_dict['Account_Number'] = preprocessing(df_sub[' Customer ID/Card PAN'])
        data_dict['Vehicle_Number'] = value

        acc_split = len(data_dict['Account_Number'].split(','))
        if acc_split > 1:
            data_dict['Multi_Account'] = 'Y'
        else:
            data_dict['Multi_Account'] = 'N'
        df = df.drop(df[df[' Vehicle No.'] == value].index)
        df = df.reset_index(drop=True)

    return df_sub,data_dict,df

def get_data_fields(data_dict,df_sub, month):
    data_dict['Month'] = month
    data_dict['Total_Amount'] = df_sub[' Amount'].sum()
    data_dict['Product'] = preprocessing(df_sub[' Product'])
    data_dict['Odometer_Reading'] = ordered_preprocess(df_sub[' Odometer'])
    data_dict['Transaction_Date'] = preprocessing(df_sub[' Txn Date'])
    data_dict['Transaction_Type'] = preprocessing(df_sub[' Txn Type'])
    data_dict['Currency'] = preprocessing(df_sub[' Currency '])
    data_dict['Distance_Covered'], data_dict['Odometer_Change'], data_dict['Reading_Missed'] = odometer_reading(df_sub)
    try:

        vn = data_dict['Vehicle_Number'].split('G')[1]

    except Exception as e:
        print(data_dict['Vehicle_Number'])
        vn='U'

    if len(data_dict["Product"])>1:
        if vn!='U':
            try:
                vn=vn.split(' ')[1]
            except Exception as e:
                print(e)
            if int(vn)>3200:
                data_dict['Product_Category']= 'PETROL'
            else:
                data_dict['Product_Category'] = 'DIESEL'

        else:
            print(vn)
            data_dict['Product_Category'] = vn
    else:
        data_dict['Product_Category'] = data_dict['Product']

    if data_dict['Product_Category']=='DIESEL':
        if data_dict['Total_Amount']>20000:
            data_dict["Limit_Exceeds"]="Y"
        else:
            data_dict["Limit_Exceeds"] = "N"

    elif data_dict['Product_Category']=='PETROL':
        if data_dict['Total_Amount'] > 5000:
            data_dict["Limit_Exceeds"] = "Y"
        else:
            data_dict["Limit_Exceeds"] = "N"

    temp=df_sub[' RSP']
    if 0 in list(temp):
        temp=temp[temp!=0]
    if '-' in list(temp):
        temp = temp[temp != '-']
    data_dict['Price'] = (temp.astype(float)).mean()
    temp=df_sub[' Quantity']
    if 0 in list(temp):
        temp = temp[temp != 0]
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
        filter_option=df[' Customer ID/Card PAN'].unique()
    else:
    #primary key is Vehicle No.
        filter_option=df[' Vehicle No.'].unique()
    for value in tqdm.tqdm(filter_option):
        # to get the subdataframe and dropped rows from dataframe df
        df_sub,data_dict,df= get_df_and_data_dict(df,value,filter)

        # get the common datafields
        data_dict=get_data_fields(data_dict, df_sub, month)
        data_dict_list.append(data_dict)
    return data_dict_list

data_account=[]
data_vehicle=[]
for filename in os.listdir(path):
    print(filename)
    if '#' not  in filename:
        data=pd.read_csv(path+filename, delimiter=',')
        data[' Odometer']=data[' Odometer']
        data[' Product']=data[' Product']
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
        data = data[data[col[5]].str.contains('UP', na=False)]
        data_account.extend(data_based_on_filter(data, mon,'Account'))
        data_vehicle.extend(data_based_on_filter(data, mon,'Vehicle'))
account = pd.DataFrame(data_account)
vehicle = pd.DataFrame(data_vehicle)

account = account.sort_values('Month')
vehicle = vehicle.sort_values('Month')

# df_list.append(account)
# diesel_vehicle=account[(account['Total_Amount']>20000) & account['Product'].str.contains('DIESEL')]
# diesel_vehicle=diesel_vehicle.reset_index(drop=True)

# petrol_vehicle=account[(account['Product'].str.contains('PETROL'))]
# petrol_vehicle=petrol_vehicle.reset_index(drop=True)
