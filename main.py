import asyncio
import os
import re
from playwright.async_api import async_playwright

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

    // 增加一个完整行高的安全缓冲区，确保最后一行不会被截断
    const lineHeight = parseFloat(window.getComputedStyle(textContainer).lineHeight);
    if (!isNaN(lineHeight) && lineHeight > 0) {
        maxHeight -= lineHeight;
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
            if (isListItemParagraph || !isParagraph) { // 列表项或非段落块（<br>）是原子单元
                // 将整个块推到下一页。
                break; // 在添加此块之前中断
            } else {
                // 如果是普通段落（<p>...</p>），我们需要逐词拆分它。
                // 回溯：从measureNode中移除currentBlock
                measureNode.innerHTML = pageHTML;

                // 提取段落的内部内容进行拆分
                const paragraphContentMatch = currentBlock.match(/<p[^>]*>(.*?)<\/p>/s);
                if (paragraphContentMatch && paragraphContentMatch[1]) {
                    const innerContent = paragraphContentMatch[1];
                    const subTokens = innerContent.split(/(\s+)/).filter(Boolean); // 按词和空白分割

                    let subPageHTML = '';
                    let j = 0;
                    for (j = 0; j < subTokens.length; j++) {
                        const subToken = subTokens[j];
                        measureNode.innerHTML = pageHTML + '<p>' + subPageHTML + subToken + '</p>'; // 重新包裹在<p>中
                        if (measureNode.scrollHeight > maxHeight) {
                            break;
                        }
                        subPageHTML += subToken;
                    }

                    // 将适合的部分添加到pageHTML，重新包裹在<p>中
                    if (subPageHTML.trim().length > 0) {
                        pageHTML += '<p>' + subPageHTML + '</p>';
                    }

                    // 构建剩余文本，包括当前块的剩余部分和后续块
                    const remainingSubTokens = subTokens.slice(j).join('');
                    if (remainingSubTokens.trim().length > 0) {
                        remainingText = '<p>' + remainingSubTokens + '</p>'; // 重新包裹剩余部分在<p>中
                    }
                    remainingText += htmlBlocks.slice(i + 1).join(''); // 添加后续块
                    break; // 我们已经处理了此块，其余部分转到下一页

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

def read_input_article(file_path):
    """从输入文件读取标题和正文，并将正文转换为 HTML。"""
    if not os.path.exists(file_path):
        return None, None
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return None, None
    title = lines[0].strip()
    body_raw = "".join(lines[1:]).strip()

    # 通过双换行符分割获取段落
    paragraphs = body_raw.split('\n\n')
    # 将每个段落包裹在 <p> 标签中，并将段落内的单换行符替换为 <br>
    body_html_parts = []
    for p_text in paragraphs:
        if p_text.strip(): # 仅添加非空段落
            # Check if it's a list item (starts with digit. space)
            # Check if it's a list item (starts with digit. space)
            if re.match(r'^\d+\.\s', p_text.strip()):
                body_html_parts.append(f"<p class=\"list-item\">{p_text.replace('\n', '<br>')}</p>")
            else:
                body_html_parts.append(f"<p>{p_text.replace('\n', '<br>')}</p>")
    body_html = "".join(body_html_parts)

    return title, body_html

async def main():
    """主函数，用于从输入文件生成海报。"""
    title_text, body_html = read_input_article("input.txt")
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
        
        cover_path = os.path.join(output_dir, "article_01_cover.png")
        await poster_element.screenshot(path=cover_path)
        print(f"  - 已保存: {cover_path}")
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

            content_path = os.path.join(output_dir, f"article_01_content_{page_count - 1:02d}.png")
            await poster_element.screenshot(path=content_path)
            print(f"  - 已保存: {content_path}")

        await browser.close()
        print("\n所有页面已处理完毕。")

if __name__ == "__main__":
    asyncio.run(main())