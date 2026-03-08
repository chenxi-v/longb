#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 尝试不同编码
encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
content = None

for encoding in encodings:
    try:
        with open('spiders/python/wawa_app.py', 'r', encoding=encoding) as f:
            content = f.read()
        print(f'Successfully read file with {encoding} encoding')
        break
    except:
        continue

if content is None:
    print('Failed to read file with any encoding')
    exit(1)

# 修复被截断的代码
old_code = "v['vod_play_from'] = '$"

new_code = """v['vod_play_from'] = '$
.join(v['vod_play_from'])
        v['vod_play_url'] = '$
.join(v['vod_play_url'])
        vod.update(v)
        vod.pop('vod_play_list', None)
        vod.pop('type', None)
        return {'list': [vod]}

    def search_content(self, key, quick):
        data = self.fetch(f"{self.host}/api.php/zjv6.vod?page=1&limit=20&wd={key}", headers=self.getheader()).json()
        return {'list': data['data']['list'], 'page': '1'}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('spiders/python/wawa_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('File fixed successfully!')
else:
    print('Pattern not found in file')
    # 打印第99行附近的内容
    lines = content.split('\n')
    for i in range(max(0, 95), min(len(lines), 105)):
        print(f'{i+1}: {lines[i]}')
