import os
import pprint

import feedparser
from feedgen.feed import FeedGenerator

from input import feedurl_list
from input import feed_info


def generate_feed(feed_info, entry_list):
    feed_generator = FeedGenerator()
    feed_generator.id(feed_info["id"])
    feed_generator.title(feed_info["title"])
    feed_generator.subtitle(feed_info["subtitle"])
    feed_generator.author(feed_info["author"])
    feed_generator.link(href=feed_info["href_self"], rel="self")
    feed_generator.language(feed_info["lang"])
    for item in entry_list:
        feed_entry = feed_generator.add_entry()
        feed_entry.id(item["id"])
        feed_entry.title(item["title"])
        feed_entry.link(href=item["link"])
        feed_entry.updated(item["updated"])
        if ("summary" in item):
            summary_type = "html" if "<" in item["summary"] else None
            feed_entry.summary(summary=item["summary"], type=summary_type)
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../target/{feed_info['filepath']}")
    out_normfile = os.path.normpath(out_file)
    os.makedirs(os.path.dirname(out_normfile), exist_ok=True)
    feed_generator.atom_file(out_normfile)

if __name__ == "__main__":
    # フィードURL一覧ファイルのフィード毎にエントリを取得して
    # エントリ一覧（フル）を作成する
    full_list = []
    feedurls = feedurl_list.feedurls
    for url in feedurls:
        data = feedparser.parse(url)
        for entry in data["entries"]:
            full_list.append(entry)
    full_list.sort(key=lambda item: item["updated_parsed"])

    # コンテンツ一覧（フル）を使ってまとめフィードを作成する
    generate_feed(feed_info.full_feed, full_list)

    # 更新分だけ含まれたフィードの作成
    last_data = feedparser.parse(feed_info.full_feed["href_self"])
    if last_data["entries"]:
        # コンテンツ一覧（フル）から前回まとめたフィードに
        # 含まれていないコンテンツのみを抽出する
        last_list = []
        for entry in last_data["entries"]:
            last_list.append(entry)
        full_list_ids = [d.get("id") for d in full_list]
        last_list_ids = [d.get("id") for d in last_list]
        new_list_ids = list(set(full_list_ids) - set(last_list_ids))
        new_list = [l for l in full_list if l["id"] in new_list_ids]
        new_list.sort(key=lambda item: item["updated_parsed"])

        # 更新分コンテンツを使って更新分だけ含まれたフィードを作成する
        generate_feed(feed_info.new_feed, new_list)
