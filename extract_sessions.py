#!/usr/bin/env python3
import re
import json
from bs4 import BeautifulSoup
import requests

def normalize_speaker_spaces(speaker_text):
    """
    発表者名の連続するスペース（半角・全角）を全角スペース1つに置き換える
    """
    if not speaker_text:
        return speaker_text
    
    # 連続する半角スペース、全角スペース、混在を全角スペース1つに置き換え
    # \s+ は半角スペース、タブ、改行などの空白文字
    # 　+ は全角スペースの連続
    # [\s　]+ は半角・全角スペースの混在した連続
    normalized = re.sub(r'[\s　]{2,}', '　', speaker_text)
    
    return normalized

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
                            
                            # HTMLの内容を取得
                            cell_html = str(content_cell)
                            
                            # <br /><br />で分割してセッション概要と発表者を分離
                            parts = re.split(r'<br\s*/?\s*>\s*<br\s*/?\s*>', cell_html, flags=re.IGNORECASE)
                            
                            description = ""
                            speaker = ""
                            
                            if len(parts) >= 3:
                                # parts[0]: タイトル部分
                                # parts[1]: 概要部分
                                # parts[2]: 発表者部分
                                
                                # 概要部分からHTMLタグを除去
                                desc_soup = BeautifulSoup(parts[1], 'html.parser')
                                description = desc_soup.get_text().strip()
                                
                                # 発表者部分を処理（複数発表者対応）
                                speaker_soup = BeautifulSoup(parts[2], 'html.parser')
                                speaker_html = str(speaker_soup)
                                
                                # 発表者部分を<br />で分割
                                speaker_parts = re.split(r'<br\s*/?\s*>', speaker_html, flags=re.IGNORECASE)
                                speakers = []
                                
                                for speaker_part in speaker_parts:
                                    speaker_text = BeautifulSoup(speaker_part, 'html.parser').get_text().strip()
                                    if speaker_text and not speaker_text.startswith('<'):
                                        # AWS、Amazon、会社名で始まる行を発表者として認識
                                        if (speaker_text.startswith(('AWS', 'Amazon', '株式会社', '合同会社', 'JSR', '三井住友', '独立行政法人')) or
                                            '　' in speaker_text or '氏' in speaker_text or '様' in speaker_text):
                                            # スペースを正規化してから追加
                                            normalized_speaker = normalize_speaker_spaces(speaker_text)
                                            speakers.append(normalized_speaker)
                                
                                # 複数発表者を改行で結合
                                speaker = '\n'.join(speakers) if speakers else "未定"
                                
                            elif len(parts) == 2:
                                # parts[0]: タイトル部分
                                # parts[1]: 概要または発表者
                                
                                content_soup = BeautifulSoup(parts[1], 'html.parser')
                                content_text = content_soup.get_text().strip()
                                
                                # 内容が発表者情報かどうかを判定
                                if content_text.startswith(('AWS', 'Amazon', '株式会社', '合同会社', 'JSR', '三井住友', '独立行政法人')):
                                    speaker = normalize_speaker_spaces(content_text)
                                    description = "セッション概要は準備中です。"
                                else:
                                    description = content_text
                                    speaker = "未定"
                            else:
                                # フォールバック処理
                                temp_soup = BeautifulSoup(cell_html, 'html.parser')
                                title_span_in_temp = temp_soup.find('span', style=lambda x: x and 'font-weight: bold' in x)
                                if title_span_in_temp:
                                    title_span_in_temp.decompose()
                                
                                remaining_text = temp_soup.get_text().strip()
                                lines = [line.strip() for line in remaining_text.split('\n') if line.strip()]
                                
                                if len(lines) >= 2:
                                    # 最後の行が発表者、それ以外が概要
                                    speaker = normalize_speaker_spaces(lines[-1])
                                    description = ' '.join(lines[:-1]).strip()
                                elif len(lines) == 1:
                                    if lines[0].startswith(('AWS', 'Amazon', '株式会社', '合同会社', 'JSR', '三井住友', '独立行政法人')):
                                        speaker = normalize_speaker_spaces(lines[0])
                                        description = "セッション概要は準備中です。"
                                    else:
                                        description = lines[0]
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
