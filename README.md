# Fandom SimpleScrape

[English](README.md) | [中文](README_zh.md)

Fandom SimpleScrape is a lightweight tool for downloading the entire plain text content of a specified Fandom Wiki site. It provides a simple graphical user interface.

## Features

- Basic Gradio Interface
- Batch download of entire text content for a specific Fandom Wiki topic
- Saves content in Markdown format

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation Steps

1. Clone the repository:

`git clone https://github.com/norsizu/Fandom-SimpleScrape.git`

2. Navigate to the project directory:

`cd Fandom-SimpleScrape`

3. Install dependencies:

`pip install -r requirements.txt`

## Usage

1. Run the following command in the project directory to start the program:

`python main.py`

2. In the graphical interface:
- Enter the Fandom Wiki URL you want to download, for example: https://domain_name.fandom.com or https://domain_name.fandom.com/zh (for Chinese sites)
- Specify the save path (default is wiki_md directory)
- Click the "Start Scraping" button to begin downloading

3. The program will start downloading content and save Markdown files in the specified path.

## Version History

- 0.2.0
 - Fixed a silent fail due to CN characters not being installed

## Author

Norsizu – [@norsizu](https://twitter.com/norsizu) 

## Updates and fix by [@davewibs](https://x.com/DaveBotton)

Forks welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

