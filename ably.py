import os
import sys
import random
import string
import requests
import time
import json
from datetime import datetime, timedelta
import requests

class Ably:
    def __init__(self):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en,en-GB;q=0.9,en-US;q=0.8',
            'Cache-Control': 'no-cache',
            'Referer': 'https://app.ablybot.com/',
            'Sec-Ch-Ua': '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-platform':'"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent':'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.39 Mobile Safari/537.36 Telegram-Android/11.4.2 (Xiaomi MI 8 Lite; Android 10; SDK 29; AVERAGE)',
            'X-Requested-With': 'tw.nekomimi.nekogram'
        }
    
    def print_(self, word):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"[{now}] | {word}")

    def make_request(self, method, url, headers=None, json=None, data=None):
        retry_count = 0
        while True:
            time.sleep(2)
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, json=json)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json, data=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json)
            else:
                raise ValueError("Invalid method.")
            
            if response.status_code >= 500:
                if retry_count >= 4:
                    self.print_(f"Mã trang thái: {response.status_code} | {response.text}")
                    return None
                retry_count += 1
            elif response.status_code >= 400:
                self.print_(f"Mã trang thái: {response.status_code} | {response.text}")
                return None
            elif response.status_code >= 200:
                return response
    
    
    def get(self, query):
        url = 'https://app.ablybot.com/api/users/me?register=true'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }

        response = self.make_request('get', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                user = res.get('user',{})
                daily_points = user.get('daily_points')
                if daily_points == 0:
                    print()
                return user
    
    def checkin(self, query):
        url = 'https://app.ablybot.com/api/users/receive_sequential_reward'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('post', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                total_points = res.get('total_points',0)
                self.print_(f"Checkin xong, Tổng điểm : {total_points}")
    
    def generate_retro(self, query):
        url = 'https://app.ablybot.com/api/users/generate_retro_reward'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('get', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                self.receive_retro(query)
    
    def receive_retro(self, query):
        url = 'https://app.ablybot.com/api/users/receive_retro_reward'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('post', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                total_points = res.get('total_points', 0)
                self.print_(f"Nhận thưởng, tổng điểm: {total_points}")
    
    def list_task_daily(self, query):
        url = 'https://app.ablybot.com/api/tasks/list'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('get', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                specials = res.get('dailies', [])
                for items in specials:
                    id = items.get('id')
                    name = items.get('name')
                    reward = items.get('reward')
                    is_completed = items.get('is_completed',True)
                    if is_completed:
                        self.print_(f"Nhiệm vụ {name} Xong")
                    else:
                        payload = {'task_id': id}
                        self.complete_task(query, payload, name, reward)

                commons = res.get('commons', [])
                for items in commons:
                    id = items.get('id')
                    name = items.get('name')
                    reward = items.get('reward')
                    is_completed = items.get('is_completed',True)
                    if is_completed:
                        self.print_(f"Nhiệm vụ {name} Xong")
                    else:
                        payload = {'task_id': id}
                        self.complete_task(query, payload, name, reward)
                
                bonus_available = res.get('bonus_available', False)

                if bonus_available:
                    self.dailies_bonus(query)

                ads_total = res.get('ads_total',0)
                ads_seen = res.get('ads_seen',0)
                totals = ads_total - ads_seen
                if totals > 0:
                    self.print_(f" {totals} xem quảng cáo")
                    for i in range(totals):
                        payload = {'task_id': -6}
                        self.complete_task(query, payload, f"Xem quảng cáo {i+1}", 500)

    def list_task_partner(self, query):
        url = 'https://app.ablybot.com/api/partners/list'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('get', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                specials = res.get('specials', [])
                for items in specials:
                    id = items.get('id')
                    name = items.get('name')
                    reward = items.get('reward')
                    payload = {'partner_id': id}
                    self.visit_task(query, payload, name, reward)

                commons = res.get('commons', [])
                for items in commons:
                    id = items.get('id')
                    name = items.get('name')
                    reward = items.get('reward')
                    payload = {'partner_id': id}
                    self.visit_task(query, payload, name, reward)
                
                
    
    def complete_task(self, query, payload, name, reward):
        url ='https://app.ablybot.com/api/tasks/complete'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
            'Content-Length': str(len(payload))
        }

        response = self.make_request('post', url=url, headers=headers, json=payload)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                total_points = res.get('total_points', 0)
                self.print_(f"Nhiệm vụ {name} | Nhận {reward}, Tổng điểm : {total_points}")
    
    def visit_task(self, query, payload, name, reward):
        url = 'https://app.ablybot.com/api/partners/visit'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
            'Content-Length': str(len(payload))
        }

        response = self.make_request('post', url=url, headers=headers, json=payload)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                total_points = res.get('total_points', 0)
                self.print_(f"Nhiệm vụ {name} | Nhận {reward}, Tổng điểm : {total_points}")
                
    
    def wheel_data(self, query):
        url = 'https://app.ablybot.com/api/airdrop/wheel_data'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('get', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                spins = res.get('spins')
                if spins > 0:
                    self.print_(f"quay {spins} Spin")
                    for i in range(spins):
                        self.spin_wheel(query)
                else:
                    self.print_('không quay được Spin')
    
    def spin_wheel(self, query):
        url = 'https://app.ablybot.com/api/airdrop/spin_wheel'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('post', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                prize = res.get('prize', 0)
                type = prize.get('type')
                amount = prize.get('amount')
                self.print_(f"Nhận Spin : {type} {amount}")
    
    def dailies_bonus(self, query):
        url = 'https://app.ablybot.com/api/tasks/dailies_bonus'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {query}',
        }
        response = self.make_request('post', url=url, headers=headers)
        if response is not None:
            res = response.json()
            ok = res.get('ok', False)
            if ok:
                total_points = res.get('total_points', 0)
                self.print_(f"Phần thưởng hàng ngày, Tổng điểm : {total_points}")

        