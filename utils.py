from docx.enum.text import WD_ALIGN_PARAGRAPH 
import re
import sys
from seviye_patterns import *
import string


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
punctuations = string.punctuation + "’" + "‘" + "“" + "”" + "–" + "…" + "»" + "«" + "—" + "–" + "━"

def fix_paragraphs(paragraphs):
    #Fix paranthesis
    fix_paranthesis(paragraphs)

    return paragraphs

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
    if len(runs) < 2:
        return runs
    
    current_run_idx = 0

    for i in range(current_run_idx+1, len(runs)):
        if is_metadata(runs[i]) or \
            has_same_attributes(runs[current_run_idx], runs[i]) or \
                is_space(runs[i].text) or \
                only_punctuations(runs[i].text):
            runs[current_run_idx].text += runs[i].text
            runs[i].text = ""
        else:
            
            #Check whether current run is a metadata. If so, prepend it to the next run
            if is_metadata(runs[current_run_idx]):
                runs[i].text = runs[current_run_idx].text + runs[i].text
                runs[current_run_idx].text = ""


            current_run_idx = i
    
    return runs

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
    trimmed = pro_strip(segment.text).lower()
    trimmed = remove_reference_number(trimmed)
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

def leaves_bend(func):
    """If the functions returns true, set in_madde=False"""
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            args[0].in_bend = False
    
        return result
    return inner

def leaves_alt_bend(func):
    """If the functions returns true, set in_madde=False"""
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            args[0].in_alt_bend = False
    
        return result
    return inner

def is_metadata(run):
    """Checks if the given run is a metadata run"""
    is_bold = get_attribute(run, 'bold')
    covered_with_parantheses = re.fullmatch(r"\(.*\)", pro_strip(run.text)) is not None
    return is_bold and covered_with_parantheses

def only_punctuations(text):
    """Checks if the given text consists of only punctuation"""
    if re.fullmatch(r"[" + re.escape(punctuations) + r"\.,\?!:;]*", text) is None:
        return False
    return True

def only_digits(text):
    """Checks if the given text consists of only digits"""
    text = text.replace("-", "")
    if re.fullmatch(r"[" + re.escape(stupid_spaces) + r"\d]*", text) is None:
        return False
    return True

def remove_reference_number(text):
    """Removes reference number at the end of the text, such as (4)."""
    text = pro_strip(text)
    text = re.sub("\(\d+\)$", "", text)
    return text

def find_nonempty_run(flattened_runs, current_idx):
    """Finds the first nonempty run after the given index"""
    for current_idx in range(current_idx+1, len(flattened_runs)):
        text = flattened_runs[current_idx].text

        if not (text == "" or only_punctuations(text) or only_digits(text)):
            break
    
    return flattened_runs[current_idx]
