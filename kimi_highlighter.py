"""
Kimi API 关键词句提取模块
用于智能识别文本中的关键词句并返回列表
"""
import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

KIMI_API_KEY = os.getenv('KIMI_API_KEY')
KIMI_API_URL = os.getenv('KIMI_API_URL', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
KIMI_MODEL = os.getenv('KIMI_MODEL', 'kimi-k2-250905')


def extract_keywords(text):
    """
    调用 Kimi API 提取文本中的关键词句
    
    Args:
        text: 输入的文本内容
        
    Returns:
        list: 关键词句列表，如果失败则返回空列表
    """
    if not KIMI_API_KEY:
        print("错误：未找到 KIMI_API_KEY 环境变量")
        return []
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KIMI_API_KEY}"
    }
    
    system_prompt = """我希望你扮演一个关键词句提取助手。你的任务是从文本中提取需要高亮显示的关键词句。

**重要规则**：
1. 必须提取文本中**原本就存在的**文字，不要总结或改写
2. 提取5-8个最重要的关键短语或句子片段（5-15个字）
3. 优先选择：核心观点、重要结论、关键动词短语、数字要点
4. 提取的内容必须能在原文中**逐字找到**
5. 避免提取过于常见的词语（如"这是"、"我们"等）

**返回格式**：
- 只返回一个JSON数组，包含提取的原文片段
- 不要有任何其他说明文字
- 格式示例：["原文片段1", "原文片段2", "原文片段3"]

记住：提取的每一个词句都必须是原文中**一字不差**存在的内容！"""
    
    payload = {
        "model": KIMI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }
    
    try:
        print("正在调用 Kimi API 提取关键词句...")
        response = requests.post(
            KIMI_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 提取 API 返回的内容
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content'].strip()
            print(f"API 返回内容: {content}")
            
            # 尝试解析为 JSON 列表
            try:
                # 移除可能的 markdown 代码块标记
                content = content.replace('```json', '').replace('```', '').strip()
                keywords = json.loads(content)
                
                if isinstance(keywords, list):
                    print(f"成功提取 {len(keywords)} 个关键词句")
                    return keywords
                else:
                    print(f"警告：API 返回的不是列表格式，而是: {type(keywords)}")
                    return []
            except json.JSONDecodeError as e:
                print(f"警告：无法解析 API 返回的 JSON: {e}")
                print(f"原始内容: {content}")
                # 尝试按行分割
                lines = [line.strip().strip('"-,') for line in content.split('\n') if line.strip()]
                return lines if lines else []
        else:
            print("警告：API 返回格式异常")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"API 请求失败: {e}")
        return []
    except Exception as e:
        print(f"提取关键词句时发生错误: {e}")
        return []


def highlight_keywords_in_html(html_text, keywords):
    """
    在 HTML 文本中标记关键词句
    
    Args:
        html_text: 原始 HTML 文本
        keywords: 关键词句列表
        
    Returns:
        str: 标记后的 HTML 文本
    """
    if not keywords:
        return html_text
    
    import re
    
    # 按长度排序，优先匹配长的关键词句，避免短词匹配覆盖长词
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    result = html_text
    highlighted_count = 0
    matched_keywords = []
    
    for keyword in sorted_keywords:
        if not keyword or len(keyword.strip()) == 0:
            continue
        
        keyword = keyword.strip()
        
        # 避免重复标记已经高亮的内容
        if f'<span class="highlight">{keyword}</span>' in result:
            continue
        
        # 尝试找到关键词的所有可能匹配
        # 使用正则表达式进行匹配
        escaped_keyword = re.escape(keyword)
        
        # 使用 finditer 找到所有匹配项
        matches = list(re.finditer(escaped_keyword, result))
        
        if not matches:
            # 如果精确匹配失败，尝试部分匹配（至少匹配70%的字符）
            min_match_len = int(len(keyword) * 0.7)
            if len(keyword) > 5:  # 只对较长的关键词进行部分匹配
                for i in range(len(keyword) - min_match_len + 1):
                    partial = keyword[i:i+min_match_len+5] if i+min_match_len+5 <= len(keyword) else keyword[i:]
                    matches = list(re.finditer(re.escape(partial), result))
                    if matches:
                        keyword = partial  # 使用部分匹配的关键词
                        break
        
        if matches:
            # 取第一个匹配项
            match = matches[0]
            start, end = match.span()
            
            # 确保不在标签内（简单检查：向前查找最近的 < 和 >）
            before = result[:start]
            last_open = before.rfind('<')
            last_close = before.rfind('>')
            
            # 如果最后一个 < 在最后一个 > 之后，说明在标签内，跳过
            if last_open > last_close:
                continue
            
            # 检查是否已经在高亮标签内
            if '<span class="highlight">' in before[max(0, len(before)-50):]:
                after = result[end:end+50]
                if '</span>' in after:
                    continue
            
            matched_text = result[start:end]
            result = result[:start] + f'<span class="highlight">{matched_text}</span>' + result[end:]
            highlighted_count += 1
            matched_keywords.append(matched_text)
    
    print(f"成功标记 {highlighted_count} 个关键词句: {matched_keywords[:3]}{'...' if len(matched_keywords) > 3 else ''}")
    return result


if __name__ == "__main__":
    # 测试代码
    test_text = """哈喽，我是大康。在我给老板们的SOP培训中，"如何确定哪些流程需要SOP？"这个议题频频出现。
    复杂的流程通常更容易出错，需要更多的协调和管理。
    SOP可以帮助明确步骤和责任。"""
    
    keywords = extract_keywords(test_text)
    print(f"提取的关键词句: {keywords}")
    
    html = "<p>复杂的流程通常更容易出错，需要更多的协调和管理。</p>"
    highlighted = highlight_keywords_in_html(html, keywords)
    print(f"标记后的HTML: {highlighted}")
