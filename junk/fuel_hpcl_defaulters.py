"""
account hpcl data

"""



import pandas as pd
import tqdm


data=pd.read_csv('/home/stealth/Desktop/analysis/whole_data_hpcl.csv',sep=',')
#data=pd.read_csv('/home/stealth/Desktop/analysis/iocl_new.csv', sep=',')

"""
['S.No', ' Terminal ID', ' Merchant', 'BatchID/ROC', ' Account Number',
       ' Vehicle Number', 'Transaction Date', 'Transaction Type', 'Product',
       'Price', 'Volume(Ltr.)', 'Currency', 'Service Charge', 'Amount(Rs.)',
       'CCMS/Cash Balance(Rs.)', 'Odometer Reading', 'Drivestars',
       'RewardType', 'Cheque No', 'MICR Code', 'Status', 'Odometer_New',
       'Corrected', 'Month', 'Field_Status']

"""


dataframe_list=list()

def preprocessing(data):
    product = list(set(data))
    product = ','.join(str(p) for p in product)
    return product

def reading_missed(reading, type):
    #reading_missed = reading[(reading=='0') | (reading=='-')].count()
    pos_count=0
    reading=list(reading)
    total_reading = len(reading)
    if len(reading)>1:
        for i  in range(0,(len(reading)-1)):
            #print('i',reading[i])
            # print('i+1',reading[i+1])
            if (float(reading[i+1])-float(reading[i]))>0:
                pos_count=pos_count+1
    else:
        if reading[0]==0:
            pos_count=0
        else:
            pos_count = 1
        total_reading = 2
    # print("lengths ======>", total_reading)
    # print("count positive====>",pos_count)

    percentage=(pos_count/(total_reading-1))*100
    if type=='Merchant':
        return pos_count,total_reading-1
    else:
        return percentage


def reading_category(df_dict):
    if df_dict['Account_Percentage']>=80:
        category=1
    elif df_dict['Account_Percentage']>=60 and df_dict['Account_Percentage']<80:
        category=2
    elif df_dict['Account_Percentage']>=40 and df_dict['Account_Percentage']<60:
        category=3
    elif df_dict['Account_Percentage']>=20 and df_dict['Account_Percentage']<40:
        category=4
    else:
        category=5
    return category



def limit_exceed_and_reaidng(data_dict):
    try:
        val=[]
        for i in data_dict['Vehicle_Number'].split(','):
            vn = i.split('G')[1]
            try:
                vn = vn.split(' ')[1]
            except Exception as e:
                print(e)
            if int(vn)>3200:
                val.append('y')
            else:
                val.append('n')
        if 'y' in val and 'n' in val:
            data_dict['Product_Category'] = 'PETROL,DIESEL'
        elif 'y' in val:
            data_dict['Product_Category'] = 'PETROL'
        else:
            data_dict['Product_Category'] = 'DIESEL'

        vn = data_dict['Vehicle_Number'].split('G')[1]
        # print("Vehicle===",vn)

    except Exception as e:
        print(data_dict['Vehicle_Number'])
    if data_dict['Product_Category'] == 'DIESEL':
        if data_dict['Actual_Amount'] > 20000:
            data_dict["Limit_Exceeds"] = "Y"
        else:
            data_dict["Limit_Exceeds"] = "N"

    elif data_dict['Product_Category'] == 'PETROL':
        if data_dict['Actual_Amount'] > 5000:
            data_dict["Limit_Exceeds"] = "Y"
        else:
            data_dict["Limit_Exceeds"] = "N"
    elif data_dict['Product_Category'] == 'PETROL,DIESEL':
        data_dict["Limit_Exceeds"] = "M"


def status(mer,acc):
    if mer>=75:
        if acc>=75:
            status='Proper'
        else:
            status='Merchant_Proper'
    else:
        if acc>=75:
            status='Account_Proper'
        else:
            status='Improper'
    return status

def merchant_percentage(account):
    total_pos=0
    total=0
    for acc in account:
        mer_acc_data = mer_data[mer_data[col[4]]==acc]
        mer_acc_data = mer_acc_data.sort_values(col[6])
        pos_count,total_count=reading_missed(mer_acc_data['Odometer_New'],'Merchant')
        total_pos=total_pos + pos_count
        total=total + total_count
    mer_percentage=(total_pos/total)*100
    return  mer_percentage

def cal_mileage(hpcl, acc):

    hpcl = hpcl.sort_values('Transaction Date')
    vehicles = hpcl[' Vehicle Number'].unique()
    vehicles_mileage = {}
    vehicle_df = hpcl[hpcl[' Account Number'] == acc]
    odometer_readings = vehicle_df['Odometer_New']
    tmp_df = vehicle_df[vehicle_df['Field_Status'] == 'Correct']
    try:
        first_index = tmp_df['Odometer_New'].index[0]
    except IndexError:
        return 0,0,0,0

    last_index = tmp_df['Odometer_New'].index[-1]

    vehicle_df = vehicle_df.loc[first_index:last_index, :]

    odometer_readings = vehicle_df['Odometer_New']
    odometer_diff = float(odometer_readings.iloc[-1]) - float(odometer_readings.iloc[0])
    fuel_used = sum(map(float, vehicle_df['Volume(Ltr.)'][:-1]))
    amount_spent = sum(map(float, vehicle_df['Amount(Rs.)'][:-1]))
    try:
        mileage = round(odometer_diff / fuel_used, 2)
    except ZeroDivisionError:
        mileage=0
    try:
        km_per_rs = round(odometer_diff / amount_spent, 2)
    except ZeroDivisionError:
        km_per_rs=0
    return fuel_used, amount_spent,mileage, km_per_rs


