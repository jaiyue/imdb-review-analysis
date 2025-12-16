# from https://github.com/plengxvi/movie_user_review_scraper
# scraper.py
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re
import random
import hashlib

def clean_review_content(content_text, title_text=""):
    """Clean review content, remove ratings and duplicate titles"""
    if not content_text:
        return ""
    
    patterns_to_remove = [
        r'^\d+\s*/\s*10\s*',
        r'^\d+\s*out of\s*10\s*',
        r'^Rating:\s*\d+\s*/\s*10\s*',
    ]
    
    for pattern in patterns_to_remove:
        content_text = re.sub(pattern, '', content_text, flags=re.IGNORECASE)
    
    if title_text and content_text.startswith(title_text):
        content_text = content_text[len(title_text):].strip()
    
    content_text = re.sub(r'^["\']\s*', '', content_text)
    content_text = re.sub(r'^\s*SPOILER\s*', '', content_text, flags=re.IGNORECASE)
    
    content_text = ' '.join(content_text.split())
    
    return content_text.strip()


def click_see_all_button(driver):
    """Click 'See All' button to expand all reviews"""
    print("\nAttempting to find 'See All' button...")
    
    see_all_selectors = [
        'button.ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--button-radius.ipc-btn--on-accent2.ipc-text-button.ipc-see-more__button',
        'button.ipc-see-more__button',
        '.ipc-see-more__button',
        'button[class*="ipc-see-more__button"]',
        'button[class*="see-more"]',
        'span.ipc-see-more_text',
        'button:has(span.ipc-see-more_text)',
    ]
    
    clicked = False
    
    for selector in see_all_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                try:
                    element_text = element.text.strip().lower()
                    
                    if any(keyword in element_text for keyword in ['see all', 'see more', 'all reviews', 'view all']):
                        print(f"Found 'See All' button: {element_text}")
                        
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(0.5)
                        
                        if element.is_displayed() and element.is_enabled():
                            current_url = driver.current_url
                            element.click()
                            print("Clicked 'See All' button")
                            clicked = True
                            
                            wait_time = random.uniform(3, 5)
                            time.sleep(wait_time)
                            
                            new_url = driver.current_url
                            if new_url != current_url:
                                print(f"Warning: URL changed from {current_url} to {new_url}")
                            
                            break
                        
                except Exception:
                    continue
            
            if clicked:
                break
                
        except Exception:
            continue
    
    if not clicked:
        print("'See All' button not found or not clickable")
    
    return clicked

def expand_all_spoilers(driver):
    """Expand all spoiler buttons on the page"""
    try:
        spoiler_selectors = [
            'button.review-spoiler-button',
            'button[class*="review-spoiler-button"]',
            'button[aria-label*="Expand Spoiler"]',
            'button[aria-label*="spoiler"]',
            'button[aria-label*="Spoiler"]',
        ]
        
        spoiler_buttons = []
        for selector in spoiler_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    spoiler_buttons.extend(buttons)
            except:
                continue
        
        expanded_count = 0
        for button in spoiler_buttons:
            try:
                if not button.is_displayed():
                    continue
                driver.execute_script("arguments[0].click();", button)
                expanded_count += 1
                time.sleep(0.3)
            except Exception:
                continue
        
        time.sleep(1)
        
    except Exception as e:
        print(f"Error finding spoiler buttons: {e}")

def get_unique_reviews(driver):
    """Get unique reviews, avoid duplicates using hash of title + content"""
    review_selectors = [
        '[data-testid="review-card-parent"]',
        'div[class*="review-container"]',
        '.lister-item-content',
        '.user-review-item',
        '.imdb-user-review',
        'article[class*="review"]'
    ]
    
    review_elements = []
    for selector in review_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                review_elements.extend(elements)
        except Exception:
            continue
    
    unique_reviews = []
    seen_hashes = set()
    
    for review in review_elements:
        try:
            # 提取标题和内容作为哈希依据
            try:
                title_element = review.find_element(By.CSS_SELECTOR, 
                    '.ipc-title.ipc-title--title, h3[class*="title"]')
                title = title_element.text.strip()
            except:
                title = ""
            
            try:
                content_element = review.find_element(By.CSS_SELECTOR, 
                    '.ipc-html-content-inner-div, .text.show-more__control, .content .text, .review-text')
                content = content_element.text.strip()
            except:
                content = ""
            
            # 生成唯一 hash
            hash_input = (title + content).encode('utf-8')
            review_hash = hashlib.md5(hash_input).hexdigest()
            
            if review_hash not in seen_hashes:
                seen_hashes.add(review_hash)
                unique_reviews.append(review)
                
        except Exception:
            unique_reviews.append(review)
    
    return unique_reviews

def check_and_click_see_all_after_scroll(driver):
    """Check for See All button after scrolling to bottom and click it"""
    initial_review_count = len(get_unique_reviews(driver))
    
    clicked = click_see_all_button(driver)
    
    if clicked:
        time.sleep(3)
        
        new_review_count = len(get_unique_reviews(driver))
        if new_review_count > initial_review_count:
            print(f"Review count increased: {initial_review_count} → {new_review_count}")
    
    return clicked

