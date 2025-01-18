import re
from dataclasses import dataclass
# dataclass 是 Python 3.7 引入的一个装饰器，它用于自动生成类中的一些样板代码，特别是那些主要用于存储数据的类。它的主要意义在于简化数据类的创建，减少重复代码，并提高代码的可读性和可维护性。
# dataclass 自动生成数据类的 __init__、__repr__、__eq__ 等常用方法，简化了数据类的创建。

# 抽取结果的数据结构
@dataclass
class TagContentResult:
    """
    A data class to represent the result of extracting tag content.

    Attributes:
        content (List[str]): A list of strings containing the content found between the specified tags.
        found (bool): A flag indicating whether any content was found for the given tag.
    """

    content: list[str]
    found: bool


# 从文本种抽取符合xml标签的内容
def extract_tag_content(text: str, tag: str) -> TagContentResult:
    """
    Extracts all content enclosed by specified tags (e.g., <thought>, <response>, etc.).

    Parameters:
        text (str): The input string containing multiple potential tags.
        tag (str): The name of the tag to search for (e.g., 'thought', 'response').

    Returns:
        dict: A dictionary with the following keys:
            - 'content' (list): A list of strings containing the content found between the specified tags.
            - 'found' (bool): A flag indicating whether any content was found for the given tag.
    """
    # Build the regex pattern dynamically to find multiple occurrences of the tag
    tag_pattern = rf"<{tag}>(.*?)</{tag}>"

    # Use findall to capture all content between the specified tag
    matched_contents = re.findall(tag_pattern, text, re.DOTALL)

    # Return the dataclass instance with the result
    return TagContentResult(
        content=[content.strip() for content in matched_contents],
        found=bool(matched_contents),
    )


if __name__ == "__main__":
    print(TagContentResult)
    # 示例文本
    text = """
    <thought>This is my first thought.</thought>
    <response>This is my first response.</response>
    <thought>This is my second thought. It's a bit longer.</thought>
    <response>This is my second response.</response>
    <other>This should not be extracted.</other>
    """

    # 提取 <thought> 标签的内容
    thought_result = extract_tag_content(text, "thought")
    print("Thought Result:", thought_result) # TagContentResult(content=['This is my first thought.', "This is my second thought. It's a bit longer."], found=True)
    print("Thought Content:", thought_result.content) # ['This is my first thought.', "This is my second thought. It's a bit longer."]
    print("Thought Found:", thought_result.found) # True
    print("-" * 20)