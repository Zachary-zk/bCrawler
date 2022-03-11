import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


def get_response(html_url, stream=False):
    headers = {
        "referer": "https://www.bilibili.com/video/BV1dS4y167y5?from=search&seid=4946859608231270468&spm_id_from=333.337.0.0",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }
    response = requests.get(html_url, headers=headers, stream=stream)
    return response


def get_url(html_url):
    r = get_response(html_url)
    a = re.search(r"window\.__INITIAL_STATE__=(.*?);", r.text).group(1)
    json_data = json.loads(a, strict=False)
    video_data = json_data['videoData']
    avid = str(video_data['aid'])
    qn = '112'
    urls = []

    for p in video_data['pages']:
        cid = str(p['cid'])
        title = p['part']
        if len(video_data['pages']) == 1:
            title = video_data['title']
        urls.append({
            'title': title,
            "url": "https://api.bilibili.com/x/player/playurl?cid=" + cid + "&avid=" + avid + "&an=" + qn + "&otype=json&fourk=1"
        })
    return urls


def save(video_url, video_size, title):
    video_res = get_response(video_url, True)
    with open(title + '.mp4', 'wb') as fd:
        print('开始下载文件：{}, 当前文件大小：{}KB'.format(title, video_size / 1024))
        for c in tqdm(iterable=video_res.iter_content(), total=video_size, unit='k', desc=None):
            fd.write(c)
        print('{},文件下载成功'.format(title))


def a_single_download(info):
    response = get_response(info['url'])
    json_data = json.loads(response.text)
    video_url = json_data['data']['durl'][0]['url']
    video_size = json_data['data']['durl'][0]['size']
    save(video_url, video_size, info['title'])


def concurrent_download(base_infos):
    executor = ThreadPoolExecutor(max_workers=10)
    futur_tasks = [executor.submit(a_single_download(), info) for info in base_infos]
    wait(futur_tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    html_url = "https://www.bilibili.com/video/BV1dS4y167y5?from=search&seid=4946859608231270468&spm_id_from=333.337.0.0"
    base_infos = get_url(html_url)
    a_single_download(base_infos[0])
