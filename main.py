import asyncio
import os
import re
from playwright.async_api import async_playwright
from kimi_highlighter import extract_keywords, highlight_keywords_in_html, auto_add_emoji

# --- 新的、健壮的 JavaScript 分页逻辑 ---
JS_PAGINATE_ONE_PAGE = """
([text, isCover]) => {
    const poster = document.getElementById('poster');
    const textContainer = document.getElementById('text-container');
    if (!textContainer) return { pageText: '', remainingText: '' };

    poster.className = isCover ? 'poster-cover' : 'poster-content';

    // 计算 textContainer 的可用高度
    const posterHeight = poster.clientHeight;
    const posterStyle = window.getComputedStyle(poster);
    const posterPaddingTop = parseFloat(posterStyle.paddingTop);
    const posterPaddingBottom = parseFloat(posterStyle.paddingBottom);

    let occupiedHeight = posterPaddingTop + posterPaddingBottom;

    // 获取 textContainer 上方元素的高度
    const imagePlaceholder = poster.querySelector('.image-placeholder');
    if (imagePlaceholder && isCover) { // 仅在封面页
        const style = window.getComputedStyle(imagePlaceholder);
        occupiedHeight += imagePlaceholder.offsetHeight; // 包括内边距和边框
        occupiedHeight += parseFloat(style.marginTop) + parseFloat(style.marginBottom);
    }

    const titleContainer = poster.querySelector('.title-container');
    if (titleContainer && isCover) { // 仅在封面页
        const style = window.getComputedStyle(titleContainer);
        occupiedHeight += titleContainer.offsetHeight;
        occupiedHeight += parseFloat(style.marginTop) + parseFloat(style.marginBottom);
    }

    // 将 textContainer 的 margin-bottom 添加到 occupiedHeight
    const textContainerStyle = window.getComputedStyle(textContainer);
    occupiedHeight += parseFloat(textContainerStyle.marginBottom);

    // textContainer 的最大高度是海报总高度减去已占用高度
    let maxHeight = posterHeight - occupiedHeight;

    // 尊重 CSS 中为 textContainer 自身定义的 max-height
    const cssMaxHeight = parseFloat(textContainerStyle.maxHeight);
    if (!isNaN(cssMaxHeight) && cssMaxHeight > 0 && cssMaxHeight < maxHeight) {
        maxHeight = cssMaxHeight;
    }

    const lineHeight = parseFloat(window.getComputedStyle(textContainer).lineHeight);
    
    // 封面页和内容页使用不同的缓冲策略
    if (isCover) {
        // 封面页：使用最小缓冲，让分页逻辑能容纳完整段落，截图时再添加留白
        if (!isNaN(lineHeight) && lineHeight > 0) {
            maxHeight -= lineHeight * 1;  // 封面页1倍行高缓冲，优先保证段落完整
        }
    } else {
        // 内容页：使用更大的缓冲区确保安全
        if (!isNaN(lineHeight) && lineHeight > 0) {
            maxHeight -= lineHeight * 2;  // 内容页2倍行高
        }
        // 智能断句：为完整句子保留额外空间
        if (maxHeight > lineHeight * 3) {
            maxHeight -= lineHeight * 0.5;
        }
    }

    // 确保 maxHeight 不为负或零
    if (maxHeight <= 0) {
        return { pageText: '', remainingText: text.trim() }; // 没有空间，将所有文本作为剩余文本返回
    }

    // 使用克隆节点进行测量，不影响可见 DOM
    const measureNode = textContainer.cloneNode(true);
    measureNode.style.visibility = 'hidden';
    measureNode.style.height = 'auto'; // 允许其增长
    measureNode.style.position = 'absolute';
    measureNode.style.maxHeight = `${maxHeight}px`; // 将计算出的最大高度应用于测量节点
    poster.appendChild(measureNode);

    // --- 新的、混合原子/可拆分块的分页逻辑 ---
    // 分割输入HTML字符串为主要HTML块（段落、换行符等）
    const htmlBlocks = text.split(/(?=<p|<br>)/).filter(Boolean);

    let pageHTML = '';
    let remainingText = '';
    let i = 0;

    for (i = 0; i < htmlBlocks.length; i++) {
        const currentBlock = htmlBlocks[i];

        // 检查当前块是否是列表项段落
        const isListItemParagraph = currentBlock.startsWith('<p class="list-item"');
        const isParagraph = currentBlock.startsWith('<p');

        // 临时将块添加到measureNode以检查是否适合
        measureNode.innerHTML = pageHTML + currentBlock;

        if (measureNode.scrollHeight > maxHeight) {
            // 如果添加此块导致溢出
            
            // 列表项或非段落块（<br>）是原子单元，整个推到下一页
            if (isListItemParagraph || !isParagraph) {
                break;
            }
            
            // 如果已经有内容了（不是第一个块），优先按完整段落切断
            if (pageHTML.trim().length > 0) {
                // 已有内容，当前段落整个推到下一页
                break;
            } else {
                // 第一个段落且超出空间，需要拆分（否则页面会为空）
                // 回溯：从measureNode中移除currentBlock
                measureNode.innerHTML = pageHTML;

                // 提取段落的内部内容进行拆分
                const paragraphContentMatch = currentBlock.match(/<p([^>]*)>(.*?)<\\/p>/s);
                if (paragraphContentMatch && paragraphContentMatch[2]) {
                    const pTag = paragraphContentMatch[1]; // 保存p标签的属性（如 class="list-item"）
                    const innerContent = paragraphContentMatch[2];
                    
                    // 改进的分词逻辑：保护 HTML 标签不被切断
                    // 将 HTML 标签和文本分别提取出来
                    const tokens = [];
                    let lastIndex = 0;
                    const tagRegex = /<[^>]+>/g;
                    let match;
                    
                    while ((match = tagRegex.exec(innerContent)) !== null) {
                        // 添加标签前的文本（按空格分割）
                        if (match.index > lastIndex) {
                            const textBefore = innerContent.substring(lastIndex, match.index);
                            const words = textBefore.split(/(\\s+)/).filter(Boolean);
                            tokens.push(...words);
                        }
                        // 添加完整的 HTML 标签（不分割）
                        tokens.push(match[0]);
                        lastIndex = match.index + match[0].length;
                    }
                    // 添加最后一个标签后的文本
                    if (lastIndex < innerContent.length) {
                        const textAfter = innerContent.substring(lastIndex);
                        const words = textAfter.split(/(\\s+)/).filter(Boolean);
                        tokens.push(...words);
                    }

                    let subPageHTML = '';
                    let j = 0;
                    for (j = 0; j < tokens.length; j++) {
                        const token = tokens[j];
                        measureNode.innerHTML = pageHTML + '<p' + pTag + '>' + subPageHTML + token + '</p>';
                        if (measureNode.scrollHeight > maxHeight) {
                            // 智能断句：封面页和内容页都启用，但封面页更严格
                            if (j > 0 && subPageHTML.length > 0) {
                                // 定义标点符号（封面页只在句号处断开，内容页可以在更多标点处断开）
                                const punctuation = isCover 
                                    ? ['。', '.']  // 封面页：只在句号处断开
                                    : ['。', '！', '？', '；', '.', '!', '?', ';'];  // 内容页：多种标点
                                let backtrackIndex = j;
                                let foundPunctuation = false;
                                
                                // 向后回溯最多25个token（封面页回溯更远以找到句号）
                                const lookbackLimit = isCover ? 30 : 10;
                                let punctuationToken = '';  // 存储找到的句号token（可能被截断）
                                
                                for (let k = j - 1; k >= Math.max(0, j - lookbackLimit); k--) {
                                    const checkToken = tokens[k];
                                    // 检查这个token（移除HTML标签后）
                                    const tokenText = checkToken.replace(/<[^>]+>/g, '');
                                    
                                    // 检查token是否以句号开头
                                    if (tokenText.length > 0) {
                                        const firstChar = tokenText.trim()[0];
                                        if (punctuation.includes(firstChar)) {
                                            // 找到以句号开头的token，只取句号
                                            punctuationToken = firstChar;
                                            backtrackIndex = k;
                                            foundPunctuation = true;
                                            break;
                                        }
                                        
                                        // 检查token是否以句号结尾
                                        const lastChar = tokenText.trim().slice(-1);
                                        if (punctuation.includes(lastChar)) {
                                            backtrackIndex = k + 1;
                                            foundPunctuation = true;
                                            break;
                                        }
                                    }
                                }
                                
                                // 如果找到了合适的断点，使用它
                                if (foundPunctuation && backtrackIndex <= j) {
                                    j = backtrackIndex;
                                    subPageHTML = tokens.slice(0, j).join('');
                                    // 如果句号是单独的，添加它
                                    if (punctuationToken) {
                                        subPageHTML += punctuationToken;
                                    }
                                }
                            }
                            break;
                        }
                        subPageHTML += token;
                    }

                    // 检查 subPageHTML 是否有未闭合的 HTML 标签（如 <span class="highlight">）
                    if (subPageHTML.trim().length > 0) {
                        // 计算未闭合的标签
                        const openTags = (subPageHTML.match(/<span[^>]*>/g) || []).length;
                        const closeTags = (subPageHTML.match(/<\\/span>/g) || []).length;
                        
                        if (openTags > closeTags) {
                            // 有未闭合的 span 标签，回退到最后一个闭合标签之后或最后一个开标签之前
                            const lastOpenSpanIndex = subPageHTML.lastIndexOf('<span');
                            if (lastOpenSpanIndex >= 0) {
                                // 回退到这个 <span 之前
                                subPageHTML = subPageHTML.substring(0, lastOpenSpanIndex);
                                // 重新计算 j：找到截断位置对应的token索引
                                let charCount = 0;
                                for (let k = 0; k < tokens.length; k++) {
                                    if (charCount + tokens[k].length > subPageHTML.length) {
                                        j = k;
                                        break;
                                    }
                                    charCount += tokens[k].length;
                                }
                            }
                        }
                        
                        pageHTML += '<p' + pTag + '>' + subPageHTML + '</p>';
                    }

                    // 构建剩余文本，包括当前块的剩余部分和后续块（保留原始属性）
                    const remainingTokens = tokens.slice(j).join('');
                    if (remainingTokens.trim().length > 0) {
                        remainingText = '<p' + pTag + '>' + remainingTokens + '</p>';
                    }
                    remainingText += htmlBlocks.slice(i + 1).join('');
                    break;

                } else {
                    // 如果是<p>标签但没有内容，或者正则表达式失败，则视为原子单元
                    break;
                }
            }
        }
        pageHTML += currentBlock; // 如果适合，则添加块
    }

    // 如果循环完成而没有中断，则所有块都适合。
    if (i === htmlBlocks.length) {
        remainingText = '';
    } else if (!remainingText) { // 如果remainingText未在子循环中构建
        remainingText = htmlBlocks.slice(i).join('');
    }

    const debugInfo = {
        posterHeight: poster.clientHeight,
        occupiedHeight: occupiedHeight,
        maxHeight: maxHeight,
        finalScrollHeight: measureNode.scrollHeight,
        pageTextLength: pageHTML.length
    };

    poster.removeChild(measureNode);

    return { pageText: pageHTML.trim(), remainingText: remainingText, debug: debugInfo };
}
"""

