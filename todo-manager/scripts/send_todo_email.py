#!/usr/bin/env python3
"""
待办事项邮件发送脚本
通过 SMTP 发送待办清单邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json


def load_todos():
    """加载待办事项"""
    with open('/workspace/projects/workspace/todo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('todos', [])


def generate_email_content():
    """生成邮件内容"""
    todos = load_todos()

    pending = [t for t in todos if not t.get('completed', False)]
    completed = [t for t in todos if t.get('completed', False)]

    content = f"""待办事项清单
生成时间：{datetime.now().strftime('%Y年%m月%d日 %A %H:%M')}

📊 总览
- ✅ 已完成：{len(completed)} 项
- ⏳ 未完成：{len(pending)} 项

---

🔥 高优先级
"""

    # 按优先级分组
    high_priority = [t for t in pending if t.get('priority') == 'high']
    medium_priority = [t for t in pending if t.get('priority') == 'medium']
    low_priority = [t for t in pending if t.get('priority') == 'low']

    for i, todo in enumerate(high_priority, 1):
        content += f"{i}. {todo.get('content')}\n"

    content += f"\n📌 中优先级\n"
    for i, todo in enumerate(medium_priority, 1):
        content += f"{i}. {todo.get('content')}\n"

    content += f"\n📝 低优先级\n"
    for i, todo in enumerate(low_priority, 1):
        content += f"{i}. {todo.get('content')}\n"

    content += f"\n✅ 已完成任务\n"
    for i, todo in enumerate(completed, 1):
        content += f"{i}. {todo.get('content')}\n"

    content += "\n---\n\n虾兵1号为您整理 🦐"

    return content


def send_email(smtp_server, smtp_port, username, password,
               from_email, to_email, use_tls=True):
    """
    发送邮件

    Args:
        smtp_server: SMTP 服务器地址（如 smtp.gmail.com）
        smtp_port: SMTP 端口（如 587）
        username: 邮箱用户名
        password: 邮箱密码或应用专用密码
        from_email: 发件人邮箱
        to_email: 收件人邮箱
        use_tls: 是否使用 TLS
    """
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"待办事项清单 - {datetime.now().strftime('%Y年%m月%d日')}"

    # 添加邮件正文
    body = generate_email_content()
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 发送邮件
    try:
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        server.login(username, password)
        server.send_message(msg)
        server.quit()

        print("✓ 邮件发送成功！")
        return True

    except Exception as e:
        print(f"✗ 邮件发送失败: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("待办事项邮件发送工具")
    print("=" * 50)
    print("\n需要配置以下 SMTP 信息：")
    print("1. SMTP 服务器地址（如 smtp.gmail.com）")
    print("2. SMTP 端口（如 587）")
    print("3. 邮箱用户名（通常是邮箱地址）")
    print("4. 邮箱密码或应用专用密码")
    print("5. 发件人邮箱")
    print("6. 收件人邮箱")
    print("\n注意：如果使用 Gmail，需要启用应用专用密码")
    print("      https://support.google.com/accounts/answer/185833")
    print("=" * 50)