def get_review_data(driver, movie_url, movie_id):
    """
    Main function: Get review data without vote counts
    """
    print(f"Accessing: {movie_url}")
    driver.get(movie_url)
    
    time.sleep(random.uniform(4, 6))
    page_title = driver.title
    print(f"Page title: {page_title}")
    
    # 点击 cookie 按钮
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="accept-button"]'))
        )
        cookie_button.click()
        time.sleep(1)
    except:
        pass
    
    # 点击 See All 按钮
    if click_see_all_button(driver):
        time.sleep(3)
    
    # 展开剧透
    expand_all_spoilers(driver)
    
    # 滚动并再次检查是否需要点击
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 检查是否有更多内容需要加载
    initial_count = len(get_unique_reviews(driver))
    if click_see_all_button(driver):
        time.sleep(3)
        new_count = len(get_unique_reviews(driver))
        if new_count > initial_count:
            print(f"Loaded more reviews: {initial_count} → {new_count}")
    
    # 再次展开剧透
    expand_all_spoilers(driver)
    time.sleep(2)
    
    # 获取所有评论元素
    review_elements = get_unique_reviews(driver)
    if not review_elements:
        print("Error: No reviews found!")
        # 返回空列表而不是 None, None
        return [], [], [], [], page_title
    
    title_list = []
    content_list = []
    has_spoiler_list = []
    rating_list = []
    
    print(f"Processing {len(review_elements)} reviews...")
    
    for i, review in enumerate(review_elements):
        try:
            # 提取标题
            title = ""
            title_selectors = [
                '.ipc-title.ipc-title--base.ipc-title--title.ipc-title--on-textPrimary.sc-b8d6d2b6-7.fUoiwh',
                '.ipc-title.ipc-title--title',
                'h3[class*="title"]',
                '.title'
            ]
            for selector in title_selectors:
                try:
                    title_element = review.find_element(By.CSS_SELECTOR, selector)
                    if title_element.text.strip():
                        title = title_element.text.strip()
                        break
                except:
                    continue
            
            # 提取内容
            content = ""
            content_selectors = [
                '.ipc-html-content-inner-div',
                '.text.show-more__control',
                '.content .text',
                '.review-text'
            ]
            for selector in content_selectors:
                try:
                    content_element = review.find_element(By.CSS_SELECTOR, selector)
                    if content_element.text.strip():
                        content = clean_review_content(content_element.text.strip(), title)
                        break
                except:
                    continue
            
            # 是否包含剧透
            has_spoiler = "No"
            if content and 'spoiler' in content.lower()[:200]:
                has_spoiler = "Yes"
            try:
                spoiler_button = review.find_element(By.CSS_SELECTOR, '.review-spoiler-button, button[aria-label*="spoiler"]')
                if spoiler_button:
                    has_spoiler = "Yes"
            except:
                pass
            
            # 提取评分
            rating = "No rating"
            rating_selectors = ['.rating-other-user-rating span', '.ipc-rating-star']
            for selector in rating_selectors:
                try:
                    rating_element = review.find_element(By.CSS_SELECTOR, selector)
                    match = re.search(r'(\d+)(?:\s*/\s*10)?', rating_element.text.strip())
                    if match:
                        rating = f"{match.group(1)}/10"
                        break
                except:
                    continue
            
            title_list.append(title)
            content_list.append(content)
            has_spoiler_list.append(has_spoiler)
            rating_list.append(rating)
            
        except Exception as e:
            title_list.append("")
            content_list.append("")
            has_spoiler_list.append("Error")
            rating_list.append("Error")
            continue
    
    print(f"\nDone! Processed total {len(review_elements)} reviews")
    return title_list, content_list, has_spoiler_list, rating_list, page_title

def save_results(data, movie_id, movie_url, folder_name='reviews'):
    """Save results without vote counts or scrape time"""
    title_list, content_list, has_spoiler_list, rating_list, page_title = data
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # 数据 CSV，Review_Index 放在第一列
    df = pd.DataFrame({
        'Review_Index': list(range(1, len(content_list)+1)),
        'Review_Title': title_list,
        'Review_Content': content_list,
        'Has_Spoiler': has_spoiler_list,
        'Rating': rating_list,
        'movie_id': [movie_id]*len(content_list)
    })
    output_file = f'{folder_name}/reviews.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Data saved to: {output_file}")
    
    # 统计 CSV
    stats = {
        'Total_Reviews': len(content_list),
        'Reviews_with_Title': sum(1 for t in title_list if t),
        'Reviews_with_Content': sum(1 for c in content_list if c and len(c) > 10),
        'Reviews_with_Spoiler': sum(1 for s in has_spoiler_list if s == 'Yes'),
        'Movie_ID': movie_id,
        'URL': movie_url,
        'Page_Title': page_title
    }
    stats_df = pd.DataFrame([stats])
    stats_file = f'{folder_name}/stats.csv'
    stats_df.to_csv(stats_file, index=False, encoding='utf-8')
    print(f"✓ Statistics saved to: {stats_file}")
    
    return output_file, stats_file

def main():
    """Main function"""
    folder_name = 'reviews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    PATH = "IMDB_Scraper/ChromeDrive/chromedriver/chromedriver"
    
    if not os.path.exists(PATH):
        print(f"Error: ChromeDriver file does not exist: {PATH}")
        return
    
    os.system(f"chmod +x {PATH}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        movie_url = "https://www.imdb.com/title/tt2948356/reviews/?ref_=tt_ov_ururv"
        movie_id = 1
        
        print("=" * 60)
        print("IMDb Review Scraper v2.0")
        print("=" * 60)
        print(f"Target URL: {movie_url}")
        print(f"Movie ID: {movie_id}")
        
        data = get_review_data(driver, movie_url, movie_id)
        
        # 检查是否成功获取了数据
        if data and len(data[0]) > 0:  # 检查 title_list 是否非空
            data_file, stats_file = save_results(data, movie_id, movie_url, folder_name)
            
            if data_file:
                print(f"\n✓ Scraping completed!")
                print(f"   Data file: {data_file}")
                print(f"   Statistics file: {stats_file}")
            else:
                print("\n✗ Scraping failed, no data saved")
        else:
            print("\n✗ Failed to retrieve review data or no reviews found")
            
    except Exception as e:
        print(f"\n✗ Error during scraper execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\nBrowser closed")

if __name__ == '__main__':
    main()
