#!/usr/bin/env python3
import re
import json
import os
import tempfile
import difflib
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

def filter_session_data(data):
    """
    セッションデータから比較対象のフィールドのみを抽出する
    比較対象: time, title, description, speaker（x_postは除外）
    """
    filtered_data = {}
    target_fields = ['time', 'title', 'description', 'speaker']
    
    for stage, days in data.items():
        filtered_data[stage] = {}
        for day, sessions in days.items():
            filtered_data[stage][day] = []
            for session in sessions:
                filtered_session = {}
                for field in target_fields:
                    if field in session:
                        filtered_session[field] = session[field]
                filtered_data[stage][day].append(filtered_session)
    
    return filtered_data

def compare_json_files(old_file, new_file):
    """
    2つのJSONファイルを比較して差分を表示する（time, title, description, speakerのみ）
    """
    try:
        with open(old_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        with open(new_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except FileNotFoundError as e:
        print(f"ファイルが見つかりません: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSONの解析エラー: {e}")
        return False
    
    # 比較対象のフィールドのみを抽出
    old_filtered = filter_session_data(old_data)
    new_filtered = filter_session_data(new_data)
    
    # JSONを整形された文字列に変換
    old_json_str = json.dumps(old_filtered, ensure_ascii=False, indent=2, sort_keys=True)
    new_json_str = json.dumps(new_filtered, ensure_ascii=False, indent=2, sort_keys=True)
    
    # 差分を計算
    old_lines = old_json_str.splitlines(keepends=True)
    new_lines = new_json_str.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        old_lines, 
        new_lines, 
        fromfile='現在のsessions.json (time, title, description, speaker)',
        tofile='新しいsessions.json (time, title, description, speaker)',
        lineterm=''
    ))
    
    if not diff:
        print("✅ 差分はありません。sessions.jsonは最新の状態です。")
        print("   （比較対象: time, title, description, speaker）")
        return False
    else:
        print("🔍 sessions.jsonに差分が見つかりました:")
        print("   （比較対象: time, title, description, speaker）")
        print("=" * 60)
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                print(f"\033[1m{line.rstrip()}\033[0m")  # 太字
            elif line.startswith('@@'):
                print(f"\033[36m{line.rstrip()}\033[0m")  # シアン
            elif line.startswith('+'):
                print(f"\033[32m{line.rstrip()}\033[0m")  # 緑（追加）
            elif line.startswith('-'):
                print(f"\033[31m{line.rstrip()}\033[0m")  # 赤（削除）
            else:
                print(line.rstrip())
        print("=" * 60)
        return True

