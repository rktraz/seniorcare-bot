from imports import *
from constants import *


class ChatContextManager:
    def __init__(self, context_file_name,
                 base_context_message, history_file_name=None,
                 general_context_restrictions=-1):

        if history_file_name is None:
            history_file_name = context_file_name.replace(".json", ".log")

        self.context_file = os.path.join(ROOT_DIR, "src", "personalized_response",  CONTEXT_FILES_DIR, context_file_name)
        self.log_file = os.path.join(ROOT_DIR, "src", "personalized_response", LOG_FILES_DIR, history_file_name)
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.context_restrictions = general_context_restrictions
        self.token_limit = TOKEN_LIMIT
        self.max_response_tokens = MAX_RESPONSE_TOKENS
        self.system_message = {"role": "system", "content": base_context_message, "timestamp": "1900-01-01T00:00:00"}
        self.conversation = [self.system_message]

        # If context_file doesn't exist, create it with the system message
        if not os.path.exists(self.context_file):
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json5.dump([self.system_message], f)
        else:  # Otherwise, load the context from file
            with open(self.context_file, 'r', encoding='utf-8') as f:
                self.conversation = json5.load(f)

        # If history_file doesn't exist, create it and add the system message
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(
                    f"{self.system_message['timestamp']}\t{self.system_message['role']}\t{self.system_message['content']}\n")

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo"):
        """Returns the number of tokens used by a list of messages."""
        ALLOWED_MODELS = ["gpt-3.5-turbo", "gpt-4", "babbage-002", "davinci-002"]
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in ALLOWED_MODELS:  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    if key == "timestamp":
                        continue
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
      See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def add_to_context(self, role, message):
        """Add user message to the context and ensure it doesn't exceed token limit."""
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be either 'user' or 'assistant'")

        timestamp = datetime.now().isoformat()
        new_message = {"role": role, "content": message, "timestamp": timestamp}

        self.conversation.append(new_message)

        # Append to history log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{new_message['timestamp']}\t{new_message['role']}\t{new_message['content']}\n")

        conv_history_tokens = self.num_tokens_from_messages(self.conversation)
        while conv_history_tokens + self.max_response_tokens >= self.token_limit:
            del self.conversation[1]
            conv_history_tokens = self.num_tokens_from_messages(self.conversation)

        # Save the updated context to file
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json5.dump(self.conversation, f)

    def get_context(self, custom_context_restrictions=None):
        """Retrieve the current conversation context."""

        without_timestamp = lambda list_: [{k: v for k, v in message.items() if k != 'timestamp'} for message in list_]

        if custom_context_restrictions is None:
            context_restrictions = self.context_restrictions
        else:
            context_restrictions = custom_context_restrictions

        if isinstance(context_restrictions, int):
            if context_restrictions == -1:  # No restrictions, get full context
                pass

            elif context_restrictions == 0:  # No history
                return without_timestamp([self.conversation[0], self.conversation[-1]])

            else:  # Number of queries to track

                if context_restrictions > len(self.conversation):
                    context_restrictions = len(self.conversation)
                elif context_restrictions < 0:
                    raise ValueError("Context restrictions must be a positive integer or -1.")

                return without_timestamp([self.system_message] + self.conversation[-context_restrictions:])

        elif isinstance(context_restrictions, str):  # Format "[NUMBER] H/D/W"

            if not re.match(r"^\d+\s*[MHDW]$", context_restrictions):
                raise ValueError("Invalid format for context_restrictions")

            # Extract the number and time unit
            match = re.match(r'(\d+)\s*([MHDW])', context_restrictions)
            number, unit = int(match.group(1)), match.group(2)

            if number < 0:
                raise ValueError("Invalid number in context_restrictions")

            if unit == "M":
                delta = timedelta(minutes=number)
            elif unit == "H":
                delta = timedelta(hours=number)
            elif unit == "D":
                delta = timedelta(days=number)
            elif unit == "W":
                delta = timedelta(weeks=number)
            else:
                raise ValueError("Invalid time unit in context_restrictions")

            cutoff_time = datetime.now() - delta

            return without_timestamp([message for message in self.conversation if
                                      message["role"] == "system" or
                                      datetime.fromisoformat(message["timestamp"]) >= cutoff_time])

        return without_timestamp(self.conversation)

    def truncate_before_date(self, truncate_date):
        """Truncate conversation before the given date."""
        # Convert string date to a datetime object for comparison
        truncate_datetime = datetime.fromisoformat(truncate_date)

        # Filter messages to keep only those that are newer than the truncate_date and the system message
        self.conversation = [message for message in self.conversation if
                             message["role"] == "system" or
                             datetime.fromisoformat(message["timestamp"]) >= truncate_datetime]

        # Save the updated context to file
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json5.dump(self.conversation, f)
