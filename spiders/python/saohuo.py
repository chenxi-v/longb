# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
from urllib.parse import urlparse
import base64
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        # 直接使用备用域名，避免初始化超时
        self.host = "https://shdy2.com"
        self.headers.update({'referer': f'{self.host}/'})
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="130", "Google Chrome";v="130"',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    def homeContent(self, filter):
        data=self.getpq()
        result = {}
        classes = []
        
        # 字母筛选（通用）
        letter_values = [{'n': '全部', 'v': ''}]
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            letter_values.append({'n': letter, 'v': letter})
        
        # 每个分类的类型筛选器
        type_filters = {
            '1': {  # 电影
                'key': 'type',
                'name': '类型',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '喜剧', 'v': '6'},
                    {'n': '爱情', 'v': '7'},
                    {'n': '恐怖', 'v': '8'},
                    {'n': '动作', 'v': '9'},
                    {'n': '科幻', 'v': '10'},
                    {'n': '战争', 'v': '11'},
                    {'n': '犯罪', 'v': '12'},
                    {'n': '动画', 'v': '13'},
                    {'n': '奇幻', 'v': '14'},
                    {'n': '剧情', 'v': '15'},
                    {'n': '冒险', 'v': '16'},
                    {'n': '悬疑', 'v': '17'},
                    {'n': '惊悚', 'v': '18'},
                    {'n': '其它', 'v': '19'},
                ]
            },
            '2': {  # 剧集
                'key': 'type',
                'name': '类型',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '大陆剧', 'v': '20'},
                    {'n': '港剧', 'v': '21'},
                    {'n': '韩剧', 'v': '22'},
                    {'n': '美剧', 'v': '23'},
                    {'n': '日剧', 'v': '24'},
                    {'n': '英剧', 'v': '25'},
                    {'n': '台剧', 'v': '26'},
                    {'n': '其它', 'v': '27'},
                ]
            },
        }
        
        filters = {}
        
        for k in data('.top_bar.clearfix a').items():
            j = k.attr('href')
            if j and 'list' in j:
                id = re.search(r'\d+', j).group(0)
                classes.append({
                    'type_name': k.text(),
                    'type_id': id
                })
                
                # 为每个分类添加筛选器（数组格式）
                cat_filters = [
                    type_filters.get(id, {'key': 'type', 'name': '类型', 'value': [{'n': '全部', 'v': ''}]}),
                    {'key': 'letter', 'name': '字母', 'value': letter_values}
                ]
                filters[id] = cat_filters
        
        result['class'] = classes
        result['filters'] = filters
        result['list'] = self.getlist(data('.grid_box ul li'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        # 获取筛选参数
        type_filter = extend.get('type', '') if extend else ''
        letter = extend.get('letter', '') if extend else ''
        
        # 构建URL，应用筛选
        # 基本格式: /list/{tid}-{pg}.html
        # 带类型筛选: /list/{type}-{pg}.html
        # 带字母筛选: 需要根据网站实际格式调整
        
        if type_filter:
            # 使用类型ID作为分类ID
            url = f"/list/{type_filter}-{pg}.html"
        else:
            url = f"/list/{tid}-{pg}.html"
        
        # 如果有字母筛选，需要根据网站实际URL格式调整
        # 这里假设网站支持字母筛选，如果不支持则忽略
        # if letter:
        #     url = url.replace('.html', f'-{letter}.html')
        
        data=self.getpq(url)
        
        # 提取页数信息（格式：1/10）
        page_text = data('.page span').text() or ''
        pagecount = 9999
        if '/' in page_text:
            try:
                pagecount = int(page_text.split('/')[1])
            except:
                pass
        
        result = {}
        result['list'] = self.getlist(data('.grid_box ul li'))
        result['page'] = pg
        result['pagecount'] = pagecount
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data=self.getpq(ids[0])
        
        # 从meta标签提取信息
        keywords = data('meta[name="keywords"]').attr('content') or ''
        description = data('meta[name="description"]').attr('content') or ''
        
        # 提取视频名称（从 h1.v_title a 标签）
        vod_name = data('h1.v_title a').text() or ''
        if not vod_name:
            # 备用方案：从keywords的第一个关键词
            vod_name = keywords.split(',')[0] if keywords else ''
        
        # 提取简介（优先从#info_more .p_txt获取完整内容）
        vod_content = ''
        p_txt = data('#info_more .p_txt').html() or ''
        if p_txt:
            # 在<br/>之前截取剧情内容
            if '<br/>' in p_txt:
                p_txt = p_txt.split('<br/>')[0]
            # 移除HTML标签，只保留文本
            p_txt = re.sub(r'<[^>]+>', '', p_txt)
            # 移除开头的"剧情：</b>"或类似内容
            p_txt = re.sub(r'^剧情：?\s*', '', p_txt.strip())
            vod_content = p_txt.strip()
        
        # 备用方案：从description中提取
        if not vod_content and description:
            if '剧情:' in description:
                vod_content = description.split('剧情:')[1].strip()
            else:
                vod_content = description
        
        # 从 p 标签提取地区、年份、导演、主演等信息
        # 使用clone()去除a标签后再获取文本，避免"剧情介绍"链接被包含
        info_p = data('h1.v_title').next('p').clone()
        info_p('a').remove()
        info_text = info_p.text() or ''
        vod_area = ''
        vod_year = ''
        vod_director = ''
        vod_actor = ''
        
        if info_text:
            # 解析格式：大陆 / 2026 / 动作,犯罪 / 导演:周靖 / 主演:邹兆龙,于荣光.../
            # 移除末尾可能的斜杠
            info_text = info_text.rstrip('/').strip()
            parts = info_text.split('/')
            for part in parts:
                part = part.strip()
                if not vod_area and part in ['大陆', '香港', '台湾', '美国', '韩国', '日本', '英国', '法国', '德国', '印度', '泰国']:
                    vod_area = part
                elif not vod_year and part.isdigit() and len(part) == 4:
                    vod_year = part
                elif '导演:' in part:
                    vod_director = part.replace('导演:', '').strip()
                elif '主演:' in part:
                    vod_actor = part.replace('主演:', '').strip()
        
        # 提取封面图片（优先从m_background的style中提取）
        vod_pic = ''
        bg_style = data('.m_background').attr('style') or ''
        if 'url(' in bg_style:
            # 提取url()中的图片地址
            match = re.search(r'url\(([^)]+)\)', bg_style)
            if match:
                vod_pic = match.group(1).replace('&amp;', '&')
        
        # 备用方案：从img标签获取
        if not vod_pic:
            vod_pic = data('.v_info_box img').attr('data-original') or data('.v_info_box img').attr('src') or data('.grid_box img').attr('data-original') or ''
        
        # 提取备注信息（去除a标签，避免"剧情介绍"链接被包含）
        remarks_p = data('.grid_box.v_info_box p').clone()
        remarks_p('a').remove()
        vod_remarks = remarks_p.text().rstrip('/').strip()
        
        vod = {
            'vod_id': ids[0],
            'vod_name': vod_name,
            'vod_pic': vod_pic,
            'vod_remarks': vod_remarks,
            'vod_content': vod_content,
            'vod_actor': vod_actor,
            'vod_director': vod_director,
            'vod_year': vod_year,
            'vod_area': vod_area,
        }
        
        n=list(data('.play_from ul li').items())
        p=list(data('ul.play_list li').items())
        ns,ps=[],[]
        
        print(f"找到 {len(n)} 条线路，{len(p)} 个播放列表")
        
        for i,j in enumerate(n):
            ns.append(j.text())
            # 拼接完整的播放链接
            episode_links = []
            for k in list(p[i]('a').items())[::-1]:
                href = k.attr('href')
                # 如果是相对路径，拼接完整的 host
                if href and not href.startswith('http'):
                    href = f"{self.host}{href}"
                episode_links.append(f"{k.text()}${href}")
            ps.append('#'.join(episode_links))
            print(f"线路 {i}: {j.text()}，共 {len(episode_links)} 集")
        
        vod['vod_play_from']='$$'.join(ns)
        vod['vod_play_url']='$$'.join(ps)
        print(f"vod_play_from: {vod['vod_play_from']}")
        print(f"vod_play_url: {vod['vod_play_url'][:100]}...")
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        url = f'{self.host}/s----------.html'
        resp = self.post(url, data={'wd': key}, headers=self.headers)
        data = pq(resp.text)
        result = {}
        result['list'] = self.getlist(data('.grid_box ul li'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def playerContent(self, flag, id, vipFlags):
        print(f"playerContent 调用: flag={flag}, id={id}")
        
        # 判断 id 是否是完整 URL
        if id.startswith('http://') or id.startswith('https://'):
            # 如果是完整 URL，直接使用
            data_text = self.fetch(id, headers=self.headers).text
            data = pq(data_text)
        else:
            # 如果是相对路径，使用 getpq
            data = self.getpq(id)
        
        try:
            surl=data('section[style*="padding-top"] iframe').eq(0).attr('src')
            print(f"提取到的 iframe src: {surl}")
            
            if not surl:
                raise Exception("未找到 iframe src")
            
            # 直接返回 iframe src，让前端使用 iframe 播放
            url = surl
            p = 1  # iframe 播放
        except Exception as e:
            print(f"失败: {e}")
            url,p=f'{self.host}{id}',1
        
        print(f"最终返回: url={url}, parse={p}")
        
        phd={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="130", "Google Chrome";v="130"',
            'sec-fetch-dest': 'video',
            'referer': f'{self.host}/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        return  {'parse': p, 'url': url, 'header': phd}

    def localProxy(self, param):
        pass

    def liveContent(self, url):
        pass

    def gethost(self):
        try:
            data=pq(self.fetch("http://shapp.us",headers=self.headers, timeout=10).text)
            for i in data('.content-top ul li').items():
                h=i('a').attr('href')
                if h:
                    try:
                        data = self.fetch(h, headers=self.headers, timeout=10)
                        if data.status_code == 200:
                            return h
                    except Exception as e:
                        print(f"域名 {h} 访问失败: {e}")
                        continue
        except Exception as e:
            print(f"获取域名列表失败: {e}")
        
        # 如果所有域名都无法访问，返回备用域名
        return "https://shdy2.com"

    def extract_values(self, text):
        url_match = re.search(r'var url = "([^"]+)"', text)
        url = url_match.group(1) if url_match else None
        t_match = re.search(r'var t = "([^"]+)"', text)
        t = t_match.group(1) if t_match else None
        key_match = re.search(r'var key = hhh\("([^"]+)"\)', text)
        key_param = key_match.group(1) if key_match else None
        act_match = re.search(r'var act = "([^"]+)"', text)
        act = act_match.group(1) if act_match else None
        play_match = re.search(r'var play = "([^"]+)"', text)
        play = play_match.group(1) if play_match else None
        return {
            "url": url,
            "t": t,
            "key": key_param,
            "act": act,
            "play": play
        }

    def getlist(self,data):
        videos = []
        for i in data.items():
            videos.append({
                'vod_id': i('a').attr('href'),
                'vod_name': i('a').attr('title'),
                'vod_pic': i('a img').attr('data-original'),
                'vod_remarks': i('.v_note').text()
            })
        return videos

    def getpq(self, path=''):
        data=self.fetch(f"{self.host}{path}",headers=self.headers).text
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))

    def hhh(self, t):
        ee = {
            "0Oo0o0O0": "a", "1O0bO001": "b", "2OoCcO2": "c", "3O0dO0O3": "d",
            "4OoEeO4": "e", "5O0fO0O5": "f", "6OoGgO6": "g", "7O0hO0O7": "h",
            "8OoIiO8": "i", "9O0jO0O9": "j", "0OoKkO0": "k", "1O0lO0O1": "l",
            "2OoMmO2": "m", "3O0nO0O3": "n", "4OoOoO4": "o", "5O0pO0O5": "p",
            "6OoQqO6": "q", "7O0rO0O7": "r", "8OoSsO8": "s", "9O0tO0O9": "t",
            "0OoUuO0": "u", "1O0vO0O1": "v", "2OoWwO2": "w", "3O0xO0O3": "x",
            "4OoYyO4": "y", "5O0zO0O5": "z", "0OoAAO0": "A", "1O0BBO1": "B",
            "2OoCCO2": "C", "3O0DDO3": "D", "4OoEEO4": "E", "5O0FFO5": "F",
            "6OoGGO6": "G", "7O0HHO7": "H", "8OoIIO8": "I", "9O0JJO9": "J",
            "0OoKKO0": "K", "1O0LLO1": "L", "2OoMMO2": "M", "3O0NNO3": "N",
            "4OoOOO4": "O", "5O0PPO5": "P", "6OoQQO6": "Q", "7O0RRO7": "R",
            "8OoSSO8": "S", "9O0TTO9": "T", "0OoUO0": "U", "1O0VVO1": "V",
            "2OoWWO2": "W", "3O0XXO3": "X", "4OoYYO4": "Y", "5O0ZZO5": "Z"
        }
        n = ""
        o = base64.b64decode(t).decode('utf-8', errors='replace')
        i = 0
        while i < len(o):
            l = o[i]
            found = False
            for key, value in ee.items():
                if o[i:i + len(key)] == key:
                    l = value
                    i += len(key) - 1
                    found = True
                    break
            if not found:
                pass
            n += l
            i += 1
        return n
