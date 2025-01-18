from colorama import Fore
from dotenv import load_dotenv
from openai import OpenAI

from agentic_patterns.utils.completions import build_prompt_structure
from agentic_patterns.utils.completions import completions_create
from agentic_patterns.utils.completions import FixedFirstChatHistory
from agentic_patterns.utils.completions import update_chat_history
from agentic_patterns.utils.logging import fancy_step_tracker



BASE_GENERATION_SYSTEM_PROMPT = """
你的任务是为用户的请求生成尽可能最佳的内容。
如果用户提供批评意见，请回应你之前尝试的修订版本。
你必须始终输出修订后的内容。
"""

BASE_REFLECTION_SYSTEM_PROMPT = """
你的任务是为用户生成的内容生成批评和建议。
如果用户的内容有错误或有需要改进的地方，请输出一个建议和批评列表。如果用户的内容没问题，没有什么需要更改的，请输出：<OK>
"""


class ReflectionAgent:
    """
    A class that implements a Reflection Agent, which generates responses and reflects
    on them using the LLM to iteratively improve the interaction. The agent first generates
    responses based on provided prompts and then critiques them in a reflection step.

    Attributes:
        model (str): The model name used for generating and reflecting on responses.
        client (OpenAI): An instance of the OpenAI client to interact with the language model.
    """

    def __init__(self, client: OpenAI =  None, model: str = "llama-3.1-70b-versatile"):
        self.client = client
        self.model = model

    def _request_completion(
        self,
        history: list,
        verbose: int = 0,
        log_title: str = "COMPLETION",
        log_color: str = "",
    ):
        """
        A private method to request a completion from the Groq model.

        Args:
            history (list): A list of messages forming the conversation or reflection history.
            verbose (int, optional): The verbosity level. Defaults to 0 (no output).

        Returns:
            str: The model-generated response.
        """
        output = completions_create(self.client, history, self.model)

        if verbose > 0:
            print(log_color, f"\n\n{log_title}\n\n", output) # print(color, text)也可以

        return output

    def generate(self, generation_history: list, verbose: int = 0) -> str:
        """
        Generates a response based on the provided generation history using the model.

        Args:
            generation_history (list): A list of messages forming the conversation or generation history.
            verbose (int, optional): The verbosity level, controlling printed output. Defaults to 0.

        Returns:
            str: The generated response.
        """
        return self._request_completion(
            generation_history, verbose, log_title="GENERATION", log_color=Fore.BLUE
        )

    def reflect(self, reflection_history: list, verbose: int = 0) -> str:
        """
        Reflects on the generation history by generating a critique or feedback.

        Args:
            reflection_history (list): A list of messages forming the reflection history, typically based on
                                       the previous generation or interaction.
            verbose (int, optional): The verbosity level, controlling printed output. Defaults to 0.

        Returns:
            str: The critique or reflection response from the model.
        """
        return self._request_completion(
            reflection_history, verbose, log_title="REFLECTION", log_color=Fore.GREEN
        )

    def run(
        self,
        user_msg: str,
        generation_system_prompt: str = "",
        reflection_system_prompt: str = "",
        n_steps: int = 10,
        verbose: int = 0,
    ) -> str:
        """
        Runs the ReflectionAgent over multiple steps, alternating between generating a response
        and reflecting on it for the specified number of steps.

        Args:
            user_msg (str): The user message or query that initiates the interaction.
            generation_system_prompt (str, optional): The system prompt for guiding the generation process.
            reflection_system_prompt (str, optional): The system prompt for guiding the reflection process.
            n_steps (int, optional): The number of generate-reflect cycles to perform. Defaults to 3.
            verbose (int, optional): The verbosity level controlling printed output. Defaults to 0.

        Returns:
            str: The final generated response after all cycles are completed.
        """
        generation_system_prompt += BASE_GENERATION_SYSTEM_PROMPT
        reflection_system_prompt += BASE_REFLECTION_SYSTEM_PROMPT

        # Given the iterative nature of the Reflection Pattern, we might exhaust the LLM context (or
        # make it really slow). That's the reason I'm limitting the chat history to three messages.
        # The `FixedFirstChatHistory` is a very simple class, that creates a Queue that always keeps
        # fixeed the first message. I thought this would be useful for maintaining the system prompt
        # in the chat history.
        generation_history = FixedFirstChatHistory(
            [
                build_prompt_structure(prompt=generation_system_prompt, role="system"),
                build_prompt_structure(prompt=user_msg, role="user"),
            ],
            total_length=3,
        )

        reflection_history = FixedFirstChatHistory(
            [build_prompt_structure(prompt=reflection_system_prompt, role="system")],
            total_length=3,
        )

        for step in range(n_steps):
            if verbose > 0:
                fancy_step_tracker(step, n_steps)

            # Generate the response
            generation = self.generate(generation_history, verbose=verbose)
            update_chat_history(generation_history, generation, "assistant")
            update_chat_history(reflection_history, generation, "user")

            # Reflect and critique the generation
            critique = self.reflect(reflection_history, verbose=verbose)

            if "<OK>" in critique:
                # If no additional suggestions are made, stop the loop
                print(
                    Fore.RED,
                    "\n\nStop Sequence found. Stopping the reflection loop ... \n\n",
                )
                break

            update_chat_history(generation_history, critique, "user")
            update_chat_history(reflection_history, critique, "assistant")

        return generation


