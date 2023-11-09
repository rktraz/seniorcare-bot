from context_manager import *
import g4f

g4f.debug.logging = True # enable logging
g4f.check_version = False # Disable automatic version checking

class GPTChatClient:
    __times_model_used_dict = {model_name: 0 for model_name in MODEL_RATES.keys()}
    __last_time_model_used_dict = {model_name: datetime.now() for model_name in MODEL_RATES.keys()}
    _debug_info = {}
    _debug_prefix_map = {}

    def __init__(self, debug=False):
        self.debug = debug

    def _query_model(self, context, model, openai=None):
        # Query the GPT model
        if not model:
            raise ValueError("Model must be provided.")
        elif model not in MODEL_RATES.keys():
            raise ValueError(f"Model {model} not found. Make sure to update the MODEL_RATES in config file.")

        time_since_last_use = (datetime.now() - GPTChatClient.__last_time_model_used_dict[model]).seconds
        GPTChatClient.__times_model_used_dict[model] -= int(time_since_last_use) // 20

        if GPTChatClient.__times_model_used_dict[model] < 0:
            GPTChatClient.__times_model_used_dict[model] = 0

        if GPTChatClient.__times_model_used_dict[model] >= 3:
            print("Sleeping for 21 seconds to avoid rate limit")
            # Will be removed when paid subscription will be used
            time.sleep(21)
        if model in ["gpt-3.5-turbo", "gpt-4"]:
            response = ""
            while not response:
                try:
                    completion = g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=context, n=1)
                except openai.error.RateLimitError:
                    time.sleep(21)
                    continue

                response = completion['choices'][0]['message']['content']
        else:
            completion = g4f.Completion.create(
                model=model,
                prompt=context[0]["content"] + "\nInput: " + context[1]["content"],
                n=1
            )
            response = completion['choices'][0].text.strip()

        GPTChatClient.__last_time_model_used_dict[model] = datetime.now()
        GPTChatClient.__times_model_used_dict[model] += 1

        return response

    def query(self, message, context_manager, model_name='gpt-3.5-turbo'):

        context_manager.add_to_context("user", message)
        current_context = context_manager.get_context()

        response = self._query_model(current_context, model=model_name)
        context_manager.add_to_context("assistant", response)

        return response
