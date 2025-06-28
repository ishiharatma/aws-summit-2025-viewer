#!/usr/bin/env python3
import json
import sys

def restore_xpost_fields(current_file, backup_file, output_file):
    """
    現在のsessions.jsonにバックアップからx_postフィールドを復元する
    """
    try:
        # 現在のファイルを読み込み
        with open(current_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        # バックアップファイルを読み込み
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print("🔄 x_postフィールドを復元中...")
        restored_count = 0
        
        # ステージごとに処理
        for stage in current_data:
            if stage not in backup_data:
                continue
                
            # 日ごとに処理
            for day in current_data[stage]:
                if day not in backup_data[stage]:
                    continue
                
                current_sessions = current_data[stage][day]
                backup_sessions = backup_data[stage][day]
                
                # バックアップセッションをタイトルでインデックス化
                backup_by_title = {session['title']: session for session in backup_sessions}
                
                # 現在のセッションにx_postを復元
                for session in current_sessions:
                    title = session['title']
                    if title in backup_by_title and 'x_post' in backup_by_title[title]:
                        session['x_post'] = backup_by_title[title]['x_post']
                        restored_count += 1
                        print(f"  ✅ 復元: {stage} - {day} - {title}")
        
        # 結果を保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 復元完了:")
        print(f"  復元されたx_postフィールド数: {restored_count}")
        print(f"  出力ファイル: {output_file}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ ファイルが見つかりません: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSONの解析エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def main():
    current_file = '/workspaces/aws-summit-2025-viewer/docs/sessions.json'
    backup_file = '/tmp/sessions_with_xpost.json'
    output_file = '/workspaces/aws-summit-2025-viewer/docs/sessions.json'
    
    print("🔍 x_postフィールドの復元を開始します...")
    print(f"  現在のファイル: {current_file}")
    print(f"  バックアップファイル: {backup_file}")
    
    success = restore_xpost_fields(current_file, backup_file, output_file)
    
    if success:
        print("\n✅ x_postフィールドの復元が完了しました！")
    else:
        print("\n❌ x_postフィールドの復元に失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()