def make_data(df_dict,mer_account_data,acc,mer_percentage):
    df_list=[]
    for month in range(1,5):
        # print('month===>',month)
        mer_acc_data = mer_account_data[mer_account_data['Month']==month]
        # print("Shape",mer_acc_data.shape[0])
        if mer_acc_data.shape[0]!=0:
            mer_acc_data = mer_acc_data.sort_values(col[6])
            mer_acc_data = mer_acc_data.reset_index(drop=True)
            df_dict['Merchant_Percentage'] = mer_percentage
            df_dict['Account_Number'] = acc
            acc_percentage = reading_missed(mer_acc_data['Odometer_New'], 'Account')
            df_dict['Account_Percentage'] = acc_percentage
            df_dict['Reading_Category'] = reading_category(df_dict)
            df_dict['Status'] = status(mer_percentage, acc_percentage)
            df_dict['Vehicle_Number']= preprocessing(mer_acc_data[col[5]])
            df_dict['Total_Readings']= mer_acc_data['Odometer_New'].shape[0]
            df_dict['Reading_Missed'] = mer_acc_data[mer_acc_data['Odometer_New']==0].shape[0]

            product=preprocessing(mer_acc_data[col[8]])

            if(len(df_dict['Vehicle_Number'].split(','))>1):
                df_dict['Multi_Vehicle'] = 'Y'
            else:
                df_dict['Multi_Vehicle'] = 'N'



            if len(product.split(','))>1:
                df_dict['MultiProduct']='Y'
            else:
                df_dict['MultiProduct'] = 'N'
            df_dict['Product'] = product

            df_dict['Actual_Amount'] = mer_acc_data[col[13]].sum()

            df_dict['Actual_Volume'] = mer_acc_data[col[10]].sum()
            fuel_used, amount_spent, mileage, km_per_rs=    cal_mileage(mer_acc_data,acc)
            df_dict['km/rs']=km_per_rs
            df_dict['mileage'] = mileage
            df_dict['Month'] = month
            df_dict['Amount'] = amount_spent
            df_dict['Volume'] = fuel_used
            limit_exceed_and_reaidng(df_dict)
            copy_dict = df_dict.copy()
            print('dicitonary',copy_dict)

            df_list.append(copy_dict)
    print('list',df_list)
    return df_list


def merchant_account_analysis(mer):
    account=mer_data[col[4]].unique()
    mer_percentage=merchant_percentage(account)
    df_list1 = list()
    df_list2 = list()
    for acc in account:
        # print(acc)
        df_dict = {}
        df_dict['Merchant'] = mer
        mer_account_data = data[data[col[4]]==acc]
        vendor=list(set(mer_account_data[col[2]]))
        if len(vendor)>=2:
            df_dict['Multiple_Merchant']='Y'
            df_dict['Merchant_Name']=','.join(v for v in vendor)

            df_list2.extend(make_data(df_dict,mer_account_data,acc,mer_percentage))
        else:
            df_dict['Merchant_Name']=mer
            df_dict['Multiple_Merchant'] = 'N'
            li=make_data(df_dict, mer_account_data, acc, mer_percentage)
            df_list1.extend(li)

    return df_list1, df_list2


"""

def reading_category(df_dict):
    if df_dict>=80:
        category=1
    elif df_dict>=60 and df_dict<80:
        category=2
    elif df_dict>=40 and df_dict<60:
        category=3
    elif df_dict>=20 and df_dict<40:
        category=4
    else:
        category=5
    return category

def merchant_account_analysis(mer):
    df_dict = {}
    df_dict['Merchant_Name'] = []
    df_dict['Account_Number'] = []
    df_dict['Account_Percentage'] = []
    df_dict['Reading_Category'] = []
    df_dict['Merchant_Percentage']=[]
    percentage=reading_missed(mer_data['Odometer_New'])
    account = mer_data[col[4]].unique()
    for acc in account:
        df_dict['Merchant_Percentage'].append(percentage)
        mer_acc_data = mer_data[mer_data[col[4]] == acc]
        df_dict['Merchant_Name'].append(mer)
        df_dict['Account_Number'].append(acc)
        acc_percentage=reading_missed(mer_acc_data['Odometer_New'])
        df_dict['Account_Percentage'].append(acc_percentage)
        df_dict['Reading_Category'].append(reading_category(acc_percentage))
    return df_dict
"""
col=data.columns
data=data[data[col[5]].str.contains('UP',na=False)]
data=data.dropna(subset=[col[2]])
data["Odometer_New"]=abs(data["Odometer_New"])
data[col[6]] = pd.to_datetime(data[col[6]], format="%Y-%m-%d %H:%M")
merchant=data[col[2]].unique()
dataframe_list2=list()
for mer in tqdm.tqdm(merchant):
    mer_data = data[data[col[2]] == mer]
    df1,df2=merchant_account_analysis(mer)
    dataframe_list.extend(df1)
    dataframe_list2.extend(df2)

new_data=pd.DataFrame(dataframe_list)
new_data1=pd.DataFrame(dataframe_list2)
#new_data.to_csv('/home/stealth/Desktop/analysis/iocl_readings.csv')
frame=[new_data,new_data1]
new_data=pd.concat(frame)
new_data.to_csv('/home/stealth/Desktop/analysis/hpcl_mileage.csv')
