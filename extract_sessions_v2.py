#!/usr/bin/env python3
import re
import json
from bs4 import BeautifulSoup
import requests

def extract_sessions_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ミニステージのセクションを見つける
    ministage_section = soup.find('div', {'id': 'ministage'})
    if not ministage_section:
        print("ミニステージセクションが見つかりません")
        return {}
    
    sessions_data = {}
    
    # 各ステージのアコーディオンを探す
    stage_buttons = ministage_section.find_all('button', class_='collapsible_agenda')
    
    for button in stage_buttons:
        stage_name = button.find('span', class_='title_agenda').text.strip()
        print(f"処理中のステージ: {stage_name}")
        
        # 対象のステージのみ処理
        if stage_name not in ['AWS Village Stage', 'Developers on Live', 'Community Stage']:
            continue
            
        sessions_data[stage_name] = {'Day 1': [], 'Day 2': []}
        
        # このステージのコンテンツを取得
        content_div = button.find_next_sibling('div', class_='contenttable')
        if not content_div:
            continue
            
        # Day 1とDay 2のテーブルを探す
        current_day = None
        for element in content_div.find_all(['h2', 'table']):
            if element.name == 'h2':
                if 'Day 1' in element.text:
                    current_day = 'Day 1'
                elif 'Day 2' in element.text:
                    current_day = 'Day 2'
            elif element.name == 'table' and current_day:
                # テーブルの行を処理
                rows = element.find_all('tr')
                for row in rows[1:]:  # ヘッダー行をスキップ
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        time_cell = cells[0].text.strip()
                        content_cell = cells[1]
                        
                        # セッションタイトルを抽出
                        title_span = content_cell.find('span', style=lambda x: x and 'font-weight: bold' in x)
                        if title_span:
                            title = title_span.text.strip()
                            
                            # HTMLの内容を解析
                            # 構造: <span>タイトル</span><br /><br />概要<br /><br />発表者
                            cell_html = str(content_cell)
                            
                            # <br /><br />で分割
                            parts = re.split(r'<br\s*/?\s*>\s*<br\s*/?\s*>', cell_html, flags=re.IGNORECASE)
                            
                            description = ""
                            speaker = ""
                            
                            if len(parts) >= 3:
                                # parts[0]: タイトル部分
                                # parts[1]: 概要部分
                                # parts[2]: 発表者部分
                                
                                # 概要を抽出
                                desc_soup = BeautifulSoup(parts[1], 'html.parser')
                                description = desc_soup.get_text().strip()
                                
                                # 発表者を抽出
                                speaker_soup = BeautifulSoup(parts[2], 'html.parser')
                                speaker = speaker_soup.get_text().strip()
                                
                            elif len(parts) == 2:
                                # タイトルと1つの内容のみ
                                content_soup = BeautifulSoup(parts[1], 'html.parser')
                                content_text = content_soup.get_text().strip()
                                
                                # AWSで始まるなら発表者、そうでなければ概要
                                if content_text.startswith(('AWS', 'Amazon', '株式会社', '合同会社', 'JSR', '三井住友', '独立行政法人')):
                                    speaker = content_text
                                    description = "セッション概要は準備中です。"
                                else:
                                    description = content_text
                                    speaker = "未定"
                            else:
                                description = "セッション概要は準備中です。"
                                speaker = "未定"
                            
                            session = {
                                'time': time_cell,
                                'title': title,
                                'description': description,
                                'speaker': speaker
                            }
                            
                            sessions_data[stage_name][current_day].append(session)
                            print(f"  {current_day}: {time_cell} - {title}")
    
    return sessions_data

def main():
    # HTMLファイルを読み込み
    try:
        with open('/tmp/summit_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("HTMLファイルが見つかりません。再取得します...")
        response = requests.get('https://pages.awscloud.com/summit-japan-2025-aws-expo-booth.html')
        html_content = response.text
        with open('/tmp/summit_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    # セッション情報を抽出
    sessions = extract_sessions_from_html(html_content)
    
    # JSONファイルに保存
    output_file = '/workspaces/aws-summit-2025-viewer/docs/sessions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    print(f"\nセッション情報を {output_file} に保存しました")
    
    # 統計情報を表示
    total_sessions = 0
    for stage, days in sessions.items():
        stage_total = sum(len(day_sessions) for day_sessions in days.values())
        total_sessions += stage_total
        print(f"{stage}: {stage_total}セッション")
    
    print(f"総セッション数: {total_sessions}")

if __name__ == "__main__":
    main()
