from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re
from lxml import html


with open("test_cases/html_exp.html", "r", encoding="utf-8") as f:
    html_text = f.read()

soup = BeautifulSoup(html_text, "html.parser")
li = soup.select_one("li")
first = li.find(True, recursive=False)
print(first.name == "span")


def extract_sentence(html_text: str) -> str:
    tree = html.fromstring(html_text)

    nodes = tree.xpath('//div[@data-test]/node()[not(self::div)]')

    # Convert nodes to string
    parts = []
    for node in nodes:
        if isinstance(node, html.HtmlElement):
            # get only the text inside span (not the tags)
            parts.append(node.text_content())
        else:
            parts.append(str(node))

    # Join everything and clean up whitespace → make it a sentence
    sentence = " ".join(parts)
    sentence = re.sub(r"\s+", " ", sentence).strip()

    return sentence

print(extract_sentence(html_text))