if __name__ == "__main__":
    import os
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')



    client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
    )
    model_name = client.models.list().data[0].id
    model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

    # ret = completions_create(client, messages=[{"role":"user","content":"agent是什么"}], model=model_name)    
    # print(ret)

    # Test case: Novel writing
    agent = ReflectionAgent(client=client, model=model_name)
    user_prompt = """请你协助我创作一篇5000字左右的科幻短篇小说，主题是关于一个孤独的宇航员在遥远的星球上发现神秘遗迹的故事。为了确保故事的质量和吸引力，我们需要分阶段进行：

**第一阶段：故事概念设计 (请你先完成此阶段，不要直接开始写故事)**

1.  **故事背景设定：**
    *   详细描述故事发生的宇宙环境，包括时间、地点（星球名称、星系位置等）、科技水平、社会背景等。
    *   这个星球有什么特殊之处？它的环境、地貌、气候如何？
    *   遗迹的性质是什么？它来自哪个文明？这个文明有什么特点？
2.  **角色设定：**
    *   详细描述主角宇航员的背景、性格、动机、目标。
    *   他/她为什么会独自一人？他/她有什么特殊技能或经历？
    *   他/她与遗迹之间有什么联系？
3.  **吸引人点设计：**
    *   故事的悬念是什么？如何在一开始就抓住读者的注意力？
    *   故事的核心冲突是什么？是外部的危险还是内部的挣扎？
    *   故事的主题是什么？想要表达什么？
    *   考虑使用倒叙手法，从一个高潮或悬念点开始，然后再慢慢揭示故事的背景。
4.  **故事大纲：**
    *   基于以上设计，列出故事的主要情节节点，包括开头、发展、高潮、结局。
    *   每个章节的大致内容和目标是什么？
    *   考虑使用倒叙，开头从哪个时间点开始？

**第二阶段：章节编写与润色 (请在完成第一阶段后，再进行此阶段)**

1.  **逐章编写：**
    *   根据第一阶段的大纲，逐章编写故事内容。
    *   注意描写细节、人物情感、环境氛围。
    *   确保故事节奏流畅，情节紧凑。
2.  **章节润色：**
    *   每完成一章，请你进行润色，包括：
        *   检查语法、拼写、标点错误。
        *   优化句子结构，使表达更清晰流畅。
        *   增强描写力度，使场景更生动。
        *   确保情节逻辑合理，前后呼应。
        *   考虑读者的感受，确保故事引人入胜。

**第三阶段：整体润色与修改 (请在完成第二阶段后，再进行此阶段)**

1.  **整体润色：**
    *   通读全文，检查故事整体的连贯性、逻辑性。
    *   确保主题明确，表达清晰。
    *   检查是否有重复或冗余的内容。
2.  **修改建议：**
    *   根据整体润色结果，提出修改建议。
    *   根据建议进行修改，直到故事达到最佳状态。

**请注意：**

*   请你先完成第一阶段的故事概念设计，不要直接开始写故事。
*   在第二阶段，请逐章编写和润色，不要一次性完成所有章节。
*   在第三阶段，请进行整体润色和修改，确保故事的质量。
*   请注意使用倒叙手法，开头就吸引读者。
*   请确保故事的科幻元素合理，并具有一定的想象力。

我期待你出色的表现！
"""
    user_prompt = """请你协助我创作一篇5000字左右的科幻短篇小说，主题是关于一个孤独的宇航员在遥远星球上发现神秘遗迹的故事。

**创作流程：**

1.  **概念设计：**
    *   先设计故事背景（星球、遗迹、科技）、角色（宇航员）、吸引人点（悬念、冲突、主题）。
    *   设计一个倒叙的开头，从高潮或悬念点开始。
    *   列出故事大纲（主要情节节点）。
2.  **逐章编写与润色：**
    *   根据大纲，逐章编写故事内容。
    *   每章完成后，进行润色（语法、流畅度、描写、逻辑）。
3.  **整体润色与修改：**
    *   通读全文，检查连贯性、逻辑性、主题。
    *   根据检查结果，提出修改建议并进行修改。

**要求：**

*   先完成概念设计，再开始写作。
*   逐章编写和润色，不要一次性完成。
*   使用倒叙手法，开头吸引人。
*   确保科幻元素合理，具有想象力。

我期待你出色的表现！
"""
    user_prompt = "请你协助我创作一篇5000字左右的科幻短篇小说，主题是关于一个孤独的宇航员在遥远的星球上发现神秘遗迹的故事。首先，设计科幻小说背景、角色、大纲，并构思一个倒叙的吸引人开头。然后，根据大纲逐章编写并润色，最后进行整体修改，完成一篇5000字左右的短篇小说。"
    user_prompt = "写一个关于一个孤独的宇航员在遥远的星球上发现神秘遗迹的故事。先完成故事背景、角色设定、吸引人点等，再编写大纲，最后逐个章写、润色。"
    user_prompt = "写一个关于一个孤独的宇航员在遥远的星球上发现神秘遗迹的故事。先完成故事背景、角色设定、吸引人点等，再编写大纲，最后逐个章写、润色。"

    final_output = agent.run(user_prompt, n_steps=5, verbose=1)
    print(Fore.YELLOW, "\n\nFinal Output:\n\n", final_output)
