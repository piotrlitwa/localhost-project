"""Formatter WordPress blog."""

from .base import BaseFormatter, FormattedContent
from ..models import Platform


class BlogFormatter(BaseFormatter):
    platform = Platform.BLOG
    template_file = "blog.txt"

    def parse_response(self, response: str) -> FormattedContent:
        meta = self._extract_field(response, "META_DESCRIPTION")
        body = self._extract_content(response)
        if meta:
            body = f"<!-- META: {meta} -->\n\n{body}"

        return FormattedContent(
            platform=self.platform,
            title=self._extract_field(response, "TITLE"),
            body=body,
            hashtags=self._extract_field(response, "HASHTAGS"),
        )
