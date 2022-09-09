import openai

class GrammarCorrection:
    PROMPT = "Correct this to standard English:\n\n"

    def __init__(self, openai_token):
        self.openai_token = openai_token

        openai.api_key = openai_token

    async def __call__(self, text):
        return await self.correct(text)

    async def correct(self, text):
        prompt = self.PROMPT + text

        response = openai.Completion.create(
            prompt=prompt,
            model="text-davinci-002",
            temperature=0,
            max_tokens=400,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

        return response["choices"][0]["text"].strip()
