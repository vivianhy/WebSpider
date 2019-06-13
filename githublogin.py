import requests
from pyquery import PyQuery as pq

class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/login',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Host': 'github.com'
        }
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.logined_url = 'https://github.com/settings/profile'
        self.session = requests.Session()
    
    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        if response.status_code == 200:
            doc = pq(response.text)
            token = doc('input:nth-child(2)').attr('value')
            return token
        else:
            print('{} {}'.format(self.login_url,response.status_code))
    
    def login(self, username, password):
        post_data = {
            'commit': 'Sign+in',
            'utf8': '✓',
            'authenticity_token': self.token(),
            'login': username,
            'password': password,
            'webauthn-support': 'supported'
        }
        response1 = self.session.post(self.post_url, data=post_data, headers=self.headers)
        if response1.status_code == 200:      
            response2 = self.session.get(self.logined_url, headers=self.headers)
            if response2.status_code == 200:
                self.profile(response2.text)
            else:
                print('{} {}'.format(self.logined_url,response2.status_code))
        else:
            print('{} {}'.format(self.post_url,response1.status_code))
    
    def profile(self, html):
        doc = pq(html)
        email = doc('#user_profile_email option:nth-child(2)').text()
        company = doc('#user_profile_company').attr('value')
        print(email, company)


if __name__ == "__main__":
    login = Login()
    login.login(username='vivianhy', password='password')