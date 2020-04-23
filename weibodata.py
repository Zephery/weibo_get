#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{
    "statuses": [
        {
            "created_at": "Tue May 31 17:46:55 +0800 2011",
            "id": 11488058246,
            "text": "求关注。"，
            "source": "<a href="http://weibo.com" rel="nofollow">新浪微博</a>",
            "favorited": false,
            "truncated": false,
            "in_reply_to_status_id": "",
            "in_reply_to_user_id": "",
            "in_reply_to_screen_name": "",
            "geo": null,
            "mid": "5612814510546515491",
            "reposts_count": 8,
            "comments_count": 9,
            "annotations": [],
            "user": {       #个人信息
                "id": 1404376560,
                "screen_name": "zaku",
                "name": "zaku",
                "province": "11",
                "city": "5",
                "location": "北京 朝阳区",
                "description": "人生五十年，乃如梦如幻；有生斯有死，壮士复何憾。",   //个性签名
                "url": "http://blog.sina.com.cn/zaku",
                "profile_image_url": "http://tp1.sinaimg.cn/1404376560/50/0/1",
                "domain": "zaku",
                "gender": "m",
                "followers_count": 1204,
                "friends_count": 447,
                "statuses_count": 2908,
                "favourites_count": 0,
                "created_at": "Fri Aug 28 00:00:00 +0800 2009",
                "following": false,
                "allow_all_act_msg": false,
                "remark": "",
                "geo_enabled": true,
                "verified": false,
                "allow_all_comment": true,
                "avatar_large": "http://tp1.sinaimg.cn/1404376560/180/0/1",
                "verified_reason": "",
                "follow_me": false,
                "online_status": 0,
                "bi_followers_count": 215
            }
        },
        ..
    ],
    "previous_cursor": 0,
    "next_cursor": 11488013766,
    "total_number": 81655
}
"""
import json
import time
import httplib
import urllib
import pymysql
from weibo import Client

connection = pymysql.connect(host="123.206.28.24", user="root", passwd="helloroot", db="myblog", port=3306,
                             charset="utf8")
cur = connection.cursor()
APP_KEY = '415390189'  # 申请微博应用的时候这几个都有
APP_SECRET = '958ea2c93dcad4ab45a99098b44b016a'
REDIRECT_URI = 'https://api.weibo.com/oauth2/authorize'
client = Client(APP_KEY, APP_SECRET, REDIRECT_URI)
url = client.authorize_url
'https://api.weibo.com/oauth2/authorize?client_id=415390189&response_type=code&redirect_uri=958ea2c93dcad4ab45a99098b44b016a'


class AppClient:
    def __init__(self):
        self._appKey = APP_KEY  # 微博应用app key
        self._appSecret = APP_SECRET  # 微博应用app secret
        self._callbackUrl = REDIRECT_URI  # 回调地址
        self._account = ''  # 微博账号
        self._password = ''  # 微博密码
        self.AppCli = client
        self._author_url = self.AppCli.authorize_url
        self.getAuthorization()

    def insert(self, user_id, name, location, url, text, created_at):
        try:
            if len(text) > 1000:
                return
            insert_sql = """insert into myblog.weibo(uid,`name`,location,url,text,created_at) VALUES (%s,%s,%s,%s,%s,%s)"""
            cur.execute(insert_sql, (user_id, name, location, url, text, created_at))
            connection.commit()
        except Exception as e:
            print e

    def get_code(self):  # 使用该函数避免了手动输入code，实现了模拟用户授权后获得code的功能
        conn = httplib.HTTPSConnection('api.weibo.com')
        postdict = {"client_id": self._appKey,
                    "redirect_uri": self._callbackUrl,
                    "userId": self._account,
                    "passwd": self._password,
                    "isLoginSina": "0",
                    "action": "submit",
                    "response_type": "code",
                    }
        postdata = urllib.urlencode(postdict)
        conn.request('POST', '/oauth2/authorize', postdata,
                     {'Referer': self._author_url,
                      'Content-Type': 'application/x-www-form-urlencoded',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                      'cookie': 'TC-Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; SCF=Aj1FsXK_kNUbcu9Ur8SSjAx1OsUWzKnakWwY55bHpytWOTIsH9auZhceKRGVy3u13gRMMXrBWEgoCikENu61kZo.; SUB=_2A250nDCDDeRhGedH6VcS8CjMyzyIHXVX6CVLrDV8PUNbmtBeLXikkW8ZQKUOT53OmRY1PK13my6oOADJ6g..; un=w1570631036@sina.com; TC-V5-G0=28bf4f11899208be3dc10225cf7ad3c6; TC-Page-G0=1ac1bd7677fc7b61611a0c3a9b6aa0b4; wvr=6; wb_cusLike_1925306000=N; _s_tentry=-; UOR=,www.weibo.com,spr_sinamkt_buy_hyww_weibo_p137; Apache=8571371761746.116.1503155261406; SINAGLOBAL=8571371761746.116.1503155261406; ULV=1503155261449:1:1:1:8571371761746.116.1503155261406:'})
        res = conn.getresponse()
        location = res.getheader('location')
        code = location.split('=')[1]
        conn.close()
        return code

    def getAuthorization(self):  # 将上面函数获得的code再发送给新浪认证服务器，返回给客户端access_token和expires_in，有了这两个东西，咱就可以调用api了
        code = self.get_code()
        self.AppCli.set_code(code)
        uuid = self.AppCli.uid
        count_temp = 1
        while (True):
            json_str = client.get('statuses/public_timeline', uid=uuid, separators=(',', ':'), count=200)
            time.sleep(5)
            count_temp = count_temp + 1
            if count_temp > 2:
                break
            d = json.dumps(json_str)
            s = json.loads(d)
            length = len(s['statuses'])
            for i in range(0, length):
                data = s['statuses'][i]
                print data['text']
                self.insert(data['id'], data['user']['name'], data['user']['location'], data['user']['url'],
                            data['text'], data['created_at'])


if __name__ == '__main__':
    app = AppClient()
