from docx.enum.text import WD_ALIGN_PARAGRAPH 


alignment_dict = {
    WD_ALIGN_PARAGRAPH.RIGHT: "right",
    WD_ALIGN_PARAGRAPH.LEFT: "left",
    WD_ALIGN_PARAGRAPH.CENTER: "center",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
    None: "left"
} 

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