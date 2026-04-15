#!/usr/bin/env python3
"""
微信文章阅读器
通过URL获取微信公众号文章的完整内容
"""

import requests
from bs4 import BeautifulSoup
import sys


def read_wechat_article(url):
    """
    读取微信文章内容

    Args:
        url (str): 微信文章链接，格式：https://mp.weixin.qq.com/s/xxxxxx

    Returns:
        dict: 包含文章标题、作者、发布时间、正文等信息的字典
    """
    try:
        # 设置请求头模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取文章标题
        title = soup.find('meta', property='og:title')
        if title:
            title = title.get('content', '')

        # 提取作者
        author_tag = soup.find('meta', property='og:article:author')
        if author_tag and author_tag.get('content'):
            author = author_tag.get('content', '')
        else:
            author_tag = soup.find('span', class_='rich_media_meta_text')
            author = author_tag.get_text(strip=True) if author_tag else ''

        # 提取发布时间
        publish_time = soup.find('meta', property='og:article:published_time')
        if publish_time:
            publish_time = publish_time.get('content', '')

        # 提取正文
        content_div = soup.find('div', class_='rich_media_content')
        if content_div:
            # 移除脚本和样式标签
            for tag in content_div(['script', 'style']):
                tag.decompose()

            # 提取文本内容，保留段落结构
            content_text = content_div.get_text(separator='\n\n', strip=True)
        else:
            content_text = ''

        # 提取文章描述（摘要）
        description = soup.find('meta', property='og:description')
        if description:
            description = description.get('content', '')

        return {
            'url': url,
            'title': title or '未知标题',
            'author': author or '未知作者',
            'publish_time': publish_time or '',
            'description': description or '',
            'content': content_text or '无法提取正文内容',
            'status': 'success'
        }

    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'error': f'网络请求失败: {str(e)}',
            'status': 'error'
        }
    except Exception as e:
        return {
            'url': url,
            'error': f'解析失败: {str(e)}',
            'status': 'error'
        }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 read_wechat_article.py <wechat_article_url>')
        print('Example: python3 read_wechat_article.py "https://mp.weixin.qq.com/s/NqAdWRwll9rB46anNjyskQ"')
        sys.exit(1)

    url = sys.argv[1]

    # 验证URL格式
    if 'mp.weixin.qq.com' not in url:
        print('错误：这不是微信文章链接')
        print('正确的格式应该是：https://mp.weixin.qq.com/s/xxxxxx')
        sys.exit(1)

    # 读取文章
    article = read_wechat_article(url)

    if article['status'] == 'success':
        print('=' * 80)
        print(f'标题：{article["title"]}')
        print(f'作者：{article["author"]}')
        if article['publish_time']:
            print(f'发布时间：{article["publish_time"]}')
        print('=' * 80)
        print()
        if article['description']:
            print('摘要：')
            print(article['description'])
            print()
        print('正文内容：')
        print(article['content'])
    else:
        print(f'错误：{article["error"]}')
        sys.exit(1)
