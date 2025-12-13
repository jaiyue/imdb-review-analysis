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
from datetime import datetime

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

def extract_vote_counts(review_element):
    """Extract vote counts"""
    helpful_count = 0
    not_helpful_count = 0
    
    try:
        vote_selectors = [
            '.ipc-voting',
            '.review-helpful',
            '[class*="vote"]',
            '[class*="helpful"]',
            '.ipc-list-card_actions'
        ]
        
        vote_section = None
        for selector in vote_selectors:
            try:
                vote_section = review_element.find_element(By.CSS_SELECTOR, selector)
                if vote_section:
                    break
            except:
                continue
        
        if vote_section:
            vote_html = vote_section.get_attribute('innerHTML')
            
            helpful_patterns = [
                r'helpful.*?(\d+)',
                r'(\d+)\s*people found this helpful',
                r'helpful.*?>\s*(\d+)\s*<',
                r'ipc-voting_label_count--up.*?>(\d+)<',
                r'data-value="(\d+)"[^>]*data-testid="helpful-button"'
            ]
            
            for pattern in helpful_patterns:
                match = re.search(pattern, vote_html, re.IGNORECASE)
                if match:
                    try:
                        helpful_count = int(match.group(1))
                        break
                    except:
                        pass
            
            not_helpful_patterns = [
                r'not.*?helpful.*?(\d+)',
                r'unhelpful.*?(\d+)',
                r'ipc-voting_label_count--down.*?>(\d+)<',
                r'data-value="(\d+)"[^>]*data-testid="unhelpful-button"'
            ]
            
            for pattern in not_helpful_patterns:
                match = re.search(pattern, vote_html, re.IGNORECASE)
                if match:
                    try:
                        not_helpful_count = int(match.group(1))
                        break
                    except:
                        pass
            
            if helpful_count == 0 and not_helpful_count == 0:
                vote_text = vote_section.text.lower()
                if 'helpful' in vote_text:
                    numbers = re.findall(r'\d+', vote_text)
                    if len(numbers) >= 2:
                        helpful_count = int(numbers[0])
                        not_helpful_count = int(numbers[1])
                    elif len(numbers) == 1:
                        helpful_count = int(numbers[0])
    
    except Exception as e:
        print(f"  Error extracting votes: {e}")
    
    return helpful_count, not_helpful_count

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
                        
                except Exception as e:
                    continue
            
            if clicked:
                break
                
        except Exception as e:
            continue
    
    if not clicked:
        try:
            see_all_button = driver.execute_script("""
                const buttons = document.querySelectorAll('button, span, a');
                for (let btn of buttons) {
                    if (btn.innerText && btn.innerText.trim().toLowerCase().includes('see all')) {
                        return btn;
                    }
                }
                return null;
            """)
            
            if see_all_button:
                print(f"Found 'See All' button via JavaScript: {see_all_button.text.strip()}")
                
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", see_all_button)
                time.sleep(0.5)
                
                if see_all_button.is_displayed() and see_all_button.is_enabled():
                    see_all_button.click()
                    print("Clicked 'See All' button (via JS)")
                    clicked = True
                    
                    wait_time = random.uniform(3, 5)
                    time.sleep(wait_time)
        except Exception as e:
            pass
    
    if not clicked:
        print("'See All' button not found or not clickable")
    
    return clicked

