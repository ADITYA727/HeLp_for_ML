"""
reading data based on difference between the readings

"""



import pandas as pd

m_data=pd.read_("/home/stealth/Desktop/analysis/UP 100 Fuel V2.xlsx")

"""
0 = S.No.
1 =  Terminal ID
2 =  Merchant
3 = BatchID/ROC
4 =  Account Number
5 =  Vehicle Number
6 = Transaction Date
7 = Transaction Type
8 = Product
9 = Price
10 = Volume(Ltr.)
11 = Currency
12 = Service Charge
13 = Amount(Rs.)
14 = CCMS/Cash Balance(Rs.)
15 = Odometer Reading
16 = Drivestars
17 = RewardType
18 = Cheque No
19 = MICR Code
20 = Status

"""

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




def average_and_mileage(index,i):

    data[col[15]][index[i + 1]] = (int(data[col[15]][index[i]]) + int(data[col[15]][index[i + 2]])) / 2
    data["Corrected"][index[i + 1]] = "Y"
def change_first(index, i,val2):
    print("Inside First")
    data[col[15]][index[i]] = int(data[col[15]][index[i+1]]) -val2
    data["Corrected"][index[i]] = "Y"

def update_table(index,i):
    if data[col[15]][index[i + 1]] !='-' and data[col[15]][index[i + 1]] !='0' :
        val1 = int(data[col[15]][index[i + 1]]) - int(data[col[15]][index[i]])
        val2 = int(data[col[15]][index[i + 2]]) - int(data[col[15]][index[i + 1]])
        val3 = int(data[col[15]][index[i + 2]]) - int(data[col[15]][index[i]])

        if val1>=0 and val2<0 and val3>=0:
                average_and_mileage(index, i)
        elif val1<0 and val2>0 and val3>0:
                average_and_mileage(index, i)
    else:
        average_and_mileage(index, i)




def correct_odometer(acc):

    account_info=m_data[m_data[col[4]]==acc]
    account_info[col[6]]=pd.to_datetime(account_info[col[6]], format="%d/%m/%y %H:%M")
    account_info=account_info.sort_values(col[6])
    print(account_info)
    index=account_info.index

    # last element
    if len(index)!=1:
        data["Corrected"][index[len(index)-1]] = "N"
    for i in range(0,len(index)-2):   #-----------------------
        if (data[col[15]][index[i]]!='-'  and data[col[15]][index[i]]!='0') and (data[col[15]][index[i+2]]!='-' and data[col[15]][index[i+2]]!='0'):
            update_table(index, i)


col=m_data.columns
account=m_data[col[4]].unique()
import tqdm
data=pd.DataFrame(index=m_data.index, columns=[col[15],"Corrected"])
data[col[15]]=m_data[col[15]]
data["Corrected"]="N"
for acc in tqdm.tqdm(list(account)):
    correct_odometer(acc)
m_data["Odometer_New"]=data[col[15]]
m_data["Corrected"]=data["Corrected"]


