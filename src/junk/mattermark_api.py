import requests
import mattermark
import json
from itertools import cycle

# full_contact_key = "2Hd8vn8mZGv9iMTTmmkFrsn5E6CUczLk"

api_key_iter = cycle(["6d52db409273c3c9418588f5e967191284339d58b66720b0eb5fd617d299448f",
                     "9339aab1050d4778a80c56a3acb6e46da1392f02545f195438b1b38a742aade9",
                     "fc8a6d20ed6108624122de12afe85edbeda07d4c1d825c0f2a8b2c65b799c7c5",
                     "f67e0c6b36b4246120955b1af851cc92a254e93b9a80b70adb2f132aac7f7017",
                     "281e3ede5535e9d562b4fec043dd0ec9a72eee811100e228174a3c5331958a9e",
                     "b45e1972cf0a767cc1c670af67c96156b0cc73ea3d6af007dd7669a5a69a2eb1",
                      "8ce930c42cc0b15cef1039c8686706386b6ff19660b92e8e8a12fcddb87e667a",
                      "9929e5fe61dcd5dddc7e764db7e51992a997e7ef483e714dda274690afc45017",
                      "8bbb7de8fbf635547122578cca9a8a955957e255b4eb356cc6191b5607fb5de1"
])



filename = '/home/shubhamjain/Desktop/devel/stealth/data/harvard_mattermark.json'


while True:
    try:
        api_key = next(api_key_iter)
        mm = mattermark.mattermark(api_key)
        print(mm)
        mm_companyname = mm.companyBussinessNamebyName("harvard university")
        mmID = mm_companyname['companies'][0]["id"]
        print(mmID)
    except Exception as e:
        print(api_key)
        continue
    break



key_people = mm.companyPersonnel(mmID)
print(key_people)
f = open(filename, 'r')
flag = 0
name_list = []
text = f.readline()
while text:
    name_list.append(json.loads(text)['name'])
    text = f.readline()
f.close()

f = open(filename, 'a')

for count, person in enumerate(key_people):
    try:
        print(count)
        if person['name'] not in name_list:
            contact_url = "https://api.mattermark.com/companies/10579506/contact"

            # data we'll be sending to the contact endpoint
            payload = {
                "key": api_key,
                "full_name": person['name']
            }

            # mattermark call
            response = requests.get(contact_url, params=payload)
            response.raise_for_status()
            person['email'] = response.json()['email']
            print("{} {}".format(api_key, person))
            f.write('{}\n'.format(json.dumps(person)))
    except Exception as e:
        api_key = next(api_key_iter)
        print(e)