def expand_all_spoilers(driver):
    """Expand all spoiler buttons on the page"""
    try:
        spoiler_selectors = [
            'button.ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--button-radius.ipc-btn--on-error.ipc-text-button.sc-b8d6d2b6-1.beKHlT.review-spoiler-button',
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
        
        unique_buttons = []
        seen_ids = set()
        for button in spoiler_buttons:
            try:
                btn_id = button.id or button.get_attribute('data-testid') or button.get_attribute('aria-label')
                if not btn_id:
                    btn_id = f"{button.tag_name}_{button.location['x']}_{button.location['y']}"
                
                if btn_id not in seen_ids:
                    seen_ids.add(btn_id)
                    unique_buttons.append(button)
            except:
                unique_buttons.append(button)
        
        spoiler_buttons = unique_buttons
        
        expanded_count = 0
        for button in spoiler_buttons:
            try:
                if not button.is_displayed():
                    continue
                
                try:
                    button_text = button.text.strip().lower()
                    aria_label = button.get_attribute('aria-label') or ""
                    aria_label_lower = aria_label.lower()
                    
                    is_spoiler_button = (
                        'spoiler' in button_text or 
                        'spoiler' in aria_label_lower or
                        'expand' in button_text or
                        'show' in button_text
                    )
                    
                    if is_spoiler_button:
                        driver.execute_script("""
                            const element = arguments[0];
                            const yOffset = -100;
                            const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
                            window.scrollTo({top: y, behavior: 'smooth'});
                        """, button)
                        time.sleep(0.5)
                        
                        driver.execute_script("arguments[0].click();", button)
                        expanded_count += 1
                        time.sleep(0.3)
                        
                except Exception as click_error:
                    try:
                        if button.is_enabled():
                            button.click()
                            expanded_count += 1
                            time.sleep(0.3)
                    except Exception as regular_error:
                        continue
                        
            except Exception as e:
                continue
        
        time.sleep(1)
        
    except Exception as e:
        print(f"Error finding spoiler buttons: {e}")

def get_unique_reviews(driver):
    """Get unique reviews, avoid duplicates"""
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
        except Exception as e:
            continue
    
    unique_reviews = []
    seen_ids = set()
    
    for review in review_elements:
        try:
            review_id = review.get_attribute('id') or review.get_attribute('data-review-id')
            
            if not review_id:
                try:
                    title = ""
                    try:
                        title_element = review.find_element(By.CSS_SELECTOR, 
                            '.ipc-title.ipc-title--base.ipc-title--title.ipc-title--on-textPrimary.sc-b8d6d2b6-7.fUoiwh')
                        title = title_element.text.strip()[:50]
                    except:
                        try:
                            title_element = review.find_element(By.CSS_SELECTOR, 
                                '.ipc-title.ipc-title--title, h3[class*="title"]')
                            title = title_element.text.strip()[:50]
                        except:
                            pass
                    
                    if title:
                        review_id = f"title_{hash(title)}"[:100]
                    else:
                        review_id = f"review_{len(unique_reviews)}"
                except:
                    review_id = f"review_{len(unique_reviews)}"
            
            if review_id not in seen_ids:
                seen_ids.add(review_id)
                unique_reviews.append(review)
                
        except Exception as e:
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
    Main function: Get review data
    """
    print(f"Accessing: {movie_url}")
    driver.get(movie_url)
    
    wait_time = random.uniform(4, 6)
    time.sleep(wait_time)
    
    page_title = driver.title
    print(f"Page title: {page_title}")
    
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="accept-button"]'))
        )
        cookie_button.click()
        time.sleep(1)
        print("Accepted Cookie")
    except:
        print("Cookie button not found or already accepted")
    
    clicked = click_see_all_button(driver)
    
    if clicked:
        extra_wait = random.uniform(2, 4)
        time.sleep(extra_wait)
    
    expand_all_spoilers(driver)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    check_and_click_see_all_after_scroll(driver)
    
    expand_all_spoilers(driver)
    time.sleep(2)
    
    review_elements = get_unique_reviews(driver)
    
    if not review_elements:
        print("Error: No reviews found!")
        return None, None
    
    title_list = []
    content_list = []
    helpful_list = []
    not_helpful_list = []
    has_spoiler_list = []
    rating_list = []
    
    for i, review in enumerate(review_elements):
        try:
            if (i + 1) % 20 == 0:
                print(f"Processing progress: {i+1}/{len(review_elements)}")
            
            title = ""
            try:
                title_selectors = [
                    '.ipc-title.ipc-title--base.ipc-title--title.ipc-title--on-textPrimary.sc-b8d6d2b6-7.fUoiwh',
                    '.ipc-title.ipc-title--title',
                    'h3[class*="title"]',
                    'a[class*="title"]',
                    '.title',
                    '[data-testid*="title"]'
                ]
                
                for selector in title_selectors:
                    try:
                        title_element = review.find_element(By.CSS_SELECTOR, selector)
                        title_text = title_element.text.strip()
                        if title_text:
                            title = title_text
                            break
                    except:
                        continue
                
                if not title:
                    try:
                        parent = review.find_element(By.XPATH, "..")
                        for selector in title_selectors:
                            try:
                                title_element = parent.find_element(By.CSS_SELECTOR, selector)
                                title_text = title_element.text.strip()
                                if title_text:
                                    title = title_text
                                    break
                            except:
                                continue
                    except:
                        pass
                        
            except Exception as e:
                pass
            
            content = ""
            try:
                content_element = review.find_element(By.CSS_SELECTOR, '.ipc-html-content-inner-div')
                content = content_element.text.strip()
            except:
                try:
                    content_selectors = [
                        '.text.show-more__control',
                        '.content .text',
                        '.review-text',
                        '.content',
                        'div[class*="content"]'
                    ]
                    
                    for selector in content_selectors:
                        try:
                            content_element = review.find_element(By.CSS_SELECTOR, selector)
                            if content_element.text.strip():
                                content = content_element.text.strip()
                                break
                        except:
                            continue
                except Exception as e:
                    pass
            
            if content:
                content = clean_review_content(content, title)
            
            has_spoiler = False
            try:
                if content and any(keyword in content.lower()[:200] for keyword in ['spoiler']):
                    has_spoiler = True
                
                try:
                    spoiler_button = review.find_element(By.CSS_SELECTOR, 
                        '.review-spoiler-button, button[aria-label*="spoiler"]')
                    if spoiler_button:
                        has_spoiler = True
                except:
                    pass
                    
            except:
                pass
            
            helpful_count, not_helpful_count = extract_vote_counts(review)
            
            rating = "No rating"
            try:
                rating_selectors = [
                    '.rating-other-user-rating span',
                    '.rating-other-user-rating',
                    '[class*="rating"] span',
                    'span[class*="rating"]',
                    '.ipc-rating-star'
                ]
                
                for selector in rating_selectors:
                    try:
                        rating_element = review.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_element.text.strip()
                        match = re.search(r'(\d+)(?:\s*/\s*10)?', rating_text)
                        if match:
                            rating = f"{match.group(1)}/10"
                            break
                    except:
                        continue
            except:
                pass
            
            title_list.append(title)
            content_list.append(content)
            helpful_list.append(helpful_count)
            not_helpful_list.append(not_helpful_count)
            has_spoiler_list.append("Yes" if has_spoiler else "No")
            rating_list.append(rating)
            
        except Exception as e:
            title_list.append("")
            content_list.append("")
            helpful_list.append(0)
            not_helpful_list.append(0)
            has_spoiler_list.append("Error")
            rating_list.append("Error")
            continue
    
    print(f"\nDone! Processed total {len(review_elements)} reviews")
    return (title_list, content_list, helpful_list, not_helpful_list, 
            has_spoiler_list, rating_list, page_title)

def save_results(data, movie_id, movie_url, folder_name='reviews'):
    """Save results to CSV file"""
    (title_list, content_list, helpful_list, not_helpful_list, 
     has_spoiler_list, rating_list, page_title) = data
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        movie_title = page_title.split('-')[0].strip()
        safe_title = re.sub(r'[^\w\s-]', '', movie_title).strip().replace(' ', '_')[:50]
    except:
        safe_title = f"movie_{movie_id}"
    
    print(f"\n{'='*60}")
    print(f"Data Statistics")
    print(f"{'='*60}")
    print(f"Total reviews: {len(content_list)}")
    print(f"Valid titles: {sum(1 for t in title_list if t and len(t) > 0)}")
    print(f"Valid content: {sum(1 for c in content_list if c and len(c) > 10)}")
    print(f"Reviews with spoilers: {sum(1 for s in has_spoiler_list if s == 'Yes')}")
    print(f"Total helpful votes: {sum(helpful_list)}")
    print(f"Total not helpful votes: {sum(not_helpful_list)}")
    
    if content_list:
        df = pd.DataFrame({
            'Review_Title': title_list,
            'Review_Content': content_list,
            'Helpful_Count': helpful_list,
            'Not_Helpful_Count': not_helpful_list,
            'Has_Spoiler': has_spoiler_list,
            'Rating': rating_list,
            'Review_Index': list(range(1, len(content_list) + 1)),
            'movie_id': [movie_id] * len(content_list),
            'Scrape_Time': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(content_list)
        })
        
        output_file = f'{folder_name}/{movie_id}_{safe_title}_reviews_{timestamp}.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ Data saved to: {output_file}")
        
        stats = {
            'Total_Reviews': len(content_list),
            'Reviews_with_Title': sum(1 for t in title_list if t and len(t) > 0),
            'Reviews_with_Content': sum(1 for c in content_list if c and len(c) > 10),
            'Reviews_with_Spoiler': sum(1 for s in has_spoiler_list if s == 'Yes'),
            'Total_Helpful_Votes': sum(helpful_list),
            'Total_Not_Helpful_Votes': sum(not_helpful_list),
            'Average_Helpful_per_Review': sum(helpful_list) / len(helpful_list) if helpful_list else 0,
            'Average_Not_Helpful_per_Review': sum(not_helpful_list) / len(not_helpful_list) if not_helpful_list else 0,
            'Movie_ID': movie_id,
            'URL': movie_url,
            'Scrape_Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Page_Title': page_title
        }
        
        stats_df = pd.DataFrame([stats])
        stats_file = f'{folder_name}/{movie_id}_{safe_title}_stats_{timestamp}.csv'
        stats_df.to_csv(stats_file, index=False, encoding='utf-8')
        print(f"\n✓ Statistics saved to: {stats_file}")
        
        return output_file, stats_file
    
    return None, None

def main():
    """Main function"""
    folder_name = 'reviews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    PATH = "./ChromeDrive/chromedriver/chromedriver"
    
    if not os.path.exists(PATH):
        print(f"Error: ChromeDriver file does not exist: {PATH}")
        print("Please ensure file path is correct or re-download ChromeDriver")
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
        
        if data[0] is not None:
            data_file, stats_file = save_results(data, movie_id, movie_url, folder_name)
            
            if data_file:
                print(f"\n✓ Scraping completed!")
                print(f"   Data file: {data_file}")
                print(f"   Statistics file: {stats_file}")
            else:
                print("\n✗ Scraping failed, no data saved")
        else:
            print("\n✗ Failed to retrieve review data")
            
    except Exception as e:
        print(f"\n✗ Error during scraper execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\nBrowser closed")

if __name__ == '__main__':
    main()