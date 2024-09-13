import requests
from bs4 import BeautifulSoup
import os
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr

# 清理文件名中的非法字符
def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# 移除参考文献
def remove_references(text):
    return re.sub(r'\[\d+\]', '', text)

# 将 HTML 转换为 Markdown
def html_to_markdown(element):
    if element.name is None:
        return remove_references(element.string or '')
    
    if element.name == 'p':
        return '\n\n' + ''.join(html_to_markdown(child) for child in element.children) + '\n\n'
    
    if element.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(element.name[1])
        return '\n' + '#' * level + ' ' + ''.join(html_to_markdown(child) for child in element.children) + '\n'
    
    if element.name == 'a':
        link_text = ''.join(html_to_markdown(child) for child in element.children).strip()
        if not link_text:
            return ''
        return link_text
    
    if element.name == 'ul':
        return '\n' + ''.join('- ' + html_to_markdown(li) + '\n' for li in element.find_all('li', recursive=False))
    
    if element.name == 'ol':
        return '\n' + ''.join(f"{i+1}. {html_to_markdown(li)}\n" for i, li in enumerate(element.find_all('li', recursive=False)))
    
    if element.name == 'img':
        return ''
    
    return ''.join(html_to_markdown(child) for child in element.children)

# 处理页面，抓取并处理所有页面
def get_and_process_page(url, base_url, save_dir):
    print(f"Processing page: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = soup.select('ul.mw-allpages-chunk li a')
    page_urls = [base_url + link['href'] for link in links]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_page, page_url, save_dir) for page_url in page_urls]
        for future in as_completed(futures):
            future.result()
    
    next_link = soup.find('div', class_='mw-allpages-nav')
    if next_link:
        next_link = next_link.find('a', text=lambda text: '下一页' in text if text else False)
    if next_link:
        return base_url + next_link['href']
    return None

# 下载页面内容
def download_page(url, save_dir):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('h1', class_='page-header__title').text.strip()
        content = soup.find('div', class_='mw-parser-output')
        
        if content:
            markdown_content = html_to_markdown(content)
            
            filename = clean_filename(title) + '.md'
            with open(os.path.join(save_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(markdown_content)
            
            return f"Downloaded: {title}"
        else:
            return f"No content found for: {url}"
    except Exception as e:
        return f"Error downloading {url}: {str(e)}"

# 主抓取函数
def scrape_fandom(fandom_url, save_path):
    # 自动去掉末尾的 `/`
    fandom_url = fandom_url.rstrip('/')
    base_url = fandom_url.rsplit('/', 1)[0]
    all_pages_url = fandom_url + "/wiki/Special:AllPages"
    
    # 检查并创建保存路径
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    current_url = all_pages_url
    messages = []
    
    while current_url:
        messages.append(f"Processing page list from: {current_url}")
        yield "\n".join(messages)
        
        current_url = get_and_process_page(current_url, base_url, save_path)
        time.sleep(random.uniform(1, 2))
    
    messages.append("Scraping completed!")
    yield "\n".join(messages)

def launch_gui():
    gr.close_all()  # 关闭所有已打开的 Gradio 实例
    
    with gr.Blocks(analytics_enabled=False) as iface:
        gr.Markdown("# Fandom SimpleScrape")
        gr.Markdown("Enter the Fandom URL and save path to start scraping. Trailing slashes (`/`) will automatically be removed.")
        
        with gr.Row():
            fandom_url = gr.Textbox(label="Fandom URL (e.g., https://domain_name.fandom.com)")
            save_path = gr.Textbox(label="Save Path", value="wiki_md")
        
        output = gr.Textbox(label="Progress")
        
        scrape_button = gr.Button("Start Scraping")

        def start_scraping(fandom_url, save_path):
            # 开始抓取
            yield "Scraping...", "Starting scraping process..."
            
            # 运行scrape_fandom并逐步更新输出
            for message in scrape_fandom(fandom_url, save_path):
                yield "Scraping...", message
            
            # 任务完成
            yield "Start Scraping", "Scraping completed!"

        # 点击按钮后启动scrape_fandom函数
        scrape_button.click(
            fn=start_scraping, 
            inputs=[fandom_url, save_path], 
            outputs=[scrape_button, output]
        )

    iface.launch()

if __name__ == "__main__":
    launch_gui()