# scraper_imdb_complete.py
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
    """清理评论内容，移除评分和重复标题"""
    if not content_text:
        return ""
    
    # 移除开头的评分模式
    patterns_to_remove = [
        r'^\d+\s*/\s*10\s*',
        r'^\d+\s*out of\s*10\s*',
        r'^Rating:\s*\d+\s*/\s*10\s*',
    ]
    
    for pattern in patterns_to_remove:
        content_text = re.sub(pattern, '', content_text, flags=re.IGNORECASE)
    
    # 移除重复的标题
    if title_text and content_text.startswith(title_text):
        content_text = content_text[len(title_text):].strip()
    
    # 移除开头的引号和SPOILER标签
    content_text = re.sub(r'^["\']\s*', '', content_text)
    content_text = re.sub(r'^\s*SPOILER\s*', '', content_text, flags=re.IGNORECASE)
    
    # 清理多余的空格和换行
    content_text = ' '.join(content_text.split())
    
    return content_text.strip()

def extract_vote_counts(review_element):
    """提取投票数量"""
    helpful_count = 0
    not_helpful_count = 0
    
    try:
        # 尝试多种方式查找投票区域
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
            # 获取投票区域的HTML
            vote_html = vote_section.get_attribute('innerHTML')
            
            # 使用正则表达式提取数字
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
            
            # 查找not helpful相关的数字
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
            
            # 如果正则没找到，尝试直接查找文本
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
        print(f"  提取投票时出错: {e}")
    
    return helpful_count, not_helpful_count

def click_see_all_button(driver):
    """点击'See All'按钮展开所有评论"""
    print("\n尝试查找'See All'按钮...")
    
    # 使用你提供的class
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
            print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            for element in elements:
                try:
                    element_text = element.text.strip().lower()
                    print(f"  元素文本: '{element_text}'")
                    
                    # 检查按钮文本是否包含相关关键词
                    if any(keyword in element_text for keyword in ['see all', 'see more', 'all reviews', 'view all']):
                        print(f"找到'See All'按钮: {element_text}")
                        
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(0.5)
                        
                        # 确保按钮可见且可用
                        if element.is_displayed() and element.is_enabled():
                            print(f"按钮状态: 可见={element.is_displayed()}, 可用={element.is_enabled()}")
                            
                            # 记录当前URL（应该不会变化）
                            current_url = driver.current_url
                            print(f"点击前URL: {current_url}")
                            
                            # 点击按钮
                            element.click()
                            print("已点击'See All'按钮")
                            clicked = True
                            
                            # 等待页面处理（URL不会变化，但内容会加载）
                            wait_time = random.uniform(3, 5)
                            print(f"等待 {wait_time:.1f} 秒让页面加载评论...")
                            time.sleep(wait_time)
                            
                            # 检查URL是否变化（不应该变化）
                            new_url = driver.current_url
                            if new_url != current_url:
                                print(f"警告: URL已变化，从 {current_url} 变为 {new_url}")
                            else:
                                print(f"URL未变化: {current_url}")
                            
                            break
                    else:
                        print(f"  元素文本不匹配: '{element_text}'")
                        
                except Exception as e:
                    print(f"  处理元素时出错: {e}")
                    continue
            
            if clicked:
                break
                
        except Exception as e:
            print(f"使用选择器 '{selector}' 时出错: {e}")
            continue
    
    # 如果还没找到，尝试通过文本查找
    if not clicked:
        print("\n尝试通过文本查找'See All'按钮...")
        try:
            # 使用JavaScript查找包含特定文本的按钮
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
                print(f"通过JavaScript找到'See All'按钮: {see_all_button.text.strip()}")
                
                # 滚动并点击
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", see_all_button)
                time.sleep(0.5)
                
                if see_all_button.is_displayed() and see_all_button.is_enabled():
                    current_url = driver.current_url
                    see_all_button.click()
                    print("已点击'See All'按钮（通过JS）")
                    clicked = True
                    
                    # 等待页面加载
                    wait_time = random.uniform(3, 5)
                    print(f"等待 {wait_time:.1f} 秒让页面加载评论...")
                    time.sleep(wait_time)
                    
                    print(f"点击后URL: {driver.current_url} (应该与点击前相同: {current_url})")
        except Exception as e:
            print(f"JavaScript查找失败: {e}")
    
    if not clicked:
        print("未找到'See All'按钮或按钮不可用")
    
    return clicked

