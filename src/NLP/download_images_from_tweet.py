"""
todo: use grequests instead of requests
"""


import requests
import os, sys
import mimetypes
import tqdm
from urllib.parse import urlparse
from os.path import splitext

home = os.path.abspath(os.path.dirname(__file__))
sys.path.append(home + '/../../')
from src.mysql_utils import MySqlUtils


sql = MySqlUtils('Twitter')
image_path = '/home/analytics/data_partition/images/images'

image_ext = ['.ani', '.bmp', '.cal', '.fax', '.gif', '.img', '.jbg', '.jpe', '.jpeg', '.jpg', '.mac', '.pbm', '.pcd',
             '.pcx', '.pct', '.pgm', '.png', '.ppm', '.psd', '.ras', '.tga', '.tiff', '.wmf']


final_query = '"india" "nicobar" "north and middle andaman" "south andaman" "anantapur" "chittoor" "east godavari" "guntur" "krishna" "kurnool" "prakasam" "srikakulam" "sri potti sriramulu nellore" "visakhapatnam" "vizianagaram" "west godavari" "ysr district, kadapa  cuddapah" "anjaw" "changlang" "dibang valley" "east kameng" "east siang" "kra daadi" "kurung kumey" "lohit" "longding" "lower dibang valley" "lower siang" "lower subansiri" "namsai" "papum pare" "siang" "tawang" "tirap" "upper siang" "upper subansiri" "west kameng" "west siang" "baksa" "barpeta" "biswanath" "bongaigaon" "cachar" "charaideo" "chirang" "darrang" "dhemaji" "dhubri" "dibrugarh" "dima hasao  north cachar hills" "goalpara" "golaghat" "hailakandi" "hojai" "jorhat" "kamrup" "kamrup metropolitan" "karbi anglong" "karimganj" "kokrajhar" "lakhimpur" "majuli" "morigaon" "nagaon" "nalbari" "sivasagar" "sonitpur" "south salamara-mankachar" "tinsukia" "udalguri" "west karbi anglong" "araria" "arwal" "aurangabad" "banka" "begusarai" "bhagalpur" "bhojpur" "buxar" "darbhanga" "east champaran  motihari" "gaya" "gopalganj" "jamui" "jehanabad" "kaimur  bhabua" "katihar" "khagaria" "kishanganj" "lakhisarai" "madhepura" "madhubani" "munger  monghyr" "muzaffarpur" "nalanda" "nawada" "patna" "purnia  purnea" "rohtas" "saharsa" "samastipur" "saran" "sheikhpura" "sheohar" "sitamarhi" "siwan" "supaul" "vaishali" "west champaran" "chandigarh" "balod" "baloda bazar" "balrampur" "bastar" "bemetara" "bijapur" "bilaspur" "dantewada  south bastar" "dhamtari" "durg" "gariyaband" "janjgir-champa" "jashpur" "kabirdham  kawardha" "kanker  north bastar" "kondagaon" "korba" "korea  koriya" "mahasamund" "mungeli" "narayanpur" "raigarh" "raipur" "rajnandgaon" "sukma" "surajpur  " "surguja" "dadra & nagar haveli" "daman" "diu" "central delhi" "east delhi" "new delhi" "north delhi" "north east  delhi" "north west  delhi" "shahdara" "south delhi" "south east delhi" "south west  delhi" "west delhi" "north goa" "south goa" "ahmedabad" "amreli" "anand" "aravalli" "banaskantha  palanpur" "bharuch" "bhavnagar" "botad" "chhota udepur" "dahod" "dangs  ahwa" "devbhoomi dwarka" "gandhinagar" "gir somnath" "jamnagar" "junagadh" "kachchh" "kheda  nadiad" "mahisagar" "mehsana" "morbi" "narmada  rajpipla" "navsari" "panchmahal  godhra" "patan" "porbandar" "rajkot" "sabarkantha  himmatnagar" "surat" "surendranagar" "tapi  vyara" "vadodara" "valsad" "ambala" "bhiwani" "charkhi dadri" "faridabad" "fatehabad" "gurgaon" "hisar" "jhajjar" "jind" "kaithal" "karnal" "kurukshetra" "mahendragarh" "mewat" "palwal" "panchkula" "panipat" "rewari" "rohtak" "sirsa" "sonipat" "yamunanagar" "bilaspur" "chamba" "hamirpur" "kangra" "kinnaur" "kullu" "lahaul & spiti" "mandi" "shimla" "sirmaur  sirmour" "solan" "una" "anantnag" "bandipore" "baramulla" "budgam" "doda" "ganderbal" "jammu" "kargil" "kathua" "kishtwar" "kulgam" "kupwara" "leh" "poonch" "pulwama" "rajouri" "ramban" "reasi" "samba" "shopian" "srinagar" "udhampur" "bokaro" "chatra" "deoghar" "dhanbad" "dumka" "east singhbhum" "garhwa" "giridih" "godda" "gumla" "hazaribag" "jamtara" "khunti" "koderma" "latehar" "lohardaga" "pakur" "palamu" "ramgarh" "ranchi" "sahibganj" "seraikela-kharsawan" "simdega" "west singhbhum" "bagalkot" "ballari  bellary" "belagavi  belgaum" "bengaluru  bangalore rural" "bengaluru  bangalore urban" "bidar" "chamarajanagar" "chikballapur" "chikkamagaluru  chikmagalur" "chitradurga" "dakshina kannada" "davangere" "dharwad" "gadag" "hassan" "haveri" "kalaburagi  gulbarga" "kodagu" "kolar" "koppal" "mandya" "mysuru  mysore" "raichur" "ramanagara" "shivamogga  shimoga" "tumakuru  tumkur" "udupi" "uttara kannada  karwar" "vijayapura  bijapur" "yadgir" "alappuzha" "ernakulam" "idukki" "kannur" "kasaragod" "kollam" "kottayam" "kozhikode" "malappuram" "palakkad" "pathanamthitta" "thiruvananthapuram" "thrissur" "wayanad" "lakshadweep" "agar malwa" "alirajpur" "anuppur" "ashoknagar" "balaghat" "barwani" "betul" "bhind" "bhopal" "burhanpur" "chhatarpur" "chhindwara" "damoh" "datia" "dewas" "dhar" "dindori" "guna" "gwalior" "harda" "hoshangabad" "indore" "jabalpur" "jhabua" "katni" "khandwa" "khargone" "mandla" "mandsaur" "morena" "narsinghpur" "neemuch" "panna" "raisen" "rajgarh" "ratlam" "rewa" "sagar" "satna" "sehore" "seoni" "shahdol" "shajapur" "sheopur" "shivpuri" "sidhi" "singrauli" "tikamgarh" "ujjain" "umaria" "vidisha" "ahmednagar" "akola" "amravati" "aurangabad" "beed" "bhandara" "buldhana" "chandrapur" "dhule" "gadchiroli" "gondia" "hingoli" "jalgaon" "jalna" "kolhapur" "latur" "mumbai city" "mumbai suburban" "nagpur" "nanded" "nandurbar" "nashik" "osmanabad" "palghar" "parbhani" "pune" "raigad" "ratnagiri" "sangli" "satara" "sindhudurg" "solapur" "thane" "wardha" "washim" "yavatmal" "bishnupur" "chandel" "churachandpur" "imphal east" "imphal west" "jiribam" "kakching" "kamjong" "kangpokpi" "noney" "pherzawl" "senapati" "tamenglong" "tengnoupal" "thoubal" "ukhrul" "east garo hills" "east jaintia hills" "east khasi hills" "north garo hills" "ri bhoi" "south garo hills" "south west garo hills " "south west khasi hills" "west garo hills" "west jaintia hills" "west khasi hills" "aizawl" "champhai" "kolasib" "lawngtlai" "lunglei" "mamit" "saiha" "serchhip" "dimapur" "kiphire" "kohima" "longleng" "mokokchung" "mon" "peren" "phek" "tuensang" "wokha" "zunheboto" "angul" "balangir" "balasore" "bargarh" "bhadrak" "boudh" "cuttack" "deogarh" "dhenkanal" "gajapati" "ganjam" "jagatsinghapur" "jajpur" "jharsuguda" "kalahandi" "kandhamal" "kendrapara" "kendujhar  keonjhar" "khordha" "koraput" "malkangiri" "mayurbhanj" "nabarangpur" "nayagarh" "nuapada" "puri" "rayagada" "sambalpur" "sonepur" "sundargarh" "karaikal" "mahe" "pondicherry" "yanam" "amritsar" "barnala" "bathinda" "faridkot" "fatehgarh sahib" "fazilka" "ferozepur" "gurdaspur" "hoshiarpur" "jalandhar" "kapurthala" "ludhiana" "mansa" "moga" "muktsar" "nawanshahr  shahid bhagat singh nagar" "pathankot" "patiala" "rupnagar" "sahibzada ajit singh nagar  mohali" "sangrur" "tarn taran" "ajmer" "alwar" "banswara" "baran" "barmer" "bharatpur" "bhilwara" "bikaner" "bundi" "chittorgarh" "churu" "dausa" "dholpur" "dungarpur" "hanumangarh" "jaipur" "jaisalmer" "jalore" "jhalawar" "jhunjhunu" "jodhpur" "karauli" "kota" "nagaur" "pali" "pratapgarh" "rajsamand" "sawai madhopur" "sikar" "sirohi" "sri ganganagar" "tonk" "udaipur" "east sikkim" "north sikkim" "south sikkim" "west sikkim" "ariyalur" "chennai" "coimbatore" "cuddalore" "dharmapuri" "dindigul" "erode" "kanchipuram" "kanyakumari" "karur" "krishnagiri" "madurai" "nagapattinam" "namakkal" "nilgiris" "perambalur" "pudukkottai" "ramanathapuram" "salem" "sivaganga" "thanjavur" "theni" "thoothukudi  tuticorin" "tiruchirappalli" "tirunelveli" "tiruppur" "tiruvallur" "tiruvannamalai" "tiruvarur" "vellore" "viluppuram" "virudhunagar" "adilabad" "bhadradri kothagudem" "hyderabad" "jagtial" "jangaon" "jayashankar bhoopalpally" "jogulamba gadwal" "kamareddy" "karimnagar" "khammam" "komaram bheem asifabad" "mahabubabad" "mahabubnagar" "mancherial" "medak" "medchal" "nagarkurnool" "nalgonda" "nirmal" "nizamabad" "peddapalli" "rajanna sircilla" "rangareddy" "sangareddy" "siddipet" "suryapet" "vikarabad" "wanaparthy" "warangal  rural" "warangal  urban" "yadadri bhuvanagiri" "dhalai" "gomati" "khowai" "north tripura" "sepahijala" "south tripura" "unakoti" "west tripura" "almora" "bageshwar" "chamoli" "champawat" "dehradun" "haridwar" "nainital" "pauri garhwal" "pithoragarh" "rudraprayag" "tehri garhwal" "udham singh nagar" "uttarkashi" "agra" "aligarh" "allahabad" "ambedkar nagar" "amethi  chatrapati sahuji mahraj nagar" "amroha  j.p. nagar" "auraiya" "azamgarh" "baghpat" "bahraich" "ballia" "balrampur" "banda" "barabanki" "bareilly" "basti" "bhadohi" "bijnor" "budaun" "bulandshahr" "chandauli" "chitrakoot" "deoria" "etah" "etawah" "faizabad" "farrukhabad" "fatehpur" "firozabad" "gautam buddha nagar" "ghaziabad" "ghazipur" "gonda" "gorakhpur" "hamirpur" "hapur  panchsheel nagar" "hardoi" "hathras" "jalaun" "jaunpur" "jhansi" "kannauj" "kanpur dehat" "kanpur nagar" "kanshiram nagar  kasganj" "kaushambi" "kushinagar  padrauna" "lakhimpur - kheri" "lalitpur" "lucknow" "maharajganj" "mahoba" "mainpuri" "mathura" "mau" "meerut" "mirzapur" "moradabad" "muzaffarnagar" "pilibhit" "pratapgarh" "raebareli" "rampur" "saharanpur" "sambhal  bhim nagar" "sant kabir nagar" "shahjahanpur" "shamali  prabuddh nagar" "shravasti" "siddharth nagar" "sitapur" "sonbhadra" "sultanpur" "unnao" "varanasi" "alipurduar" "bankura" "birbhum" "burdwan  bardhaman" "cooch behar" "dakshin dinajpur  south dinajpur" "darjeeling" "hooghly" "howrah" "jalpaiguri" "kalimpong" "kolkata" "malda" "murshidabad" "nadia" "north 24 parganas" "paschim medinipur  west medinipur" "purba medinipur  east medinipur" "purulia" "south 24 parganas" "uttar dinajpur  north dinajpur" "andaman and nicobar island  ut" "andhra pradesh" "arunachal pradesh" "assam" "bihar" "chandigarh  ut" "chhattisgarh" "dadra and nagar haveli  ut" "daman and diu  ut" "delhi  nct" "goa" "gujarat" "haryana" "himachal pradesh" "jammu and kashmir" "jharkhand" "karnataka" "kerala" "lakshadweep  ut" "madhya pradesh" "maharashtra" "manipur" "meghalaya" "mizoram" "nagaland" "odisha" "puducherry  ut" "punjab" "rajasthan" "sikkim" "tamil nadu" "telangana" "tripura" "uttarakhand" "uttar pradesh" "west bengal"'
user_query = """SELECT queue.user_handle FROM
                  queue JOIN user
                  ON queue.user_handle = user.user_handle
                  WHERE
                  queue.tweet_status=1 AND user.lang='en' AND
                  user.total_tweet_count > 25 AND queue.query_id=1 AND
                      MATCH (user.location, user.time_zone, user.description) AGAINST ('{}');""".format(final_query)

