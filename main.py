
import asyncio
import os
import re
from playwright.async_api import async_playwright

async def main():
    """
    主函数，为一系列文本生成海报。
    """
    # 要生成海报的文本列表
    text_list = [
        "生活不止眼前的苟且，还有诗和远方的田野。",
        "心之所向，素履以往。",
        "愿你走出半生，归来仍是少年。",
        "每一个不曾起舞的日子，都是对生命的辜负。",
    ]

    # 确保 output 文件夹存在
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 打开本地 HTML 模板
        # 使用 os.path.abspath 获取绝对路径，并构造成 file:// URL
        template_path = os.path.abspath('template.html')
        await page.goto(f'file://{template_path}')

        # 定位要截图的元素和文本容器
        container = page.locator('#main-container')
        text_element = page.locator('#text-content')

        for text in text_list:
            # 填充文本
            await text_element.fill(text)

            # 生成一个安全的文件名，移除在Windows文件名中非法的字符
            safe_text = re.sub(r'[\\/:*?"<>|]', '', text)
            # 截取前30个字符以防文件名过长
            filename = safe_text[:30].strip() + '.png'
            output_path = os.path.join(output_dir, filename)

            # 截图并保存
            await container.screenshot(path=output_path)
            print(f"海报已保存到: {output_path}")

        await browser.close()

if __name__ == "__main__":
    # 在Windows上，为asyncio设置正确的事件循环策略
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