def read_input_article(file_path, enable_highlight=True, enable_auto_emoji=False):
    """从输入文件读取标题和正文，并将正文转换为 HTML。
    
    Args:
        file_path: 输入文件路径
        enable_highlight: 是否启用关键词句高亮（默认为True）
        enable_auto_emoji: 是否启用AI智能添加Emoji（默认为False）
        
    Returns:
        tuple: (title, body_html, raw_body_text)
    """
    if not os.path.exists(file_path):
        return None, None, None
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return None, None, None
    title = lines[0].strip()
    body_raw = "".join(lines[1:]).strip()
    
    # === AI 智能添加 Emoji ===
    if enable_auto_emoji:
        print("\n=== [AI] 智能添加 Emoji ===")
        title, body_raw = auto_add_emoji(title, body_raw)
        print("=== Emoji 添加完成 ===\n")

    # 通过双换行符分割获取段落
    paragraphs = body_raw.split('\n\n')
    # 将每个段落包裹在 <p> 标签中，并将段落内的单换行符替换为 <br>
    body_html_parts = []
    for p_text in paragraphs:
        if p_text.strip(): # 仅添加非空段落
            # 检查是否是列表项（以数字. 空格开头）
            if re.match(r'^\d+\.\s', p_text.strip()):
                # 提取列表项标题（数字. 标题: ）并加粗
                # 匹配模式：数字. 标题:
                list_match = re.match(r'^(\d+\.\s+)([^:：]+)([:：]\s*)(.*)', p_text.strip(), re.DOTALL)
                if list_match:
                    number = list_match.group(1)  # "1. "
                    list_title = list_match.group(2)   # "复杂性"（列表项标题，不是文章标题）
                    colon = list_match.group(3)   # ": "
                    content = list_match.group(4) # 剩余内容
                    # 将标题部分用 span 包裹并加粗
                    formatted_text = f'{number}<span class="list-title">{list_title}{colon}</span>{content.replace(chr(10), "<br>")}'
                    body_html_parts.append(f'<p class="list-item">{formatted_text}</p>')
                else:
                    # 如果没有冒号，就整个保持原样
                    body_html_parts.append(f"<p class=\"list-item\">{p_text.replace('\n', '<br>')}</p>")
            else:
                body_html_parts.append(f"<p>{p_text.replace('\n', '<br>')}</p>")
    body_html = "".join(body_html_parts)

    # 如果启用高亮，调用 Kimi API 提取关键词句并标记
    if enable_highlight:
        print("\n=== 开始智能识别关键词句 ===")
        keywords = extract_keywords(body_raw)
        if keywords:
            print(f"识别到的关键词句: {keywords}")
            body_html = highlight_keywords_in_html(body_html, keywords)
        else:
            print("未识别到关键词句或API调用失败")
        print("=== 关键词句识别完成 ===\n")

    return title, body_html, body_raw