def expand_all_spoilers(driver):
    """展开页面上所有的spoiler按钮"""
    try:
        # 使用你提供的class
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
                    print(f"使用选择器 '{selector}' 找到 {len(buttons)} 个spoiler按钮")
                    spoiler_buttons.extend(buttons)
            except:
                continue
        
        # 去重
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
        
        print(f"总共找到 {len(spoiler_buttons)} 个spoiler按钮")
        
        expanded_count = 0
        for i, button in enumerate(spoiler_buttons):
            try:
                # 检查按钮状态
                if not button.is_displayed():
                    print(f"  按钮 {i+1}: 不可见，跳过")
                    continue
                
                # 尝试使用JavaScript点击来避免元素被拦截
                try:
                    # 检查按钮文本或标签
                    button_text = button.text.strip().lower()
                    aria_label = button.get_attribute('aria-label') or ""
                    aria_label_lower = aria_label.lower()
                    
                    # 判断是否是spoiler按钮
                    is_spoiler_button = (
                        'spoiler' in button_text or 
                        'spoiler' in aria_label_lower or
                        '展开' in button_text or
                        '显示' in button_text or
                        'expand' in button_text or
                        'show' in button_text
                    )
                    
                    if is_spoiler_button:
                        # 滚动到按钮上方一点的位置
                        driver.execute_script("""
                            const element = arguments[0];
                            const yOffset = -100;
                            const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
                            window.scrollTo({top: y, behavior: 'smooth'});
                        """, button)
                        time.sleep(0.5)
                        
                        # 尝试使用JavaScript点击来避免元素被拦截
                        driver.execute_script("arguments[0].click();", button)
                        expanded_count += 1
                        print(f"  已展开第 {expanded_count} 个spoiler (使用JS点击)")
                        time.sleep(0.3)
                        
                except Exception as click_error:
                    print(f"  使用JS点击按钮 {i+1} 时出错: {click_error}")
                    
                    # 如果JS点击失败，尝试普通点击
                    try:
                        if button.is_enabled():
                            button.click()
                            expanded_count += 1
                            print(f"  已展开第 {expanded_count} 个spoiler (使用普通点击)")
                            time.sleep(0.3)
                    except Exception as regular_error:
                        print(f"  普通点击按钮 {i+1} 时也出错: {regular_error}")
                        
            except Exception as e:
                print(f"  处理第 {i+1} 个spoiler按钮时出错: {e}")
                continue
        
        print(f"总共展开了 {expanded_count} 个spoiler按钮")
        time.sleep(1)
        
    except Exception as e:
        print(f"查找spoiler按钮时出错: {e}")

def get_unique_reviews(driver):
    """获取唯一的评论，避免重复"""
    # 基于你提供的class信息
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
                print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                review_elements.extend(elements)
        except Exception as e:
            print(f"选择器 '{selector}' 出错: {e}")
            continue
    
    print(f"原始找到 {len(review_elements)} 条评论")
    
    # 使用集合存储唯一的评论ID，避免重复
    unique_reviews = []
    seen_ids = set()
    
    for review in review_elements:
        try:
            # 获取评论ID或创建唯一标识符
            review_id = review.get_attribute('id') or review.get_attribute('data-review-id')
            
            if not review_id:
                # 尝试提取标题创建唯一ID
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
    
    print(f"去重后剩余 {len(unique_reviews)} 条唯一评论")
    return unique_reviews

def check_and_click_see_all_after_scroll(driver):
    """滚动到底部后检查是否有See All按钮并点击"""
    print("\n检查是否有额外的'See All'按钮...")
    
    # 保存当前的评论数量
    initial_review_count = len(get_unique_reviews(driver))
    print(f"当前评论数: {initial_review_count}")
    
    # 检查是否有See All按钮
    clicked = click_see_all_button(driver)
    
    if clicked:
        print("已点击额外的'See All'按钮，等待页面加载...")
        time.sleep(3)
        
        # 检查评论数量是否增加
        new_review_count = len(get_unique_reviews(driver))
        if new_review_count > initial_review_count:
            print(f"评论数量增加: {initial_review_count} → {new_review_count}")
        else:
            print(f"评论数量未增加: {initial_review_count} → {new_review_count}")
    
    return clicked

