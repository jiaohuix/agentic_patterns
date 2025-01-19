import os

from openai import OpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS

from agentic_patterns.tool_pattern.tool import tool
from agentic_patterns.planning_pattern.react_agent import ReactAgent
from agentic_patterns.utils.completions import completions_create


ddgs = DDGS()

@tool
def search(query: str) -> str:
    """
    网络搜索引擎，输入查询，输出top10条相关新闻内容。

    该函数使用DDGS（DuckDuckGo Search）进行搜索，将搜索结果进行格式化处理后返回。
    每条搜索结果包含标题、链接和正文内容，以Markdown格式展示，方便用户查看和点击。

    Args:
        query (str): 搜索查询关键词。

    Returns:
        str: 格式化后的搜索结果字符串，包含多条搜索结果。

    Example:
        >>> result = search("如何发财")
        >>> print(result)
        ## Search Results
        [1 标题1](链接1)
        正文内容1
        [2 标题2](链接2)
        正文内容2
        ...

    Note:
        搜索结果的数量和质量可能受到DDGS搜索算法和网络环境的影响。
    """
    results = ddgs.text(query, max_results=10)
    postprocessed_results = [f"[[citation:{idx}]] [{result['title']}]({result['href']})\n{result['body']}" for idx, result in enumerate(results, start=1)]
    # [title](url) \n
    # body
    return "## Search Results\n\n" + "\n\n".join(postprocessed_results)

# print(search(query="如何发财"))


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')

client = OpenAI(
api_key=OPENAI_API_KEY,
base_url=OPENAI_API_BASE
)
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
model_name = "Qwen/Qwen2.5-Coder-32B-Instruct"
model_name = "LoRA/meta-llama/Meta-Llama-3.1-8B-Instruct"
model_name = "internlm/internlm2_5-20b-chat"
model_name = "THUDM/glm-4-9b-chat"
# model_name = "Qwen/Qwen2.5-14B-Instruct"

# query = "最近小红书和ticktok哪个股票可能比较利好 搜索后再调用generate_answer回答"
query = "最近小红书发生了什么事情，股票利好吗"

@tool
def generate_answer(query: str, context: str) -> str:
    """
    根据给定的查询和上下文，生成回答。【每次遇到网络搜索，或者本地知识库检索到文本片段，需要把完整的context和query作为输入，调用generate_answer！】

    该函数使用OpenAI的API，将查询和上下文组合成提示，然后调用模型生成回答。
    回答会遵循给定的格式要求，引用上下文中的信息，并以专业的语气呈现。

    Args:
        query (str): 用户的问题。
        context (str): 与问题相关的上下文信息，包含多条引用内容。

    Returns:
        str: 生成的回答字符串。

    Example:
        >>> context = search("如何发财")
        >>> result = answer_bot("如何发财", context)
        >>> print(result)
        根据搜索结果，发财的方法有...[citation:1][citation:3]

    Note:
        回答的质量和准确性依赖于上下文信息的完整性和模型的性能。
        如果上下文信息不足，回答可能会包含“信息缺失”的提示。
    """
    prompt = _rag_query_text.format(query=query, context=context)
    messages = [{"role":"user", "content": prompt}]
    ret = completions_create(client, messages= messages, model = model_name)

    return ret

sys_prompt = """
You are a large language AI assistant built by jiaohuix. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

Remember, don't blindly repeat the contexts verbatim.
"""

agent = ReactAgent(tools=[search],client=client,
        model=model_name, system_prompt=sys_prompt)
res = agent.run(user_msg=query)
