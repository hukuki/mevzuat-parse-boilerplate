from docx.enum.text import WD_ALIGN_PARAGRAPH 
import re
import sys
from seviye_patterns import *


alignment_dict = {
    WD_ALIGN_PARAGRAPH.RIGHT: "right",
    WD_ALIGN_PARAGRAPH.LEFT: "left",
    WD_ALIGN_PARAGRAPH.CENTER: "center",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
    WD_ALIGN_PARAGRAPH.DISTRIBUTE: "distribute",
    None: "left"
} 

_s = ''.join(chr(c) for c in range(sys.maxunicode+1))
stupid_spaces = ''.join(re.findall(r'\s', _s))

def fix_paragraphs(paragraphs):
    #Remove empty paragraphs
    remove_empty_paragraphs(paragraphs)

    #Fix paranthesis
    fix_paranthesis(paragraphs)

    return paragraphs

def remove_empty_paragraphs(paragraphs):
    for i in reversed(range(len(paragraphs))):
        if paragraphs[i].text == "" or is_space(paragraphs[i].text):
            paragraphs.pop(i)

def is_metadata(run):
    is_bold = get_attribute(run, 'bold')
    covered_with_parantheses = re.fullmatch(r"\(.*\)", pro_strip(run.text)) is not None
    return is_bold and covered_with_parantheses

def get_attribute(run, attribute):
    if attribute == "alignment":
        return alignment_dict[run._parent.alignment]
    
    else:
        if getattr(run, attribute) != None:
            return getattr(run, attribute)
        elif getattr(run.font, attribute) != None:
            return getattr(run.font, attribute)
        elif run.style != None and getattr(run.style.font, attribute) != None:
            return getattr(run.style.font, attribute)
        else:
            return not not getattr(run._parent.style.font, attribute)
        
def is_space(text):
    """Checks if the given text consists of only spaces (including stupid ones)"""
    if re.fullmatch("[" + re.escape(stupid_spaces) + "]*", text) is None:
        return False
    return True

def merge_runs(runs):
    merged_runs = []

    current_run = None
    #Find a nonempty run to start with
    for i, run in enumerate(runs):
        if run.text and not is_space(run.text):
            current_run = run
            runs = runs[i:]
            break

    for run in runs[1:]:
        if is_metadata(run) or has_same_attributes(current_run, run) or is_space(run.text):
            #Merge
            current_run.text += run.text
        else:
            #do not merge
            merged_runs.append(current_run)
            
            current_run = run
    
    merged_runs.append(current_run)
    return merged_runs

def fix_paranthesis(paragraphs):
    for paragraph in paragraphs:
        for i in range(len(paragraph.runs)):
            text = pro_strip(paragraph.runs[i].text)

            if text.startswith(")"):
                paragraph.runs[i-1].text += ")" #append to previous run
                paragraph.runs[i].text = text[1:]
            
            if text.endswith("("):
                paragraph.runs[i+1].text = "(" + paragraph.runs[i+1].text #prepend to next run
                paragraph.runs[i].text = text[:-1]

def has_same_attributes(run1, run2):
    return (get_attribute(run1, 'italic') == get_attribute(run2, 'italic')and \
            get_attribute(run1, 'bold') == get_attribute(run2, 'bold') and \
            get_attribute(run1, 'alignment') == get_attribute(run2, 'alignment'))

def pro_strip(text):
    """.strip function that we need"""
    return text.strip(stupid_spaces)

def includes_madde(segment):
    """Looks for the pattern 'madde \d+'"""
    trimmed = segment.text.strip().lower()
    madde_pattern = re.compile(r'madde')    
    includes_madde = madde_pattern.search(trimmed) is not None
    return includes_madde

def leaves_madde(func):
    """If the functions returns true, set in_madde=False"""
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            args[0].in_madde = False
    
        return result
    return inner

def covered_with_parenthesis(segment):
    """Looks for the pattern '(.*($'"""
    trimmed = pro_strip(segment.text).lower()
    ends_with_parrentesis = re.fullmatch(r".*\)", trimmed) is not None
    return ends_with_parrentesis

def is_metadata(run):
    """Checks if the given run is a metadata run"""
    is_bold = get_attribute(run, 'bold')
    covered_with_parantheses = re.fullmatch(r"\(.*\)", pro_strip(run.text)) is not None
    return is_bold and covered_with_parantheses