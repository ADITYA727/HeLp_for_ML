import requests
import math
import joblib


RESULTS_PER_PAGE = 30

categories = {
    # 'bollywood': (134273497, 7196, ['#bollywood']),
    # 'politics': (134313754, 7420, ['@narendramodi', '@amitshah']),
    # 'cricket': (134317730, 3591, ['#indiavssouthafrica', '#SAvsIND', '#indvsa', '#teamindia', '#indvssl', '#slvsind']),
    # 'bigg_boss': (134325682, 1101, ['bigg boss', 'bb11']),
    # 'football': (134329161, 14346, ['#fcbarcelona', '#liverpool', '#chelsea']),
    # 'machine_learning': (134333634, 20000, ['#machinelearning', '#bigdata']),
    # 'happy_birthday': (134341586, 10000, ['happy birthday']),
    # 'hollywood': (134348544, 10000, ['#hollywood']),
    # 'mobiles': (134354508, 10000, ['redmi note']),
    'food': (134359478, 1400, ['pasta', 'make']),
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': """_privy_484F964CDA79917FF5C60133=%7B%22uuid%22%3A%22f005a8e7-ebc8-4d99-b9a9-8c9b9bf1c4f1%22%7D; _privy_a=%7B%22referring_domain%22%3A%22www.google.co.in%22%2C%22referring_url%22%3A%22https%3A%2F%2Fwww.google.co.in%2F%22%2C%22utm_medium%22%3A%22search%22%2C%22utm_source%22%3A%22Google%22%2C%22search_term%22%3Anull%2C%22initial_url%22%3A%22https%3A%2F%2Fbrand24.com%2Fblog%2Fhow-to-count-the-number-of-tweets-for-a-specific-hashtag%2F%3Fadg%3DTwitter_monitoring_bs%26adgr%3Ddsa%26gclid%3DEAIaIQobChMI2sG3gL7_2QIVFiUrCh2UGgKDEAAYASAAEgK9MfD_BwE%22%2C%22sessions_count%22%3A1%2C%22pages_viewed%22%3A1%7D; _privy_b=%7B%22referring_domain%22%3A%22www.google.co.in%22%2C%22referring_url%22%3A%22https%3A%2F%2Fwww.google.co.in%2F%22%2C%22utm_medium%22%3A%22search%22%2C%22utm_source%22%3A%22Google%22%2C%22search_term%22%3Anull%2C%22initial_url%22%3A%22https%3A%2F%2Fbrand24.com%2Fblog%2Fhow-to-count-the-number-of-tweets-for-a-specific-hashtag%2F%3Fadg%3DTwitter_monitoring_bs%26adgr%3Ddsa%26gclid%3DEAIaIQobChMI2sG3gL7_2QIVFiUrCh2UGgKDEAAYASAAEgK9MfD_BwE%22%2C%22pages_viewed%22%3A1%7D; _hp2_ses_props.2979368351=%7B%22r%22%3A%22https%3A%2F%2Fwww.google.co.in%2F%22%2C%22ts%22%3A1521706385175%2C%22d%22%3A%22brand24.com%22%2C%22h%22%3A%22%2Fblog%2Fhow-to-count-the-number-of-tweets-for-a-specific-hashtag%2F%22%7D; __unam=7639673-1624cc4c0b5-5ea2a1be-1; _ga=GA1.2.1923893448.1521706387; _gid=GA1.2.1833056498.1521706387; _sp_ses.80ab=*; _ym_uid=1521706390708279118; _ym_isad=1; _ym_visorc_38352770=w; _snrs_sa=ssuid:8df8e365-901b-4826-902a-484002eadbd4&appear:1521706391&sessionVisits:2; _snrs_sb=ssuid:8df8e365-901b-4826-902a-484002eadbd4&leaves:1521706392; _snrs_p=host:brand24.com&permUuid:15340999-e4a4-4a24-ba54-8786e0d43ef4&uuid:15340999-e4a4-4a24-ba54-8786e0d43ef4&emailHash:&user_hash:&init:1521706391&last:1521706391&current:1521706391&uniqueVisits:1&allVisits:1; _snrs_uuid=15340999-e4a4-4a24-ba54-8786e0d43ef4; _snrs_puuid=15340999-e4a4-4a24-ba54-8786e0d43ef4; b24er=e3Ojc%2BWm0SGYcREEEOse3ftPKT7A9kjhLnZaFNTJ0zjHRASk6HwHlwo4ijyJ5O60o%2B6lsriuca1hydIF99oCFayn%2FUTZUtDuwB0zr5dps1UwQeAkJshowTYMM8odVDABY19a8chHXyXXEFMitbSxId28%2BjlNR2sQipw7Gt64ESMbHsNfwf7Gb8dL4I63ViIQ3inxP15NcZ9BXirYFLii1U1WY7LCXvEXQenywTgve1GYlecbO96zRE8gT11org0W; b24el=xfZpiiEP%2Ffsz6e7caobjmhImJFCGg5AiuZbq8%2BZUX84%3D; _ga=GA1.3.1923893448.1521706387; _gid=GA1.3.1833056498.1521706387; _gac_UA-109906-9=1.1521706387.EAIaIQobChMI2sG3gL7_2QIVFiUrCh2UGgKDEAAYASAAEgK9MfD_BwE; _snrs_uuid=15340999-e4a4-4a24-ba54-8786e0d43ef4; _snrs_puuid=15340999-e4a4-4a24-ba54-8786e0d43ef4; _hjIncludedInSample=1; _gac_UA-109906-9=1.1521706417.EAIaIQobChMI2sG3gL7_2QIVFiUrCh2UGgKDEAAYASAAEgK9MfD_BwE; fbm_469543809880617=base_domain=.brand24.com; fbsr_469543809880617=zC6z2hDwiPe5LSKj_jTTb0Rc1ZQQvzKX-uU301yxsMY.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUF6SGdna01Wb1hzSkN4cDBYUE55TjZDQTN0dGhQMnZSVDNoOW5mYkluRU5UcW9janF3SVNQMkc2a1dqQ0tVdzkxczY4M2NzSlFDVDFGdVdDSDZHNWV2ZHdLVE5NRGp0LUNiWFFINXh3c0ZrU3M1cEZWbms3RGJmQUUtRWxTTHlZM0VMTHZMQmJrOV9MRlM4S0kxMEhnWlM2RUdETDdsUmlDTmNyNEhGdzMxVm1wd2JWVklXaHZNazF3N0dWWjhfcUZ2TWtRWlBHRl9ranlaMmoyVHFBbkZ2LXNuMDZybW9xWGZkbXFGY2dxMi11ZjNJWERiZ1Z5TTZWTEVpaGVJNXoyRXJXQ0RUX1UybGlYRFpna1hjaUtxVGRqcDlnd2tieVJLRzB5STVVUkJ3U1NvVHRDei1WUVlOWWg2UDgxbkNqWERWNnlPRlZHMWhjUGtPeF94Y3poZyIsImlzc3VlZF9hdCI6MTUyMTcwNjQ3NiwidXNlcl9pZCI6IjE1MDk5ODg3MjM4ODY5NCJ9; PHPSESSID=6cpgo8e7i81dmjqhciml7otcs5; kemrcaw=b43b436867afc796858822c2da735700%2590373843; intercom-lou-7d95c7a1f40e65f71000a61e8f048680ca2bd6f2=1; projectHasJustAdded134271012=1; gtm-last-project-added=134273497; _hp2_id.2979368351=%7B%22userId%22%3A2871515272797622%2C%22pageviewId%22%3A%221309690933597156%22%2C%22sessionId%22%3A%225151023540104834%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%223.0%22%7D; _snrs_sa=ssuid:8df8e365-901b-4826-902a-484002eadbd4&appear:1521706391&sessionVisits:38; _snrs_sb=ssuid:8df8e365-901b-4826-902a-484002eadbd4&leaves:1521707117; _snrs_p=host:app.brand24.com&permUuid:15340999-e4a4-4a24-ba54-8786e0d43ef4&uuid:15340999-e4a4-4a24-ba54-8786e0d43ef4&emailHash:&user_hash:&init:1521706391&last:1521706391&current:1521707115&uniqueVisits:1&allVisits:19; intercom-session-7d95c7a1f40e65f71000a61e8f048680ca2bd6f2=b1lwQmhldE0wUHpsWmVCTzViT3U1akUwWnZESDNSam1RcHlmTUU4OGpLK05UUlNJSkt5anhuQzRLcElRdkc0Uy0td3BhVnhHZktUMmZZNnJGdXFnc3ZnUT09--b3805ba3961471af96789276433218d50e4116d6; _sp_id.80ab=ef5e9ef1-3ca9-42bb-8e06-68eb6dde8af5.1521706390.1.1521707234.1521706390.c7559916-b36c-4d4f-bd89-0297f14ed500""",
    'Host': 'app.brand24.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
}

for category, category_details in categories.items():
    sid = category_details[0]
    count = category_details[1]

    url = 'https://app.brand24.com/panel/results-search2/sid/%s' % (sid,)
    pages = math.ceil(count/RESULTS_PER_PAGE)

    tweets = []
    for page in range(1, pages+1):
        print(page)

        post_data = {
            'd1': '2010-05-31',
            'd2': '2018-03-22',
            'dr': '7',
            'va': '1',
            'cdt': 'days',
            'or': '0',
            'p': str(page),
            'sc': '0'
        }

        try:
            r = requests.post(url, headers=headers, data=post_data)
            tweets += r.json()['results']
        except Exception as e:
            print(e)

    joblib.dump(tweets, '%s_tweets.pkl' % (category,))

