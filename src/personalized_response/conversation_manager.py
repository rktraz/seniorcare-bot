import time
import os
import sys

# import openai as openai

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)

from context_manager import *
from gpt_chat_client import *
from src.database.database_api import get_context_promt_for_user

# openai.api_key = OPENAI_API_KEY


class ConversationManager:
    def __init__(self, debug=False):
        self.gpt_chat_client = GPTChatClient(debug=debug)
        self.contexts = {}

        people_names = ['Bill']  # Needs to be deriven from the database
        for person_name in people_names:
            prompt = get_context_promt_for_user(person_name)
            self.contexts.update({f"{person_name}GeneralChat": ChatContextManager(f"{person_name.lower()}_general_chat",
                                                                                  base_context_message=prompt,
                                                                                  general_context_restrictions='2H')})

        self.contexts.update({"ReminderInserterChat": ChatContextManager("reminder_inserter_chat",
                                                                         base_context_message=REMINDER_INSERTING_CHAT_PROMPT,
                                                                         general_context_restrictions=0)})

        self.contexts.update({"InContextReminder": ChatContextManager("in_context_reminder",
                                                                      base_context_message=IN_CONTEXT_REMINDER,
                                                                      general_context_restrictions=0)})
        self.debug = debug

    def query(self, user, query):
        return self.__process_gn_part_of_query(user, query)

    def in_context_reminder(self, user, reminder):
        return self.gpt_chat_client.query(reminder, self.contexts["InContextReminder"])

    def add_reminder_to_answer(self, user, reminder):
        question = self.contexts[f"{user}GeneralChat"].conversation[-2]["content"]
        answer = self.contexts[f"{user}GeneralChat"].conversation[-1]["content"]
        request = f"QUESTION:{question}\n ANSWER:{answer}\n REMINDER: {reminder}"

        answer_with_reminder = self.gpt_chat_client.query(request, self.contexts["ReminderInserterChat"])

        self.contexts[f"{user}GeneralChat"].conversation[-1]["content"] = answer_with_reminder

        return answer_with_reminder

    def __process_gn_part_of_query(self, user, message):
        context_key = f"{user}GeneralChat"

        general_chat_response = self.gpt_chat_client.query(message, self.contexts[context_key])
        return general_chat_response


if __name__ == "__main__":
    assistant_manager = ConversationManager(debug=True)

    iteractable_test = False

    print("Conversation starts....")
    while iteractable_test:
        query = input("> ")
        reply = assistant_manager.query("Bill", query)
        print(reply)
    else:
        query = "What is now the weather?"  # "What is my tasks for today?."
        assistant_manager.query("Bill", query)
