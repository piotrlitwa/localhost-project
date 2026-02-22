"""Formatter Medium."""

from .base import BaseFormatter, FormattedContent
from ..models import Platform


class MediumFormatter(BaseFormatter):
    platform = Platform.MEDIUM
    template_file = "medium.txt"

    def parse_response(self, response: str) -> FormattedContent:
        subtitle = self._extract_field(response, "SUBTITLE")
        body = self._extract_content(response)
        if subtitle:
            body = f"*{subtitle}*\n\n{body}"

        return FormattedContent(
            platform=self.platform,
            title=self._extract_field(response, "TITLE"),
            body=body,
            hashtags=self._extract_field(response, "HASHTAGS"),
        )
