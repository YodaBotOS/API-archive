import re
import openai


class StudyNotes:
    PROMPT = "What are {amount} key points I should know when studying {topic}?\n\n1."
    REGEX = re.compile(r"'[0-9]+\. ?(.+)+")

    def __init__(self, openai_token):
        self.openai_token = openai_token

        openai.api_key = openai_token

    async def __call__(self, topic, amount):
        return await self.generate(topic, amount)

    async def generate(self, topic, amount) -> list[str]:
        prompt = self.PROMPT.format(topic=topic, amount=amount)

        response = openai.Completion.create(
            prompt=prompt,
            model="text-davinci-002",
            temperature=0.3,
            max_tokens=400,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

        text = "1. " + response["choices"][0]["text"].strip()

        return self.REGEX.findall(text)
