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
        tables = content_div.find_all('table')
        
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
                            
                            # セッション概要と発表者を抽出
                            content_text = content_cell.get_text()
                            
                            # タイトルの後の部分を取得
                            parts = content_text.split(title, 1)
                            if len(parts) > 1:
                                remaining_text = parts[1].strip()
                                
                                # 発表者は最後の行（通常「AWS　...」で始まる）
                                lines = [line.strip() for line in remaining_text.split('\n') if line.strip()]
                                
                                # 概要と発表者を分離
                                description = ""
                                speaker = ""
                                
                                if lines:
                                    # 発表者を探す（通常「AWS」で始まる行）
                                    speaker_lines = []
                                    desc_lines = []
                                    
                                    for line in lines:
                                        if line.startswith(('AWS', 'Amazon', '株式会社', '合同会社', 'JSR', '三井住友', '独立行政法人')):
                                            speaker_lines.append(line)
                                        else:
                                            desc_lines.append(line)
                                    
                                    description = '\n'.join(desc_lines).strip()
                                    speaker = '\n'.join(speaker_lines).strip() if speaker_lines else "未定"
                                
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
