import requests
import json

# QiitaのAPIから最新記事を取得（例）
RSS_URL = "https://qiita.com/api/v2/items?page=1&per_page=5"
# 手順1でコピーしたURLをここに入れるか、GitHubの環境変数を使います
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1466637779793481961/NcoA4KwIivbv3jFW5xXZxdgX6N7dOZqF0DhwLmkQFo3ww7lvdR5vzkml7e8sZ_w0joG8"

def main():
    response = requests.get(RSS_URL)
    articles = response.json()
    
    content = "🚀 **最新のIT記事（過去6時間）**\n\n"
    for article in articles:
        content += f"- [{article['title']}]({article['url']})\n"

    payload = {"content": content}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    main()
