# 微信文章阅读器 (WeChat Article Reader)

读取微信公众号文章并灵活处理输出，支持提取完整内容、总结或提取关键信息。核心能力是能够获取文章的完整内容（标题、作者、发布时间、摘要、正文），并根据用户需求决定输出形式。

## 核心能力

- 能够提取和输出微信文章的完整内容（标题、作者、发布时间、摘要、正文）
- 保留所有原始信息（价格、数据、链接、细节），不做删改

## 快速开始

读取微信文章内容：

```bash
python3 scripts/read_wechat_article.py "https://mp.weixin.qq.com/s/xxxxxx"
```

脚本会输出文章的所有信息，后续可根据用户需求灵活处理。

## 依赖安装

在使用前，请确保安装了必要的 Python 依赖：

```bash
pip install requests beautifulsoup4
```

## 文件结构

- `SKILL.md` - 技能说明文档，包含详细的使用场景和输出策略
- `scripts/read_wechat_article.py` - 核心读取脚本，支持URL验证、内容提取、错误处理

