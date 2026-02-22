"""Formatter X/Twitter."""

from .base import BaseFormatter, FormattedContent
from ..models import Platform


class TwitterFormatter(BaseFormatter):
    platform = Platform.TWITTER
    template_file = "twitter.txt"

    def parse_response(self, response: str) -> FormattedContent:
        return FormattedContent(
            platform=self.platform,
            title=self._extract_field(response, "TITLE"),
            body=self._extract_content(response),
            hashtags=self._extract_field(response, "HASHTAGS"),
        )
