import requests
from bs4 import BeautifulSoup
import os
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr

# Clean illegal characters from filenames
def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# Remove [1], [2], etc.
def remove_references(text):
    return re.sub(r'\[\d+\]', '', text)

# Convert HTML to Markdown
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
        return link_text
    
    if element.name == 'ul':
        return '\n' + ''.join('- ' + html_to_markdown(li) + '\n' for li in element.find_all('li', recursive=False))
    
    if element.name == 'ol':
        return '\n' + ''.join(f"{i+1}. {html_to_markdown(li)}\n" for i, li in enumerate(element.find_all('li', recursive=False)))
    
    if element.name == 'img':
        return ''  # Skip images
    
    return ''.join(html_to_markdown(child) for child in element.children)

# Download and save a single page
def download_page(url, save_dir):
    try:
        print(f"Downloading: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_el = soup.find('h1', class_='page-header__title')
        content = soup.find('div', class_='mw-parser-output')
        
        if not title_el or not content:
            return f"Skipped (missing content): {url}"
        
        title = title_el.text.strip()
        filename = clean_filename(title) + '.md'
        filepath = os.path.join(save_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            return f"Skipped (already exists): {title}"
        
        markdown_content = html_to_markdown(content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(markdown_content)
        
        return f"Downloaded: {title}"
    except Exception as e:
        return f"Error downloading {url}: {str(e)}"

# Process a "Special:AllPages" chunk and follow the next page link
def get_and_process_page(url, base_url, save_dir):
    print(f"Processing page list: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = soup.select('ul.mw-allpages-chunk li a')
    page_urls = [base_url + link['href'] for link in links]
    print(f"Found {len(page_urls)} articles.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_page, page_url, save_dir) for page_url in page_urls]
        for future in as_completed(futures):
            print(future.result())
    
    next_link_block = soup.find('div', class_='mw-allpages-nav')
    if next_link_block:
        next_link = next_link_block.find('a', string=lambda s: 'next page' in s.lower() if s else False)
        if next_link:
            return base_url + next_link['href']
    
    return None

# Main scraping loop
def scrape_fandom(fandom_url, save_path):
    fandom_url = fandom_url.rstrip('/')
    base_url = fandom_url
    all_pages_url = fandom_url + "/wiki/Special:AllPages"
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    current_url = all_pages_url
    messages = []

    while current_url:
        messages.append(f"Scraping index page: {current_url}")
        yield "\n".join(messages)
        current_url = get_and_process_page(current_url, base_url, save_path)
        time.sleep(random.uniform(1, 2))

    messages.append("Scraping completed!")
    yield "\n".join(messages)

# Gradio GUI
def launch_gui():
    gr.close_all()
    
    with gr.Blocks(analytics_enabled=False) as iface:
        gr.Markdown("# Fandom SimpleScrape")
        gr.Markdown("Enter the Fandom URL and save path to start scraping. Example: `https://villains.fandom.com`")
        
        with gr.Row():
            fandom_url = gr.Textbox(label="Fandom URL")
            save_path = gr.Textbox(label="Save Path", value="wiki_md")
        
        output = gr.Textbox(label="Progress")
        scrape_button = gr.Button("Start Scraping")

        def start_scraping(fandom_url, save_path):
            yield "Scraping...", "Starting scraping process..."
            for message in scrape_fandom(fandom_url, save_path):
                yield "Scraping...", message
            yield "Start Scraping", "Scraping completed!"

        scrape_button.click(
            fn=start_scraping, 
            inputs=[fandom_url, save_path], 
            outputs=[scrape_button, output]
        )

    iface.launch()

# Entry point
if __name__ == "__main__":
    # Option 1: Launch GUI
    launch_gui()

    # Uncomment to test in terminal without GUI
    # for line in scrape_fandom("https://villains.fandom.com", "dump_md"):
    #     print(line)
