
"""
correct and incorrect data

"""



import pandas as pd


"""
0 SNo.
1  Terminal ID
2  Merchant Name 
3  Location
4  Customer ID/Card PAN
5  Vehicle No.
6  Txn Date
7  Txn Type
8  Product
9  Currency 
10  RSP
11  Quantity
12  Amount
13  Balance
14 Entitled CashBack
15  Odometer
16  Status


"""
list_inc=[]
list_cor=[]
def change(data):
    odometer=list(data['Odometer_New'])
    change=0
    for i in range(0,len(odometer)-1):
        if odometer[i+1]!='-' and odometer[i]!='-' and odometer[i+1]!='0' and odometer[i]!='0':
            if float(odometer[i+1])-float(odometer[i])<=0:
                change=1
        else:
            change=1
            break

    if change==1:
        data['Field_Status']='Incorrect'
        list_inc.append(data)
    else:
        print("Hii")
        data['Field_Status'] = 'Correct'
        list_cor.append(data)
def insert_dataframe(input_data):
    for i in range(1,5):
        data=input_data[input_data['Month']==i]
        data=data.sort_values(col[6])
        change(data)

m_data=pd.read_csv("/home/stealth/Desktop/analysis/iocl_new.csv")
col=list(m_data.columns)
col.append('Month')
#format for IOCL
#m_data[col[6]]=pd.to_datetime(m_data[col[6]], format="%d/%m/%y %H:%M")
#format for HPCL
m_data[col[6]]=pd.to_datetime(m_data[col[6]], format="%Y-%m-%d %H:%M")

m_data['Month']=[t.month for t in m_data[col[6]]]

accounts=m_data[col[4]].unique()

for acc in accounts:
    input_data=m_data[m_data[col[4]]==acc]
    insert_dataframe(input_data)


incorrect_data=pd.concat(list_inc)
correct_data=pd.concat(list_cor)

frame=[incorrect_data,correct_data]
whole_data=pd.concat(frame)

