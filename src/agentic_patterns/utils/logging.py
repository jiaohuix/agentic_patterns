import time

from colorama import Fore
from colorama import Style
'''
1 colorama 是一个 Python 库，它允许你在终端中使用 ANSI 转义序列来控制文本的颜色和样式，而无需考虑不同的操作系统。这意味着你的代码可以在 Windows、macOS 和 Linux 等平台上都能正常工作，并显示相同的颜色和样式。
2 Fore 模块用于设置文本的前景色（即文本本身的颜色）。它提供了一系列常量，代表不同的颜色。
    常用颜色常量：

    Fore.BLACK: 黑色
    Fore.RED: 红色
    Fore.GREEN: 绿色
    Fore.YELLOW: 黄色
    Fore.BLUE: 蓝色
    Fore.MAGENTA: 洋红色
    Fore.CYAN: 青色
    Fore.WHITE: 白色
    Fore.RESET: 重置颜色为默认值
    使用方法：

    将 Fore 模块中的颜色常量与字符串拼接，即可设置字符串的前景色。
    例如：print(Fore.RED + "This text is red.")

3 Style 模块用于设置文本的样式，例如粗体、斜体、下划线等。它也提供了一系列常量，代表不同的样式。
    常用样式常量：

    Style.DIM: 暗淡
    Style.NORMAL: 正常
    Style.BRIGHT: 亮
    Style.RESET_ALL: 重置所有样式为默认值

4 使用方法：

将 Style 模块中的样式常量与字符串拼接，即可设置字符串的样式。
例如：print(Style.BRIGHT + "This text is bright.")
结合 Fore 和 Style

你可以将 Fore 和 Style 模块中的常量组合使用，来设置文本的颜色和样式。

例如：print(Style.BRIGHT + Fore.GREEN + "This text is bright green.")

注意：
print( Style.BRIGHT + "This text is bright green."+Fore.CYAN)
颜色拼接在字符串后面，当前字符串还是之前的颜色，然后后面的字符串才改变颜色
'''

def fancy_print(message: str) -> None:
    """
    Displays a fancy print message.

    Args:
        message (str): The message to display.
    """
    print(Style.BRIGHT + Fore.CYAN + f"\n{'=' * 50}")
    print(Fore.MAGENTA + f"{message}")
    print(Style.BRIGHT + Fore.CYAN + f"{'=' * 50}\n")
    time.sleep(0.5)

# 打印进度
def fancy_step_tracker(step: int, total_steps: int) -> None:
    """
    Displays a fancy step tracker for each iteration of the generation-reflection loop.

    Args:
        step (int): The current step in the loop.
        total_steps (int): The total number of steps in the loop.
    """
    fancy_print(f"STEP {step + 1}/{total_steps}")


if __name__ == "__main__":
    fancy_print(message="hello")
    fancy_step_tracker(1, 10)
