import pandas as pd
import tqdm

data=pd.read_csv('/home/stealth/Desktop/analysis/whole_data_hpcl.csv',sep=',')
col=data.columns
data=data[data[col[5]].str.contains('UP',na=False)]
data=data.dropna(subset=[col[2]])
data["Odometer_New"]=abs(data["Odometer_New"])
data[col[6]] = pd.to_datetime(data[col[6]], format="%Y-%m-%d %H:%M")
account=data[col[4]].unique()
data['Field']='Correct'
print("Hello")
for acc in tqdm.tqdm(account):
    acc_data=data[data[col[4]]==acc]
    acc_data=acc_data.sort_values(col[6])
    odometer=acc_data['Odometer_New']
    indexes=odometer.index
    data['Field'][indexes[0]] = 'Correct'
    d1 = odometer[indexes[0]]
    for i in range(0,len(indexes)-1):
        d2=odometer[indexes[i+1]]

        if d2-d1 :
            data['Field'][indexes[i+1]]='Correct'
            d1=d2
        else:
            data['Field'][indexes[i + 1]] = 'Incorrect'
data.to_csv('/home/stealth/Desktop/analysis/total_data_hpcl.csv')