def analyze_session_changes(old_file, new_file):
    """
    セッション情報の変更を詳細に分析する（time, title, description, speakerのみ）
    """
    try:
        with open(old_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        with open(new_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    
    # 比較対象のフィールドのみを抽出
    old_filtered = filter_session_data(old_data)
    new_filtered = filter_session_data(new_data)
    
    print("\n📊 変更内容の詳細分析:")
    print("   （比較対象: time, title, description, speaker）")
    print("-" * 40)
    
    # ステージごとに比較
    for stage in set(list(old_filtered.keys()) + list(new_filtered.keys())):
        if stage not in old_filtered:
            print(f"🆕 新しいステージが追加されました: {stage}")
            continue
        elif stage not in new_filtered:
            print(f"🗑️  ステージが削除されました: {stage}")
            continue
        
        # 日ごとに比較
        for day in set(list(old_filtered[stage].keys()) + list(new_filtered[stage].keys())):
            if day not in old_filtered[stage]:
                print(f"🆕 {stage} - {day}: 新しい日が追加されました")
                continue
            elif day not in new_filtered[stage]:
                print(f"🗑️  {stage} - {day}: 日が削除されました")
                continue
            
            old_sessions = old_filtered[stage][day]
            new_sessions = new_filtered[stage][day]
            
            if len(old_sessions) != len(new_sessions):
                print(f"📈 {stage} - {day}: セッション数が変更されました ({len(old_sessions)} → {len(new_sessions)})")
            
            # セッションの詳細比較
            old_titles = {s['title']: s for s in old_sessions}
            new_titles = {s['title']: s for s in new_sessions}
            
            # 新しいセッション
            for title in new_titles:
                if title not in old_titles:
                    print(f"  ➕ 新しいセッション: {title}")
            
            # 削除されたセッション
            for title in old_titles:
                if title not in new_titles:
                    print(f"  ➖ 削除されたセッション: {title}")
            
            # 変更されたセッション
            for title in old_titles:
                if title in new_titles:
                    old_session = old_titles[title]
                    new_session = new_titles[title]
                    
                    changes = []
                    if old_session.get('time') != new_session.get('time'):
                        print(f"  🔄 変更されたセッション: {title}")
                        print(f"    - 時間: {old_session.get('time', 'N/A')} → {new_session.get('time', 'N/A')}")
                    if old_session.get('description') != new_session.get('description'):
                        if not changes:
                            print(f"  🔄 変更されたセッション: {title}")
                        print(f"    - 概要が変更されました")
                    if old_session.get('speaker') != new_session.get('speaker'):
                        if not changes:
                            print(f"  🔄 変更されたセッション: {title}")
                        print(f"    - 発表者: {old_session.get('speaker', 'N/A')} → {new_session.get('speaker', 'N/A')}")
                    
                    # 変更があったかどうかをマーク
                    if (old_session.get('time') != new_session.get('time') or
                        old_session.get('description') != new_session.get('description') or
                        old_session.get('speaker') != new_session.get('speaker')):
                        changes.append(True)

def preserve_xpost_fields(new_sessions, existing_file):
    """
    既存のsessions.jsonからx_postフィールドを保持して新しいセッションデータにマージする
    """
    try:
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        print("🔗 既存のx_postフィールドを保持中...")
        preserved_count = 0
        
        # ステージごとに処理
        for stage in new_sessions:
            if stage not in existing_data:
                continue
                
            # 日ごとに処理
            for day in new_sessions[stage]:
                if day not in existing_data[stage]:
                    continue
                
                new_sessions_list = new_sessions[stage][day]
                existing_sessions_list = existing_data[stage][day]
                
                # 既存セッションをタイトルでインデックス化
                existing_by_title = {session['title']: session for session in existing_sessions_list}
                
                # 新しいセッションにx_postを保持
                for session in new_sessions_list:
                    title = session['title']
                    if title in existing_by_title and 'x_post' in existing_by_title[title]:
                        session['x_post'] = existing_by_title[title]['x_post']
                        preserved_count += 1
                        print(f"  🔗 保持: {stage} - {day} - {title}")
        
        print(f"📊 x_postフィールド保持完了: {preserved_count}個")
        return new_sessions
        
    except FileNotFoundError:
        print("ℹ️  既存ファイルが見つかりません。新規作成します。")
        return new_sessions
    except json.JSONDecodeError as e:
        print(f"⚠️  既存ファイルの解析エラー: {e}")
        return new_sessions
    except Exception as e:
        print(f"⚠️  x_postフィールド保持中にエラー: {e}")
        return new_sessions

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
    
    # 出力ファイルのパス
    output_file = '/workspaces/aws-summit-2025-viewer/docs/sessions.json'
    
    # 既存のx_postフィールドを保持
    sessions = preserve_xpost_fields(sessions, output_file)
    
    # 既存のsessions.jsonが存在するかチェック
    if os.path.exists(output_file):
        print("📋 既存のsessions.jsonが見つかりました。差分をチェックします...")
        
        # 一時ファイルに新しいデータを保存
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as temp_file:
            json.dump(sessions, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name
        
        try:
            # 差分をチェック
            has_changes = compare_json_files(output_file, temp_file_path)
            
            if has_changes:
                # 詳細な変更分析
                analyze_session_changes(output_file, temp_file_path)
                
                # ユーザーに確認
                print(f"\n❓ sessions.jsonを更新しますか？ (y/N): ", end="")
                response = input().strip().lower()
                
                if response in ['y', 'yes']:
                    # 一時ファイルの内容を本ファイルにコピー
                    with open(temp_file_path, 'r', encoding='utf-8') as temp_f:
                        with open(output_file, 'w', encoding='utf-8') as output_f:
                            output_f.write(temp_f.read())
                    print(f"✅ sessions.jsonを更新しました: {output_file}")
                else:
                    print("❌ sessions.jsonの更新をキャンセルしました")
            else:
                print("ℹ️  更新の必要はありません")
                
        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)
    else:
        # 新規作成
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        print(f"🆕 新しいsessions.jsonを作成しました: {output_file}")
    
    # 統計情報を表示
    print(f"\n📊 セッション統計:")
    total_sessions = 0
    for stage, days in sessions.items():
        stage_total = sum(len(day_sessions) for day_sessions in days.values())
        total_sessions += stage_total
        print(f"  {stage}: {stage_total}セッション")
    
    print(f"  総セッション数: {total_sessions}")

if __name__ == "__main__":
    main()
