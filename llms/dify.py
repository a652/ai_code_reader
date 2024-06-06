from llms.llm import LLM
import json
import os
from dify_client import ChatClient
from dify_client import CompletionClient


class Dify(LLM):
    def __init__(self, model_name):
        super().__init__(model_name)

        self.api_key = os.environ.get('DIFY_API_KEY')
        # Initialize ChatClient
        self.chat_client = ChatClient(self.api_key)
        self.chat_client.base_url = os.environ.get('DIFY_BASE_URL')
        # Initialize CompletionClient
        self.completion_client = CompletionClient(self.api_key)
        self.completion_client.base_url = os.environ.get('DIFY_BASE_URL')

    def request(self, sys_prompt, user_prompt, stream=False):
        """
        curl -X POST 'https://cloud.dify.ai/v1/chat-messages' \
        --header 'Authorization: Bearer {api_key}' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "inputs": {},
            "query": "What are the specs of the iPhone 13 Pro Max?",
            "response_mode": "streaming",
            "conversation_id": "",
            "user": "abc-123",
            "files": [
            {
                "type": "image",
                "transfer_method": "remote_url",
                "url": "https://cloud.dify.ai/logo/logo-site.png"
            }
            ]
        }'
        """
        query = user_prompt[0][0]
       # print(f'type: {type(query)}, query: {query}')

       # 返回结果
        if stream:
            # Create Chat Message using ChatClient
            chat_response = self.chat_client.create_chat_message(inputs={}, query=query, user="code_reader", response_mode="streaming")
            chat_response.raise_for_status()

            for line in chat_response.iter_lines(decode_unicode=True):
                line = line.split('data:', 1)[-1]
                linestrip = line.strip()
                if linestrip != '' and linestrip is not None:
                    print(linestrip)
                    line = json.loads(linestrip)
                    yield line.get('answer')
        else:
            files = []

            # files = [{
            #     "type": "image",
            #     "transfer_method": "local_file",
            #     "upload_file_id": "your_file_id"
            # }]

            # Create Completion Message using CompletionClient
            completion_response = self.completion_client.create_completion_message(inputs={}, query= query, response_mode="blocking", user="user_id", files=files)
            completion_response.raise_for_status()

            result = completion_response.json()

            #print(result.get('answer'))
            yield result.get('answer')
