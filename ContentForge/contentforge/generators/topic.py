"""Mechanika 3: Generowanie treści z ogólnego tematu."""

from .base import BaseGenerator


class TopicGenerator(BaseGenerator):
    """Generator treści na podstawie ogólnego tematu — większa swoboda kreatywna."""

    def generate_brief(self, **kwargs) -> str:
        topic = kwargs.get("topic", "")
        if not topic:
            raise ValueError("Wymagany temat (topic)")

        user_prompt = self.build_prompt("topic.txt", topic=topic)
        return self.get_full_prompt(user_prompt)