users = sql.get_data(user_query)
users_list = [user['user_handle'] for user in users]
print('Query count {}'.format(len(users)))
image_query=' and urls_contained LIKE "%{}"'.format(image_ext[0])
for img in image_ext[1:]:
    image_query= image_query + " or urls_contained LIKE '%{}'".format(img)
query = 'SELECT tweet_id, urls_contained FROM Twitter.tweet where  user_handle IN (' + ','.join(
    ("'{}'".format(user) for user in users_list)) + ")" + image_query + "and image_path = NULL"

# query="SELECT  tweet_id, urls_congettained FROM tweet WHERE urls_contained LIKE '%.jpg%';"


# to find the image extension ans getting the reponse
def get_response_and_extension(u):
    response = requests.get(u)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    #parsed = urlparse(u)
    #root, ext = splitext(parsed.path)
    #print(ext,extension)
    return response, extension


def download_image(response, filename_path, extension):
    url_check = [True for ext in image_ext if ext in extension]

    if url_check:
        filename_path=filename_path+extension
        try:
            f = open(filename_path, 'wb')
            f.write(response.content)
            f.close()
        except Exception as e:
            print(e)
            return False
        return True
    else:
        return False


def get_image_and_query(url):
    url_split = url['urls_contained'].split(',')
    filename_path = image_path + str(url['tweet_id'])
    query_image=''
    for u in url_split:
        print(u)
        try:
            response, extension = get_response_and_extension(u)
        except Exception as e:
            print(e)
            query_not_image = 'UPDATE tweet SET image_path = "{}" WHERE tweet_id={};'.format('', url['tweet_id'])
            continue
        if (response and extension and download_image(response, filename_path, extension)):
            query_image = 'UPDATE tweet SET image_path = "{}" WHERE tweet_id={};'.format(
                str(url['tweet_id']) + extension, url['tweet_id'])
            print(str(url['tweet_id']) + extension)
        else:
            query_not_image = 'UPDATE tweet SET image_path = "{}" WHERE tweet_id={};'.format('', url['tweet_id'])
    if query_image:
        return query_image
    else :
        return query_not_image




def main(query):
    data = sql.get_data(query)
    print("no. of tweet id ", len(data))
    for url in tqdm.tqdm(data):
        if not url['urls_contained']:
            query_for_update = 'UPDATE tweet SET image_path = "{}" WHERE tweet_id={};'.format('', url['tweet_id'])
        else:
            query_for_update = get_image_and_query(url)
        sql.cursor.execute(query_for_update)


main(query)
