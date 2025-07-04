# AWS Summit Japan 2025 Mini-Stage Schedule Viewer - 修正履歴

## 2024-06-22

### ヘッダーリンクのアイコン化とX公式カラー統一
- AWSファビコンをダウンロードして追加（`aws-favicon.ico`）
- ヘッダーリンクにアイコンを追加（AWS Expo詳細、マイページ）
- テキストを短縮（「マイページログイン」→「マイページ」）
- XハッシュタグリンクにXロゴ画像を使用（絵文字から変更）
- X公式イメージカラーに統一（黒ベース）
- 1990年代風版はグレー背景で内部統一（セッション詳細の「投稿を見る」ボタンと同じスタイル）

#### デザイン統一
- **モダン版**: 黒背景 + 白Xロゴ（X公式準拠）
- **1990年代風版**: グレー背景 + 黒Xロゴ（Windows 95風統一）
- **Claude版**: グレー背景 + 黒Xロゴ（Windows 95風統一）

#### レスポンシブ対応
- デスクトップ: 16x16pxアイコン、スマートフォン: 12x12pxアイコン
- `display: inline-flex + align-items: center`でアイコンとテキストの適切な配置
- `gap: 6px`でアイコンとテキストの間隔を統一

### X投稿リンク機能の実装
- sessions.jsonに`x_post`フィールドを追加（Community Stage登壇者向け）
- セッション詳細モーダルの「Googleカレンダーに追加」ボタン右側にX投稿リンクを配置
- `x_post`がある場合のみXロゴ付きボタンを表示する条件付き表示機能
- 別ウィンドウでX投稿を開く機能（`target="_blank"`）
- 複数発表者でも混乱しないセッション全体に関連する投稿として配置

#### デザイン統一
- **モダン版**: 黒背景ボタン + 白Xロゴ（logo-white.png）
- **1990年代風版**: Windows 95風グレーボタン + 黒Xロゴ（logo-black.png）
- **Claude版**: Windows 95風グレーボタン + 黒Xロゴ（logo-black.png）

#### レスポンシブ対応
- デスクトップ: 横並び表示（flex-direction: row）
- モバイル: 縦並び表示（flex-direction: column）
- スマホ表示でのボタンサイズ最適化（自然なサイズでGoogleカレンダーボタンと統一）

### スマートフォンでのヘッダタイトル改行問題解決
- Google Pixel 8等での「AWS Summit Japan 2025」タイトル2段表示を防止
- `white-space: nowrap`で強制的に1行表示
- 段階的フォントサイズ調整（768px以下: 1.8em/18px、480px以下: 1.4em/16px）
- `letter-spacing`で文字間隔を最適化（-0.3px、-0.5px）
- `overflow: hidden`と`text-overflow: ellipsis`で長すぎる場合の対応

### 1990年代風トップへ戻るボタンのデザイン統一
- 円形モダンボタンから1990年代風の角型ボタンに変更
- Windows 95風のoutset/insetボーダー効果を追加
- ボタンテキストを「↑」から「TOP」に変更
- MS Sans Serifフォントで統一感を向上
- モバイル版も同様に1990年代風デザインに調整

### タイトル正式名称統一
- 全HTMLファイルのtitleタグを「AWS Summit Japan 2025」の正式名称に変更
- ヘッダーのh1タグも正式名称に統一
- README.md、README.ja.mdも正式名称に更新
- 公式イベント名との整合性を確保

## 2024-06-21

### 発表者のスペース正規化機能追加
- `extract_sessions.py`に`normalize_speaker_spaces()`関数を追加
- 発表者名の連続するスペース（半角・全角・混在）を全角スペース1つに正規化
- 正規表現パターン`r'[\s　]{2,}'`を使用して2個以上の連続スペースを検出
- 全ての発表者処理箇所に適用（複数発表者、単一発表者、フォールバック処理）
- sessions.jsonを最新の正規化データで更新

### マイページログインリンクの追加
- ヘッダー部分に「マイページログイン」リンクを追加
- 「AWS Expo 詳細はこちら」の右側に配置
- 両リンクとも新しいウィンドウで開く設定（`target="_blank"`）
- レスポンシブ対応でPC・スマホ共に2段にならないよう調整
- CSS Flexboxレイアウトで横並び表示
- 文字サイズとパディングを調整（PC: 0.85em、タブレット: 0.75em、スマホ: 0.7em）

### セッション詳細画面の複数発表者表示修正
- `showSessionDetail()`関数で複数発表者の改行表示に対応
- `textContent`から`innerHTML`に変更して`\n`を`<br>`タグに変換
- `#modal-speaker`のCSSに`line-height: 1.5`を追加
- 複数発表者が正しく複数行で表示されるよう修正

### ファイル名整理
- `extract_sessions_v2.py`を`extract_sessions_v0.py`にリネーム
- バージョン階層の明確化（v0: 基本版、Current: 最新版）

### 複数発表者対応機能実装
- `extract_sessions.py`でHTMLの`<br />`タグで区切られた複数発表者に対応
- 正規表現による柔軟なHTMLパターンマッチング
- `getSpeakerName()`関数を強化して複数パターンの発表者名抽出に対応
- CSS `.session-speaker`に`white-space: pre-line`と`-webkit-line-clamp: 2`を追加
- sessions.jsonを複数発表者対応データで更新

### CSS構文エラー修正
- 85行目の余分な`}`を削除
- CSS括弧の整合性を確認（開始230個、終了230個で完全一致）

### アクティブセッション機能とデバッグログシステム実装
- 現在進行中のセッションを緑色でハイライト表示
- パルスアニメーション効果を追加
- 日付・時刻による正確な判定ロジック実装
- パフォーマンス最適化（開催日・時間外はスキップ処理）
- デバッグログシステムの実装
  - `DEBUG_MODE`フラグによる一元制御
  - カテゴリ別ログ出力
  - タイムスタンプ付きログ
  - 本番環境では完全無効化（`DEBUG_MODE = false`）

### レイアウト変更と絵文字追加
- PCとスマホ共通で中央寄せの縦並びレイアウトに変更
- Day1/Day2ボタンを上段、時刻・状況表示を下段に配置
- 時刻表示に絵文字を追加（🕐 時刻、📅 開催前、🔴 開催中、✅ 終了）
- CSS Flexboxで`flex-direction: column`と`align-items: center`を使用
- レスポンシブCSSを簡素化

### 現在時刻と開催状況表示機能追加
- リアルタイム時刻表示（1秒間隔更新）
- AWS Summit開催状況の自動判定
  - 開催前、開催中、本日終了、開催終了の4段階
- 日付と時間による正確な状況判定
- 視覚的なステータス表示（色分け）

### セッション詳細モーダル機能実装
- セッションクリック時の詳細表示モーダル
- セッション情報（時間、タイトル、概要、発表者）の表示
- Googleカレンダー連携機能
- モーダル外クリックでの閉じる機能
- レスポンシブ対応

### 初期実装
- Google Calendar風UIでのスケジュール表示
- 3つのステージ対応（AWS Village Stage、Developers on Live、Community Stage）
- Day1/Day2の日付切り替え機能
- セッションデータの動的読み込み
- レスポンシブデザイン（PC、タブレット、スマートフォン対応）
- セッション抽出スクリプト（`extract_sessions.py`）の実装
- 80セッションのデータ処理
