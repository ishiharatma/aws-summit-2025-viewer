# 開発ルール・指示書

## 🚨 最重要原則

### ユーザー指示の必須性
- **基本原則**: 全ての変更はユーザーの明示的な指示に基づいて実行
- **AI作業者**: ユーザーの許可なしにファイル変更を行ってはならない
- **例外なし**: 緊急時やバグ修正であっても事前確認が必要
- **確認方法**: 変更内容と影響範囲を説明し、明確な許可を得る

### 指示書変更の特別規則
- **特別扱い**: 本ファイル（DEVELOPMENT_RULES.md）とAI_INSTRUCTIONS.mdの変更は特別規則が適用
- **二重確認**: 一般的なファイル変更許可とは独立して、指示書変更の明確な指示が必要
- **明示的要求**: 「指示書を変更して」「ルールを追加して」等の明確な指示が必要
- **暗黙的禁止**: 他の作業指示に含まれていても、指示書への明確な言及がなければ変更禁止
- **保護対象**: プロジェクトの根幹となるルールを保護するための特別措置

---

## コミット・プッシュ時の必須ルール

### 1. DEBUG_MODE確認
- **必須**: コミット前に`DEBUG_MODE = false`であることを確認
- **場所**: `docs/index.html`内のJavaScript部分
- **理由**: 本番環境でのパフォーマンス最適化とログ出力防止

### 2. コミットメッセージ
- **言語**: 英語
- **形式**: 簡潔で明確な説明
- **内容**: 変更内容、技術的詳細、影響範囲を含む

### 3. 自動コミット・プッシュの制限
- **原則**: 表示確認後にユーザーの指示を待つ
- **例外**: 明示的に指示された場合のみ自動実行

## 変更履歴の記録

### HISTORY.md更新ルール
- **タイミング**: 主要な機能追加・修正時
- **順序**: 最新が上（逆時系列）
- **言語**: 日本語
- **内容**: 
  - 実装した機能の概要
  - 技術的詳細
  - ユーザー体験への影響
  - 修正したファイル

### 記録対象
- 新機能の追加
- UI/UXの改善
- バグ修正
- パフォーマンス最適化
- セキュリティ改善
- データ構造の変更

## コーディング規約

### JavaScript
- **デバッグログ**: `debugLog()`関数を使用
- **フラグ制御**: `DEBUG_MODE`による制御
- **関数命名**: キャメルケース
- **コメント**: 日本語可

### Python
- **関数命名**: スネークケース
- **docstring**: 日本語可
- **エラーハンドリング**: 適切な例外処理

### CSS
- **命名**: ケバブケース
- **レスポンシブ**: モバイルファーストアプローチ
- **ブラウザ対応**: モダンブラウザ対応

## ファイル管理

### 重要ファイル
- `docs/index.html`: メインアプリケーション
- `docs/sessions.json`: セッションデータ
- `extract_sessions.py`: データ抽出スクリプト（最新版）
- `extract_sessions_v0.py`: 旧版（参考用）

### バックアップ方針
- 重要な変更前にファイルのバックアップを検討
- バージョン管理はGitで行う

## セキュリティ

### 外部リンク
- `target="_blank"`使用時は`rel="noopener noreferrer"`を併記
- XSS対策: `innerHTML`使用時は適切なサニタイズ

### データ処理
- ユーザー入力の適切な検証
- HTMLエスケープの実装

## パフォーマンス

### 最適化方針
- 不要な処理のスキップ（開催日・時間外など）
- DOM操作の最小化
- 効率的なデータ構造の使用

### 監視項目
- ページ読み込み速度
- JavaScript実行時間
- メモリ使用量

## テスト

### 動作確認項目
- 全デバイス対応（PC、タブレット、スマートフォン）
- 全ブラウザ対応
- 日付・時刻変更による動作確認
- セッション詳細表示の確認

### データ整合性
- sessions.jsonの構文確認
- セッション数の確認（80セッション）
- 発表者情報の正規化確認

## 緊急時対応

### ロールバック手順
1. 問題のあるコミットを特定
2. `git revert`でロールバック
3. 修正版の作成・テスト
4. 再デプロイ

### 連絡体制
- 重要な変更は事前相談
- 問題発生時は即座に報告

---

**注意**: このファイルは開発作業の指針として作成されています。新しいルールや変更があった場合は、このファイルを更新してください。
