import os

data='/home/stealthuser/Perosnal/Sentimental/Patel_Reservation/'
f=open(data+'with_geo.txt')
lines=f.readlines()

# python Exporter.py --querysearch "#Patelagitation" -- near "22.25,71.19" --since 2015-05-01 --until 2017-08-15

# s="python Exporter.py --querysearch"
# s1="-- near \"22.25,71.19\""
# s2="--since 2015-05-01 --until 2017-08-15"

# for line in lines:
# 	line=line.strip('\n')
# 	print s+" "+"\""+line+"\""+" "+s1+" "+s2

folders= data+'with_geo/'
fols=os.listdir(folders)
i=0
for fol in fols:
	
	os.rename(folders+fol,folders+lines[i].strip('\n'))
	i+=1 