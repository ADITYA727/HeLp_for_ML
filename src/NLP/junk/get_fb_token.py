import requests

USERNAME = "ganapatel@outlook.com"
PASSWORD = "gana@#$%"


fields = {
	"access_token" : "237759909591655|0f140aabedfb65ac27a739ed1a2263b1",
	"email" : USERNAME,
	"format": "json",
	"generate_session_cookies" : "1",
	"locale" : "en_US",
	"machine_id" : "GwcYUPj__peN15gJSxiPZwa5",
	"password" : PASSWORD,
	"sdk" : "ios",
	"sdk_version" : "2"
}

head = {'user-agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 6_1_6 like Mac OS X)\
							\AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B500\
							[FBAN/MessengerForiOS;FBAV/6.1.0.33.5;FBBV/2955837;FBDV/iPod4,1;\
							FBMD/iPod touch;FBSN/iPhone OS;FBSV/6.1.6;FBSS/2; \
							FBCR/;FBID/phone;FBLC/en_US;FBOP/5]'}

r = requests.post("https://b-api.facebook.com/method/auth.login", data = fields, headers = head)
access_token = r.json()['access_token']

print(access_token)