async def main():
    """主函数，用于从输入文件生成海报。"""
    # ========================================
    # 配置选项
    # ========================================
    ENABLE_HIGHLIGHT = True      # 启用关键词高亮
    ENABLE_AUTO_EMOJI = True     # 启用AI智能添加Emoji [NEW!]
    # ========================================
    
    title_text, body_html, raw_body = read_input_article(
        "input.txt", 
        enable_highlight=ENABLE_HIGHLIGHT,
        enable_auto_emoji=ENABLE_AUTO_EMOJI
    )
    if not title_text and not body_html:
        print("信息: 'input.txt' 为空或未找到。不会生成海报。")
        return

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        html_file_path = os.path.abspath("index.html")
        await page.goto(f"file://{html_file_path}")

        poster_element = page.locator('#poster')
        display_wrapper = page.locator('#display-wrapper')  # 添加对display-wrapper的引用（外层容器）
        text_container = page.locator('#text-container')
        title_element = page.locator('.title-container') # 定位标题元素

        # 在页面上设置标题
        await title_element.evaluate('(node, text) => node.innerText = text', title_text)

        # --- 开始分页过程 ---
        remaining_text = body_html
        page_count = 0

        # 1. 生成封面页
        print("正在生成封面页...")
        result = await page.evaluate(JS_PAGINATE_ONE_PAGE, [remaining_text, True])
        page_text = result['pageText']
        remaining_text = result['remainingText']
        if (result.get('debug')):
            print(f"  - DEBUG (Cover): {result['debug']}")

        await poster_element.evaluate('(node) => node.className = "poster-cover"')
        await text_container.evaluate('(node, html) => node.innerHTML = html', page_text)
        
        # 封面页：找到容器内最后一个完全可见的段落，确保文字完整显示
        cover_height = await poster_element.evaluate('''(node) => {
            const textContainer = node.querySelector('#text-container');
            if (!textContainer) return 1440;
            
            // 获取行高
            const textStyle = window.getComputedStyle(textContainer);
            const lineHeight = parseFloat(textStyle.lineHeight);
            
            const posterRect = node.getBoundingClientRect();
            const containerRect = textContainer.getBoundingClientRect();
            const containerBottom = containerRect.bottom;  // 容器可视底部
            
            // 找到所有段落
            const paragraphs = textContainer.querySelectorAll('p');
            let lastVisibleParagraph = null;
            
            // 找到最后一个完全可见的段落（底部不超出容器）
            for (let i = 0; i < paragraphs.length; i++) {
                const p = paragraphs[i];
                const pRect = p.getBoundingClientRect();
                
                // 如果段落底部在容器内（完全可见），记录它
                if (pRect.bottom <= containerBottom + 5) {  // +5px容差
                    lastVisibleParagraph = p;
                }
            }
            
            let bottomPosition;
            if (lastVisibleParagraph) {
                // 使用最后一个完全可见段落的底部
                const pRect = lastVisibleParagraph.getBoundingClientRect();
                bottomPosition = pRect.bottom - posterRect.top;
            } else {
                // 如果没有完全可见的段落，使用容器底部
                bottomPosition = containerBottom - posterRect.top;
            }
            
            // 总高度 = 底部位置 + 1.2 行高作为留白，并加 6px 安全缓冲
            const totalHeight = bottomPosition + lineHeight * 1.5;
            const finalHeight = Math.ceil(totalHeight) + 10;
            
            // 设置海报高度
            node.style.height = finalHeight + 'px';
            const displayWrapper = document.querySelector('#display-wrapper');
            if (displayWrapper) {
                displayWrapper.style.height = finalHeight + 'px';
            }
            
            return finalHeight;
        }''')
        
        cover_path = os.path.join(output_dir, "cover.png")
        await display_wrapper.screenshot(path=cover_path)
        print(f"  - 已保存: {cover_path} (智能高度: {cover_height}px，底部留白: 1.2行高+6px)")
        
        # 恢复原始高度
        await poster_element.evaluate('(node) => node.style.height = ""')
        await display_wrapper.evaluate('(node) => node.style.height = ""')
        
        page_count += 1

        # 2. 生成内容页
        while remaining_text:
            page_count += 1
            print(f"正在生成内容页 {page_count}...")
            result = await page.evaluate(JS_PAGINATE_ONE_PAGE, [remaining_text, False])
            page_text = result['pageText']
            remaining_text = result['remainingText']
            if (result.get('debug')):
                print(f"  - DEBUG (Content): {result['debug']}")

            await poster_element.evaluate('(node) => node.className = "poster-content"')
            await text_container.evaluate('(node, html) => node.innerHTML = html', page_text)

            # 内容页：智能调整高度以适应实际内容，底部留白为 1.2 行高并加 6px
            actual_height = await poster_element.evaluate('''(node) => {
                const textContainer = node.querySelector('#text-container');
                if (!textContainer) return node.offsetHeight;
                
                // 找到最后一个子元素
                const lastChild = textContainer.lastElementChild;
                if (!lastChild) return node.offsetHeight;
                
                // 获取行高（一行文字的高度）
                const textStyle = window.getComputedStyle(textContainer);
                const lineHeight = parseFloat(textStyle.lineHeight);
                
                // 获取 poster 和最后元素的位置
                const posterRect = node.getBoundingClientRect();
                const lastChildRect = lastChild.getBoundingClientRect();
                const lastChildBottom = lastChildRect.bottom - posterRect.top;
                
                // 总高度 = 最后元素底部 + 1.2 行高作为底部留白，并加 6px 安全缓冲
                const totalHeight = lastChildBottom + lineHeight * 1.2;
                
                // 添加 6 像素的微调以避免边缘渲染问题
                const finalHeight = Math.ceil(totalHeight) + 6;
                
                // 临时设置海报高度
                node.style.height = finalHeight + 'px';
                
                // 同时调整 display-wrapper 的高度
                const displayWrapper = document.querySelector('#display-wrapper');
                if (displayWrapper) {
                    displayWrapper.style.height = finalHeight + 'px';
                }
                
                return finalHeight;
            }''')

            content_path = os.path.join(output_dir, f"content_{page_count - 1:02d}.png")
            
            # 截取display-wrapper，添加截图选项以避免边框重影
            await display_wrapper.screenshot(path=content_path, animations='disabled', scale='css')
            print(f"  - 已保存: {content_path} (智能高度: {actual_height}px，底部留白: 1.2行高+6px)")
            
            # 恢复原始高度
            await poster_element.evaluate('(node) => node.style.height = ""')
            await display_wrapper.evaluate('(node) => node.style.height = ""')

        await browser.close()
        print("\n所有页面已处理完毕。")

if __name__ == "__main__":
    asyncio.run(main())