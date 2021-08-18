from requests import *
from json import dumps, loads
from bs4 import BeautifulSoup
import os
import math


class CodemaoApi(): 
    def __init__(self, UA='Mozilla/5.0 (Windows NT 10.0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36', debug=False):
        # New: api sets
        self.apis = {'home': 'https://shequ.codemao.cn',
                     'matomoApi': 'https://matomo.codemao.cn/piwik.js',
                     'login': 'https://api.codemao.cn/tiger/v3/web/accounts/login',
                     'logout': 'https://api.codemao.cn/tiger/v3/web/accounts/logout',
                     'cookie': 'https://shequ.codemao.cn/user/',
                     'getSelfInfo1': 'https://api.codemao.cn/web/users/details',
                     'getSelfInfo2': 'https://api.codemao.cn/api/user/info',
                     'getUserInfo': 'https://api.codemao.cn/api/user/info/detail/{}',
                     'changeSelfInfo': 'https://api.codemao.cn/tiger/v3/web/accounts/info',
                     'postArticle': 'https://api.codemao.cn/web/forums/boards/{}/posts',
                     'deleteArticle': 'https://api.codemao.cn/web/forums/posts/{}',
                     'postReply': 'https://api.codemao.cn/web/forums/posts/{}/replies',
                     'deleteReply': 'https://api.codemao.cn/web/forums/replies/{}',
                     'postL2Reply': 'https://api.codemao.cn/web/forums/replies/{}/comments',
                     'deleteL2Reply': 'https://api.codemao.cn/web/forums/comments/{}',
                     'clearWork': 'https://api.codemao.cn/tiger/work/user/works/permanently',
                     'requireWorkshop': 'https://api.codemao.cn/web/discussions/{}/comment',
                     'topReply': 'https://api.codemao.cn/web/forums/replies/{}/top',
                     'untopReply': 'https://api.codemao.cn/web/forums/replies/{}/top',
                     'likeReply': 'https://api.codemao.cn/web/forums/comments/{}/liked?source=REPLY',
                     'unlikeReply': 'https://api.codemao.cn/web/forums/comments/{}/liked?source=REPLY',
                     'searchArticle': 'https://api.codemao.cn/web/forums/posts/search?title={}&limit=30&page={}',
                     'likeWork': 'https://api.codemao.cn/nemo/v2/works/{}/like',
                     'unlikeWork': 'https://api.codemao.cn/nemo/v2/works/{}/like',
                     'getArticleInfo': 'https://api.codemao.cn/web/forums/posts/{}/details'}
        self.debug = debug
        # Use abs path to create in the root path, not cwd
        self.logpath = os.path.split(__file__)[0] + os.sep + 'runtime.log'
        self.ses = session()
        self.headers = {"Content-Type": "application/json", "User-Agent": UA}
        self.log('Successfully create the main session')
    
    def log(self, *msg):
        if self.debug:
            print(*msg)
        # New: temp log file in the root dir
        if not os.path.exists(self.logpath):
            open(self.logpath, 'w', encoding='utf-8').close()
        with open(self.logpath, 'a', encoding='utf-8') as log:
            msg = [str(i) for i in msg]
            text = ' '.join(msg) + '\n' # list -> str
            log.write(text)

    def login(self, identity='', password=''):
        if identity and password:
            # Get PID
            self.log('getting pid...')
            text = get(self.apis['home'], headers = self.headers).text
            soup = BeautifulSoup(text, 'html.parser')
            json = soup.find('script').string.split("=")[1]
            pid = loads(json)['pid']
            self.log('Successfully get pid; pid:' + pid)
            # Log-in
            self.log('logging in...')
            res = self.ses.post(self.apis['login'], headers=self.headers, data=dumps({"identity": identity, "password": password, "pid": pid}))
            if res.status_code == 200:
                self.log("Successfully login to codemao.cn")
            else:
                self.log('End of logging in to codemao.cn; response', res.status_code)
        else:
            res = self.ses.get(self.apis['cookie'], headers=self.headers)
            if res.status_code == 200:
                self.log("Successfully login to codemao.cn")
            else:
                self.log('End of logging with cookie; response', res.status_code)
        return res.json()

    def logout(self):
        self.log('logging out...')
        res = self.ses.options(self.apis['logout'], headers=self.headers)
        if res.status_code == 204:
            self.log('Successfully log-out from codemao.cn')
        else:
            self.log('End of logout from codemao.cn; response', res.status_code)
        return res.json()

    def getSelfInfo(self):
        self.log('getting...')
        res1 = self.ses.get(self.apis['getSelfInfo1'], headers=self.headers)
        res2 = self.ses.get(self.apis['getSelfInfo2'], headers=self.headers)
        if res1.status_code == 200 and res2.status_code == 200:
            self.log('Successfully get self info')
        else:
            self.log('End of requiring; response', res1.status_code, res2.status_code)
        return dict(res1.json(), **res2.json())

    def getUserInfo(self, urid):
        self.log('getting...')
        res = self.ses.get(self.apis['getUserInfo'].format(urid), headers=self.headers)
        if res.status_code == 200:
            self.log('Successfully get info.')
        else:
            self.log('End of requiring; response', res.status_code)
        return res.json()

    def changeSelfInfo(self, info):
        self.log('changing...')
        res = self.ses.patch(self.apis['changeSelfInfo'].format(urid), headers=self.headers, data=dumps(info))
        if res.status_code == 200:
            self.log('Successfully change info.')
        else:
            self.log('End of requiring; response', res.status_code)
        return res.json()

    def postArticle(self, board, title, content):
        self.log('posting...')
        res = self.ses.post(self.apis['postArticle'].format(board), headers=self.headers, data=dumps({'title': title, 'content': content}))
        if res.status_code == 201:
            self.log("Successfully post article")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def deleteArticle(self, arid):
        self.log('posting...')
        res = self.ses.delete(self.apis['deleteArticle'].format(arid), headers=self.headers)
        if res.status_code == 201:
            self.log("Successfully delete article")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def postReply(self, arid, content):
        self.log('posting...')
        res = self.ses.post(self.apis['postReply'].format(arid), headers=self.headers, data=dumps({'content': content}))
        if res.status_code == 201:
            self.log("Successfully post reply")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def deleteReply(self, cmid):
        self.log('posting...')
        res = self.ses.delete(self.apis['deleteReply'].format(cmid), headers=self.headers)
        if res.status_code == 201:
            self.log("Successfully delete reply")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def postL2Reply(self, arid, cmid, content):
        self.log('posting...')
        res = self.ses.post(self.apis['postL2Reply'].format(arid), headers=self.headers, data=dumps({"parent_id":cmid, "content": content}))
        if res.status_code == 201:
            self.log("Successfully post reply")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def deleteL2Reply(self, cmid):
        self.log('posting...')
        res = self.ses.delete(self.apis['deleteL2Reply'].format(cmid), headers=self.headers)
        if res.status_code == 201:
            self.log("Successfully delete reply")
        else:
            self.log('End of posting; response', res.status_code)
        return res.json()

    def clearWork(self):
        self.log('clearing...')
        res = self.ses.delete(self.apis['clearWork'], headers=self.headers, data=dumps({'title': title, 'content': content}))
        if res.status_code == 200:
            self.log("Successfully send request to workshop")
        else:
            self.log('End of requiring; response', res.status_code)
        return res.json()

    def requireWorkshop(self, wsid, content):
        self.log('requiring...')
        res = self.ses.post(self.apis['requireWorkshop'].format(wsid), headers=self.headers, data=dumps({'content': content, 'rich_content': content, 'source': 'WORK_SHOP'}))
        if res.status_code == 200:
            self.log("Successfully send request to workshop")
        else:
            self.log('End of requiring; response', res.status_code)
        return res.json()

    def topReply(self, rpid):
        self.log('Setting...')
        res = self.ses.put(self.apis['topReply'].format(rpid), headers=self.headers, data=r'{}')
        if res.status_code == 204:
            self.log("Successfully set top reply")
        else:
            self.log('End of requiring; response', res.status_code)

    def untopReply(self, rpid):
        self.log('Setting...')
        res = self.ses.delete(self.apis['untopReply'].format(rpid), headers=self.headers)
        if res.status_code == 204:
            self.log("Successfully cancel top reply")
        else:
            self.log('End of requiring; response', res.status_code)

    def likeReply(self, rpid):
        self.log('Setting...')
        res = self.ses.put(self.apis['likeReply'].format(rpid), headers=self.headers, data=r'{}')
        if res.status_code == 204:
            self.log("Successfully set liked reply")
        else:
            self.log('End of setting; response', res.status_code)

    def unlikeReply(self, rpid):
        self.log('Setting...')
        res = self.ses.put(self.apis['unlikeReply'].format(rpid), headers=self.headers)
        if res.status_code == 204:
            self.log("Successfully cancel liked reply")
        else:
            self.log('End of setting; response', res.status_code)
    
    def searchArticle(self, key, to=20):
        self.log('searching...')
        page = 1
        res = [] 
        state = True
        while state:
            resp = self.ses.get(self.apis['searchArticle'].format(key, page), headers=self.headers).json()
            if not resp['items']:
                break
            for info in resp['items']:
                if to and len(res) >= to:
                    state = False
                    break
                res.append({'user': {'userid': info['user']['id'], 'username': info['user']['nickname']},'id': info['id'],'title': info['title']})
            page += 1
        return res

    def likeWork(self, wkid):
        self.log('setting...')
        res = self.ses.post(self.apis['likeWork'].format(wkid), headers=self.headers, data=r'{}')
        if res.status_code == 204:
            self.log('Successfully set liked work')
        else:
            self.log('End of setting; response', res.status_code)
        return res.json()

    def unlikeWork(self, wkid):
        self.log('setting...')
        res = self.ses.delete(self.apis['unlikeWork'].format(wkid), headers=self.headers)
        if res.status_code == 204:
            self.log('Successfully cancel liked work')
        else:
            self.log('End of setting; response', res.status_code)
        return res.json()

    def getArticleInfo(self, arid):
        self.log('getting...')
        res = self.ses.get(self.apis['getArticleInfo'].format(arid), headers=self.headers)
        if res.status_code == 200:
            self.log('Successfully get info.')
        else:
            self.log('End of requiring; response', res.status_code)
        return res.json()