def get_review_data(driver, movie_url, movie_id, max_reviews=1000):
    """
    主函数：获取评论数据
    """
    print(f"正在访问: {movie_url}")
    driver.get(movie_url)
    
    # 等待页面加载
    wait_time = random.uniform(4, 6)
    print(f"等待 {wait_time:.1f} 秒让页面加载...")
    time.sleep(wait_time)
    
    # 获取页面标题
    page_title = driver.title
    print(f"页面标题: {page_title}")
    print(f"当前URL: {driver.current_url}")
    
    # 接受 Cookie
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="accept-button"]'))
        )
        cookie_button.click()
        time.sleep(1)
        print("已接受 Cookie")
    except:
        print("未找到Cookie按钮或已接受")
    
    # 步骤1: 首先点击"See All"按钮
    print("\n" + "="*60)
    print("步骤1: 查找并点击'See All'按钮")
    print("="*60)
    
    # 点击See All按钮
    clicked = click_see_all_button(driver)
    
    if clicked:
        print("'See All'按钮已点击，等待页面处理...")
        extra_wait = random.uniform(2, 4)
        print(f"额外等待 {extra_wait:.1f} 秒确保评论完全加载...")
        time.sleep(extra_wait)
    else:
        print("未找到或无法点击'See All'按钮，继续执行...")
    
    # 步骤2: 展开所有spoiler
    print("\n" + "="*60)
    print("步骤2: 展开所有spoiler内容")
    print("="*60)
    expand_all_spoilers(driver)
    
    # 步骤3: 最终滚动到底部确保所有内容加载
    print("\n" + "="*60)
    print("步骤3: 最终滚动到底部并检查See All按钮")
    print("="*60)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 滚动到底部后检查是否有See All按钮
    check_and_click_see_all_after_scroll(driver)
    
    # 步骤4: 再次展开可能新加载的spoiler
    print("\n" + "="*60)
    print("步骤4: 展开新加载的spoiler")
    print("="*60)
    expand_all_spoilers(driver)
    time.sleep(2)
    
    # 步骤5: 获取最终评论元素
    print("\n" + "="*60)
    print("步骤5: 收集评论数据")
    print("="*60)
    review_elements = get_unique_reviews(driver)
    
    if not review_elements:
        print("错误: 没有找到任何评论!")
        return None, None
    
    # 存储数据的列表
    title_list = []
    content_list = []
    helpful_list = []
    not_helpful_list = []
    has_spoiler_list = []
    rating_list = []
    
    print(f"\n开始处理 {len(review_elements)} 条唯一评论...")
    
    for i, review in enumerate(review_elements):
        # 移除评论数量限制，获取所有评论
        try:
            if (i + 1) % 20 == 0:
                print(f"处理进度: {i+1}/{len(review_elements)}")
            
            # 获取标题
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
                print(f"  评论 {i+1}: 获取标题时出错: {e}")
            
            # 获取评论内容
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
                    print(f"  评论 {i+1}: 获取内容时出错: {e}")
            
            # 清理内容
            if content:
                content = clean_review_content(content, title)
            
            # 检查是否有spoiler
            has_spoiler = False
            try:
                if content and any(keyword in content.lower()[:200] for keyword in ['spoiler', '剧透']):
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
            
            # 获取投票信息
            helpful_count, not_helpful_count = extract_vote_counts(review)
            
            # 获取评分
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
            
            # 添加到列表
            title_list.append(title)
            content_list.append(content)
            helpful_list.append(helpful_count)
            not_helpful_list.append(not_helpful_count)
            has_spoiler_list.append("Yes" if has_spoiler else "No")
            rating_list.append(rating)
            
        except Exception as e:
            print(f"处理第 {i + 1} 条评论时出错: {e}")
            title_list.append("")
            content_list.append("")
            helpful_list.append(0)
            not_helpful_list.append(0)
            has_spoiler_list.append("Error")
            rating_list.append("Error")
            continue
    
    print(f"\n完成！总共处理了 {len(review_elements)} 条评论")
    return (title_list, content_list, helpful_list, not_helpful_list, 
            has_spoiler_list, rating_list, page_title)

