import requests
import json
import os  # これを追加
from datetime import datetime, timedelta, timezone

# 直接URLを書かずに、環境変数から読み込む
# "DISCORD_WEBHOOK" はGitHubのSecretsで設定した名前と一致させます
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")


def _parse_qiita_datetime(dt_str: str) -> datetime:
    # Qiitaは例: "2024-01-01T12:34:56+09:00" / "...Z" の形式
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def fetch_popular_qiita_items(within_hours: int = 6, top_n: int = 5):
    """Qiitaの直近within_hours時間の投稿を、人気順でtop_n件返す。"""
    api_url = "https://qiita.com/api/v2/items"
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=within_hours)

    # 直近分を取りこぼさないよう、少し多めに取得してからローカルで絞り込み
    params = {
        "page": 1,
        "per_page": 100,
    }
    response = requests.get(api_url, params=params, timeout=20)
    response.raise_for_status()
    items = response.json()

    recent_items = []
    for item in items:
        created_at = item.get("created_at")
        if not created_at:
            continue
        try:
            created_dt = _parse_qiita_datetime(created_at)
        except ValueError:
            continue
        if created_dt >= cutoff:
            recent_items.append(item)

    def sort_key(item):
        # Qiitaの人気指標として stocks_count を優先、次に likes_count
        return (
            int(item.get("stocks_count", 0)),
            int(item.get("likes_count", 0)),
            int(item.get("comments_count", 0)),
        )

    recent_items.sort(key=sort_key, reverse=True)
    return recent_items[:top_n]

def main():
    # URLが取得できていない場合のチェック
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK is not set.")
        return

    within_hours = 6
    top_n = 5

    try:
        articles = fetch_popular_qiita_items(within_hours=within_hours, top_n=top_n)
    except requests.RequestException as e:
        print(f"Error: failed to fetch Qiita items: {e}")
        return

    if not articles:
        print("Info: no recent articles found in the last hours.")
        return

    content = f"🚀 **人気のIT記事（過去{within_hours}時間 / Qiita）**\n\n"
    for article in articles:
        title = article.get("title", "(no title)")
        url = article.get("url", "")
        stocks = int(article.get("stocks_count", 0))
        likes = int(article.get("likes_count", 0))
        content += f"- 📌{stocks} ⭐{likes} [{title}]({url})\n"

    payload = {"content": content}
    try:
        post_resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=20)
        post_resp.raise_for_status()
        print(f"Posted {len(articles)} articles to Discord.")
    except requests.RequestException as e:
        print(f"Error: failed to post to Discord: {e}")

if __name__ == "__main__":
    main()
