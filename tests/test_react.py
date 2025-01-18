import os
import math

from openai import OpenAI
from dotenv import load_dotenv

from agentic_patterns.tool_pattern.tool import tool
from agentic_patterns.utils.extraction import extract_tag_content
from agentic_patterns.planning_pattern.react_agent import ReactAgent

@tool
def sum_two_elements(a: int, b: int) -> int:
    """
    Computes the sum of two integers.

    Args:
        a (int): The first integer to be summed.
        b (int): The second integer to be summed.

    Returns:
        int: The sum of `a` and `b`.
    """
    return a + b


@tool
def multiply_two_elements(a: int, b: int) -> int:
    """
    Multiplies two integers.

    Args:
        a (int): The first integer to multiply.
        b (int): The second integer to multiply.

    Returns:
        int: The product of `a` and `b`.
    """
    return a * b

@tool
def compute_log(x: int) -> float | str:
    """
    Computes the logarithm of an integer `x` with an optional base.

    Args:
        x (int): The integer value for which the logarithm is computed. Must be greater than 0.

    Returns:
        float: The logarithm of `x` to the specified `base`.
    """
    if x <= 0:
        return "Logarithm is undefined for values less than or equal to 0."
    
    return math.log(x)


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')


client = OpenAI(
api_key=OPENAI_API_KEY,
base_url=OPENAI_API_BASE
)
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

available_tools = {
    "sum_two_elements": sum_two_elements,
    "multiply_two_elements": multiply_two_elements,
    "compute_log": compute_log
}
query = "I want to calculate the sum of 1234 and 5678 and multiply the result by 5. Then, I want to take the logarithm of this result"
print("query:", query)
agent = ReactAgent(tools=[sum_two_elements, multiply_two_elements, compute_log],client=client,
        model=model_name)
agent.run(user_msg=query)