def save_results(data, movie_id, movie_url, folder_name='reviews'):
    """保存结果到CSV文件"""
    (title_list, content_list, helpful_list, not_helpful_list, 
     has_spoiler_list, rating_list, page_title) = data
    
    # 创建时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建安全的文件名
    try:
        movie_title = page_title.split('-')[0].strip()
        safe_title = re.sub(r'[^\w\s-]', '', movie_title).strip().replace(' ', '_')[:50]
    except:
        safe_title = f"movie_{movie_id}"
    
    # 数据统计
    print(f"\n{'='*60}")
    print(f"数据统计")
    print(f"{'='*60}")
    print(f"总评论数: {len(content_list)}")
    print(f"有效标题数: {sum(1 for t in title_list if t and len(t) > 0)}")
    print(f"有效内容数: {sum(1 for c in content_list if c and len(c) > 10)}")
    print(f"有Spoiler的评论数: {sum(1 for s in has_spoiler_list if s == 'Yes')}")
    print(f"总Helpful投票数: {sum(helpful_list)}")
    print(f"总Not Helpful投票数: {sum(not_helpful_list)}")
    
    if helpful_list:
        avg_helpful = sum(helpful_list) / len(helpful_list)
        avg_not_helpful = sum(not_helpful_list) / len(not_helpful_list)
        print(f"平均Helpful投票: {avg_helpful:.2f}")
        print(f"平均Not Helpful投票: {avg_not_helpful:.2f}")
    
    # 保存主数据
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
        print(f"\n✓ 数据已保存到: {output_file}")
        
        # 显示数据预览
        print(f"\n{'='*60}")
        print(f"数据预览（前3条）")
        print(f"{'='*60}")
        for j in range(min(3, len(content_list))):
            print(f"\n评论 {j+1}:")
            print(f"  标题: {title_list[j][:50]}..." if len(title_list[j]) > 50 else f"  标题: {title_list[j]}")
            preview = content_list[j][:100] + "..." if len(content_list[j]) > 100 else content_list[j]
            print(f"  内容: {preview}")
            print(f"  Helpful: {helpful_list[j]}, Not Helpful: {not_helpful_list[j]}")
            print(f"  有Spoiler: {has_spoiler_list[j]}, 评分: {rating_list[j]}")
        
        # 保存统计摘要
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
        print(f"\n✓ 统计数据已保存到: {stats_file}")
        
        return output_file, stats_file
    
    return None, None

def main():
    """主函数"""
    # 确保保存目录存在
    folder_name = 'reviews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # ChromeDriver 路径
    PATH = "./ChromeDrive/chromedriver/chromedriver"
    
    # 检查文件是否存在
    if not os.path.exists(PATH):
        print(f"错误: ChromeDriver 文件不存在: {PATH}")
        print("请确保文件路径正确或重新下载 ChromeDriver")
        return
    
    # 给予执行权限
    os.system(f"chmod +x {PATH}")
    
    # Chrome 选项设置
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
        # 测试URL - Zootopia
        movie_url = "https://www.imdb.com/title/tt2948356/reviews/?ref_=tt_ov_ururv"
        movie_id = 1
        
        print("=" * 60)
        print("IMDb 评论爬虫 v2.0")
        print("=" * 60)
        print(f"目标URL: {movie_url}")
        print(f"电影ID: {movie_id}")
        
        # 获取数据 - 使用较大的max_reviews值但不在循环中限制
        data = get_review_data(driver, movie_url, movie_id, max_reviews=1000)
        
        if data[0] is not None:
            data_file, stats_file = save_results(data, movie_id, movie_url, folder_name)
            
            if data_file:
                print(f"\n✓ 爬取完成！")
                print(f"   数据文件: {data_file}")
                print(f"   统计文件: {stats_file}")
            else:
                print("\n✗ 爬取失败，未保存任何数据")
        else:
            print("\n✗ 未能获取到评论数据")
            
    except Exception as e:
        print(f"\n✗ 爬虫运行时出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\n浏览器已关闭")

if __name__ == '__main__':
    main()