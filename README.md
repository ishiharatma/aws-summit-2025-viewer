# devcontainer-amazon-q-cli

[![🇯🇵 日本語](https://img.shields.io/badge/%F0%9F%87%AF%F0%9F%87%B5-日本語-white)](./README.ja.md) [![🇺🇸 English](https://img.shields.io/badge/%F0%9F%87%BA%F0%9F%87%B8-English-white)](./README.md)

A DevContainer template for Amazon Q CLI. Get started with AI-powered coding assistance instantly - just open in VS Code with Dev Containers extension. Pre-configured environment with Amazon Q CLI installed and ready to use.

## Getting Started

This DevContainer provides a pre-configured environment with Amazon Q CLI installed and ready to use for AI-powered coding assistance. Follow these simple steps to get started:

1. Ensure you have VS Code with the Dev Containers extension installed
2. Clone this repository to your local machine
3. Open the repository in VS Code
4. Click on the "Reopen in Container" option when prompted

## Post-Creation Setup

After your container is built, the postCreateCommand.sh script will automatically run to finalize the setup:

![postCreateCommand](/images/docker-postcreatecommand.jpg)

This script installs all necessary dependencies and configures the Amazon Q CLI for immediate use.

## Using Amazon Q CLI

### Starting Amazon Q Chat

To start a new Amazon Q chat session, use the following command:

```sh
q chat
```

Upon startup, you'll see the initial chat interface where Amazon Q connects to MCP server:

![q-chat-start](/images/q-chat-start.jpg)

As shown in the image, Amazon Q successfully connects to the MCP (Managed Code Processing) server during initialization.

### Available Tools

Amazon Q comes with various tools to assist your development process. You can view these by checking:

![q-chat-tools](/images/q-chat-tools.jpg)

The image shows the list of available tools, including access to the MCP server for advanced code processing capabilities.

## Key Features

Pre-configured development environment with all dependencies installed

- Seamless Amazon Q CLI integration
- Access to MCP server for enhanced coding assistance
- Ready to use without manual configuration steps

Enjoy developing with AI-powered assistance from Amazon Q!
