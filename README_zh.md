# Fandom SimpleScrape

[English](README.md) | [中文](README_zh.md)

Fandom SimpleScrape 是一个轻量级工具，用于下载指定页面的 Fandom Wiki 整站的纯文本内容，它提供了一个简单的图形用户界面。

## 功能特点

- 简单易用的图形界面
- 批量下载某个主题的 Fandom Wiki 整站文本内容
- 保存为 Markdown 格式

## 安装

### 前提条件

- Python 3.7+
- pip（Python 包管理器）

### 安装步骤

1. 克隆仓库：

`git clone https://github.com/norsizu/Fandom-SimpleScrape.git`

2. 进入项目目录：

`cd Fandom SimpleScrape`

3. 安装依赖：

`pip install -r requirements.txt`

## 使用方法

1. 在项目目录中运行以下命令启动程序：

`python main.py`

2. 在图形界面中：
- 输入你想下载的 Fandom Wiki URL，例如：https://domain_name.fandom.com或https://domain_name.fandom.com/zh（中文站点）
- 指定保存路径（默认为wiki_md目录）
- 点击 "Start Scraping" 按钮开始下载

3. 程序将开始下载内容，并在指定路径保存 Markdown 文件。

## 版本历史

- 0.1.0
 - 初始发布
 - 基本的下载功能
 - 简单的图形用户界面

## 作者

Norsizu – [@norsizu](https://twitter.com/norsizu) 

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

