# Text2Poster Generator - 用户手册

## 简介

Text2Poster Generator 是一个简单的 Python 脚本，它利用 Playwright 自动化浏览器操作，将 `input.txt` 中的文本转换为具有预定义样式的海报图片。

## 安装依赖

在运行脚本之前，请确保您的系统已安装 Python 3。然后，按照以下步骤安装所需的 Python 库和浏览器驱动：

1.  **创建 `requirements.txt` 文件** (如果尚未创建):

    ```
    playwright
    ```

2.  **安装 Python 依赖**:

    打开命令行或终端，导航到项目根目录，然后运行：

    ```bash
    pip install -r requirements.txt
    ```

3.  **安装 Playwright 浏览器驱动**:

    在命令行或终端中运行：

    ```bash
    python -m playwright install
    ```

    这将下载并安装 Playwright 所需的浏览器（如 Chromium）。

## 准备 `input.txt`

`input.txt` 文件用于提供生成海报的文本内容。请确保该文件位于项目根目录。

-   **格式**：每行包含一条您希望生成海报的文本。
-   **示例**：

    ```
    Hello, Gemini!
    This is a test.
    Generate a poster for me.
    ```

## 运行 `main.py` 脚本

准备好 `input.txt` 后，您可以运行 `main.py` 脚本来生成海报。

1.  **导航到项目根目录**：

    在命令行或终端中，使用 `cd` 命令进入您的项目文件夹。

2.  **执行脚本**：

    ```bash
    python main.py
    ```

    脚本将开始生成海报，并在命令行中显示进度信息。生成的海报图片将保存到项目根目录下的 `output/` 文件夹中。

## 输出

所有生成的海报图片将以 `poster_01.png`, `poster_02.png` 等格式命名，并存储在 `output/` 文件夹中。
