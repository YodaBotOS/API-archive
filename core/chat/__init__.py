import json

import openai


class Chat:
    PROMPT = """
The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.
Human: Hello, who are you?
AI: I am a bot.
Human: Who are you?
AI: I am a bot.
"""

    EXPIRE_AFK = 3 * 60  # 3 minutes expiration

    def __init__(self, openai_token, redis):
        self.openai_token = openai_token
        self.redis = redis

        self.prompt = self.PROMPT

        openai.api_key = openai_token

    @staticmethod
    def gen_prompt(prompt, next):
        p = ""

        for who, content in prompt:
            content = content.replace("\n", " ").strip()

            p += f"{who}: {content}\n{next}: "

        p = p.strip()

        return p

    async def get(self, job_id, default=None):
        rjs = await self.redis.get(job_id)

        if rjs is None:
            return default

        js = json.loads(rjs)

        if js and rjs and js['status'] != 'stopped':
            return js

        return default

    async def set(self, job_id, js, *, ex=None, force=False):
        if not force and not await self.job_id_present(job_id):
            raise ValueError("Job ID does not exist, stopped or has expired (3 minutes passed).")

        ex = ex or self.EXPIRE_AFK

        await self.redis.set(job_id, json.dumps(js), ex=ex, keepttl=False)

        return js

    async def delete(self, job_id):
        if not await self.job_id_present(job_id):
            raise ValueError("Job ID does not exist, stopped or has expired (3 minutes passed).")

        await self.redis.delete(job_id)

    async def job_id_present(self, job_id):
        res = await self.get(job_id)

        present = res is not None

        return present

    async def start(self, job_id):
        if await self.job_id_present(job_id):
            raise ValueError("Job ID already exists.")

        js = {
            'status': 'running',
            'job_id': job_id,
            'messages': [],
            'custom': False,
            'custom_prompt': None,
        }

        await self.set(job_id, js, force=True)

        js['status'] = 'started'

        return js

    async def custom_start(self, job_id, prompt):
        if await self.job_id_present(job_id):
            raise ValueError("Job ID already exists.")

        js = {
            'status': 'running',
            'job_id': job_id,
            'messages': [],
            'custom': True,
            'custom_prompt': prompt,
        }

        await self.set(job_id, js, force=True)

        js['status'] = 'started'

        return js

    async def stop(self, job_id):
        if not await self.job_id_present(job_id):
            raise ValueError("Job ID does not exist, stopped or has expired (3 minutes passed).")

        js = await self.get(job_id)
        js['status'] = 'stopped'

        await self.delete(job_id)

        return js

    async def respond(self, job_id, message):
        if not await self.job_id_present(job_id):
            raise ValueError("Job ID does not exist, stopped or has expired (3 minutes passed).")

        js = await self.get(job_id)

        js['messages'].append(("Human", message))

        js = await self.ai_respond(job_id, js)

        await self.set(job_id, js)

    async def ai_respond(self, job_id, js):
        messages = js['messages']

        if js['custom']:
            prompt = js['custom_prompt']
        else:
            prompt = self.prompt

        prompt = prompt or self.PROMPT

        prompt = self.gen_prompt(prompt, "AI: ")

        response = openai.Completion.create(
            prompt=prompt,
            model="text-davinci-002",
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:", "Human:", "AI:"],
        )

        ai_resps = response["choices"][0]["text"].strip()

        ai_resps = ai_resps or "Sorry, I did not understand."

        if not ai_resps:
            ai_resps = "Sorry, I did not understand."

        messages.append(("AI", ai_resps))

        return js
