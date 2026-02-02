from bs4 import BeautifulSoup
import re

def extract_span_value(li_tag):
    span = li_tag.find("span")
    if not span: return None

    text = span.get_text(strip=True)
    if re.match(r'^\d[AB]$', text, re.I): return text.upper()
    if re.match(r'^\d+%$', text): return int(text.replace("%", ""))
    return None

def check_logic_type(rule):
    if "not" in rule:
        return "NOT"
    elif "all of" in rule or "completed the following" in rule or "enrolled in the following" in rule or "each of" in rule:
        return "AND"
    elif "at least" in rule or "1 of" in rule or "enrolled in" in rule:
        return "OR"
    
    return None

def link_to_rule(code, link, grade = None):
    if "/courses/view" in link and grade:
        return { "type": "GRADE", "grade": grade, "code":  code }
    elif "/courses/view" in link:
        return { "type": "COURSE", "code": code }
    elif "/programs/view" in link:
        return { "type": "PROGRAM", "code": code }
    
    raise ValueError("Unidentified link")


# return [n.Node]
def parse_prereq(ul):
    children = ul.find_all(recursive=False)
    res = []

    for child in children:
        if child.name == "li" and child.has_attr("data-test"):
            obj = re.compile(r"<div data-test.*?>\s*<div>")
            res = obj.search(str(child))
            rule = " ".join(child.stripped_strings)

            courses_or_programs = []

            if res: #<div data-test="..."><div> Not completely nor concurrently enrolled in: MATH125
                pass
            else:
                logic_type = check_logic_type(rule)

                grade = None
                if "level" in rule:
                    return { "type": "LEVEL", "level": extract_span_value(child) }
                elif "grade" in rule:
                    grade = extract_span_value(child)

                links = child.find_all("a", href = True)
                for a in links:
                    code = a.get_text(strip=True)
                    link = a.get("href", "")
                    courses_or_programs.append(link_to_rule(code, link, grade=grade))

                if logic_type:
                    res.append({ "type": logic_type, "items": courses_or_programs})
                else: 
                    res.append({ "type": "OTHER", "content": rule})
            

        else: # child.name == "li" or <div><span></span>
            inner_li = child.find("li")
            rule = inner_li.find("span").get_text(strip=True)
            logic_type = check_logic_type(rule)
            inner_ul = inner_li.find("ul")
            res.append( { "type": logic_type, "items": parse_prereq(inner_ul)} )

    return res

            