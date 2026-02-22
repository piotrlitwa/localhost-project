"""Formatter LinkedIn/Facebook."""

from .base import BaseFormatter, FormattedContent
from ..models import Platform


class LinkedInFormatter(BaseFormatter):
    platform = Platform.LINKEDIN
    template_file = "linkedin.txt"

    def parse_response(self, response: str) -> FormattedContent:
        return FormattedContent(
            platform=self.platform,
            title=self._extract_field(response, "TITLE"),
            body=self._extract_content(response),
            hashtags=self._extract_field(response, "HASHTAGS"),
        )
