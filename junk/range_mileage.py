import pandas as pd

data=pd.read_csv('/home/stealth/Desktop/analysis/iocl_mileage.csv')

data['range_mileage']=0

for i in range(0,data.shape[0]):
    if data['mileage'][i]==0:
        data['range_mileage'][i]=0
    elif data['mileage'][i]>0 and data['mileage'][i]<10:
        data['range_mileage'][i]=1
    elif data['mileage'][i]>10 and data['mileage'][i]<20:
        data['range_mileage'][i]=2
    elif data['mileage'][i]>20 and data['mileage'][i]<30:
        data['range_mileage'][i]=3
    elif data['mileage'][i]>30 and data['mileage'][i]<40:
        data['range_mileage'][i]=4
    elif data['mileage'][i]>40 and data['mileage'][i]<50:
        data['range_mileage'][i]=5
    elif data['mileage'][i]>50 and data['mileage'][i]<60:
        data['range_mileage'][i]=6
    elif data['mileage'][i]>60 and data['mileage'][i]<70:
        data['range_mileage'][i]=7
    elif data['mileage'][i]>70 and data['mileage'][i]<80:
        data['range_mileage'][i]=8
    elif data['mileage'][i]>80 and data['mileage'][i]<90:
        data['range_mileage'][i]=9
    elif data['mileage'][i]>90 and data['mileage'][i]<100:
        data['range_mileage'][i]=10
    elif data['mileage'][i]>100 :
        data['range_mileage'][i]=11

data['range_mileage'].to_csv('/home/stealth/Desktop/analysis/range_iocl_excel.csv')


