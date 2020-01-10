"""
remove outliers

"""
import pandas as pd

"""
Index(['S.No.', ' Terminal ID', ' Merchant', 'BatchID/ROC', ' Account Number',
       ' Vehicle Number', 'Transaction Date', 'Transaction Type', 'Product',
       'Price', 'Volume(Ltr.)', 'Currency', 'Service Charge', 'Amount(Rs.)',
       'CCMS/Cash Balance(Rs.)', 'Odometer Reading', 'Drivestars',
       'RewardType', 'Cheque No', 'MICR Code', 'Status', 'Odometer_New',
       'Corrected', 'Month'],
      dtype='object')

"""



hpcl=pd.read_csv('/home/stealth/Desktop/analysis/whole_data.csv',sep=',')

import csv
vehicle_filter = hpcl[' Vehicle Number'].str.startswith('UP32')
hpcl = hpcl[vehicle_filter]

hpcl = hpcl.sort_values('Transaction Date')

vehicles = hpcl[' Vehicle Number'].unique()

vehicles_mileage = {}

for vehicle in vehicles:
    vehicle_df = hpcl[hpcl[' Vehicle Number'] == vehicle]
    odometer_readings = vehicle_df['Odometer_New']
    tmp_df = vehicle_df[(vehicle_df['Odometer_New'] != '-') & (vehicle_df['correct_status'] == 'Correct')]
    try:
        first_index = tmp_df['Odometer_New'].index[0]
    except IndexError:
        continue

    last_index = tmp_df['Odometer_New'].index[-1]

    vehicle_df = vehicle_df.loc[first_index:last_index, :]

    odometer_readings = vehicle_df['Odometer_New']
    odometer_diff = float(odometer_readings.iloc[-1]) - float(odometer_readings.iloc[0])
    fuel_used = sum(map(float, vehicle_df['Volume(Ltr.)'][:-1]))
    amount_spent = sum(map(float, vehicle_df['Amount(Rs.)'][:-1]))
    try:
        mileage = round(odometer_diff / fuel_used, 2)
    except ZeroDivisionError:
        continue
    km_per_rs = round(odometer_diff / amount_spent, 2)
    vehicles_mileage[vehicle] = (mileage, km_per_rs)

with open('vehicles_hpcl_details.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Vehicle', 'Mileage', 'km/rs'])
    for k, v in vehicles_mileage.items():
        writer.writerow([k, v[0], v[1]])


