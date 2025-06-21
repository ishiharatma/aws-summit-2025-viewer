# devcontainer-amazon-q-cli

[![🇯🇵 日本語](https://img.shields.io/badge/%F0%9F%87%AF%F0%9F%87%B5-日本語-white)](./README.ja.md) [![🇺🇸 English](https://img.shields.io/badge/%F0%9F%87%BA%F0%9F%87%B8-English-white)](./README.md)

Amazon Q CLI用のDevContainerテンプレートです。AI駆動のコーディング支援をすぐに利用開始できます - VS CodeのDev Containers拡張機能で開くだけです。Amazon Q CLIがインストール済みで、すぐに使用できる事前設定済み環境です。

## はじめに

このDevContainerは、Amazon Q CLIがインストール済みで、AI駆動のコーディング支援にすぐに使用できる事前設定済み環境を提供します。以下の簡単な手順に従って開始してください。

1. Dev Containers拡張機能がインストールされたVS Codeがあることを確認してください
2. このリポジトリをローカルマシンにクローンしてください
3. VS Codeでリポジトリを開いてください
4. プロンプトが表示されたら「Reopen in Container」オプションをクリックしてください

## 作成後のセットアップ

コンテナがビルドされた後、postCreateCommand.shスクリプトが自動的に実行され、セットアップを完了します。

![postCreateCommand](/images/docker-postcreatecommand.jpg)

## Amazon Q CLIの使用

### Amazon Qチャットの開始

新しいAmazon Qチャットセッションを開始するには、以下のコマンドを使用してください。

```sh
q chat
```

起動時に、Amazon QがMCPサーバーに接続する初期チャットインターフェースが表示されます。

![q-chat-start](/images/q-chat-start.jpg)

画像に示されているように、Amazon Qは初期化中にMCP（Managed Code Processing）サーバーに正常に接続します。

### 利用可能なツール

Amazon Qには開発プロセスを支援する様々なツールが含まれています。これらは以下を確認することで表示できます。

![q-chat-tools](/images/q-chat-tools.jpg)

画像は利用可能なツールのリストを表示しており、高度なコード処理機能のためのMCPサーバーへのアクセスも含まれています。

## 主な機能

- すべての依存関係がインストール済みの事前設定済み開発環境
- シームレスなAmazon Q CLI統合
- 拡張コーディング支援のためのMCPサーバーへのアクセス
- 手動設定手順なしですぐに使用可能

Amazon QのAI駆動支援で開発をお楽しみください！
