from enum import Enum
from utils import get_attribute, leaves_madde, includes_madde, pro_strip, only_punctuations, only_digits
import re

class SegmentType(Enum):
    ANA_BASLIK      = 0     #Ana Başlık
    MEVZUAT_BILGI   = 1     #Mevzuat Bilgi
    BOLUM_BASLIK    = 2     #Bölüm Başlıkları
    ALT_BASLIK      = 3     #Alt Başlıklar
    MADDE_BASLIK    = 4     #Madde Başlık
    FOOTNOTE        = 5     #Footnote
    TABLE           = 6     #Table
    FREE_TEXT       = 7     #Free text
    FIKRA           = 8     #Fıkra
    BEND            = 9    #Bend
    ALT_BEND        = 10    #Alt Bend
    ALT_ALT_BEND    = 11    #Alt Alt Bend
    FIKRA_SONU      = 13    #Fıkra Sonu
    DEBUG           = 12    #Debug


segment2idx = {segment.name: segment.value for segment in SegmentType}

class SegmentClassifier:
    
    def __init__(self, flattened_runs):
        self.in_madde = False
        self.current_segment = None
        self.flattened_runs = flattened_runs
        self.current_run_count = -1

    def classify_next(self, segment):
        self.current_segment = segment
        self.current_run_count += 1

        if self.check_ignore(): return None
        if self.classify_ana_baslik(): return SegmentType.ANA_BASLIK
        if self.classify_mevzuat_bilgi(): return SegmentType.MEVZUAT_BILGI
        if self.classify_bolum_baslik(): return SegmentType.BOLUM_BASLIK
        if self.classify_madde_baslik(): return SegmentType.MADDE_BASLIK
        if self.classify_alt_baslik(): return SegmentType.ALT_BASLIK
        if self.classify_seviye(): return self.classify_seviye()
        if self.classify_footnote(): return SegmentType.FOOTNOTE
        if self.classify_table(): return SegmentType.TABLE
        if self.classify_free_text(): return SegmentType.FREE_TEXT

    def check_ignore(self):
        text = pro_strip(self.current_segment.text)

        if text == "":
            return True
        elif only_punctuations(text):
            return True
        elif only_digits(text):
            return True
        else:
            return False
        
    def classify_ana_baslik(self):
        return False
    
    def classify_mevzuat_bilgi(self):
        return False
    
    @leaves_madde
    def classify_bolum_baslik(self):
        is_centered = get_attribute(self.current_segment, "alignment") == "center"
        is_bold = get_attribute(self.current_segment, 'bold')
        
        return is_centered and is_bold

    @leaves_madde
    def classify_alt_baslik(self):
        is_bold = get_attribute(self.current_segment, 'bold')

        next_is_madde_baslik = includes_madde(self.flattened_runs[self.current_run_count + 1])

        return is_bold and next_is_madde_baslik

    def classify_madde_baslik(self):
        is_bold = get_attribute(self.current_segment, 'bold')

        inc_madde = includes_madde(self.current_segment)

        if is_bold and inc_madde:
            self.in_madde = True
            return True
        
        return False

    @leaves_madde
    def classify_footnote(self):
        return False

    def classify_seviye(self):
        bold = get_attribute(self.current_segment, 'bold')
        text = pro_strip(self.current_segment.text)
        
        if bold and not self.in_madde:
            return False
        
        #Define list patterns here
        fikra_pattern =  re.compile(r"^\(\d+\)")
        bend_pattern = re.compile(r"^[a-z]\)")
        alt_bend_pattern = re.compile(r"^\d+\.")

        if fikra_pattern.match(text):
            return SegmentType.FIKRA
        elif bend_pattern.match(text):
            return SegmentType.BEND
        elif alt_bend_pattern.match(text):
            return SegmentType.ALT_BEND
        else:
            return SegmentType.FIKRA_SONU
        
    @leaves_madde
    def classify_table(self):
        #Allaha emanet
        pass
    
    @leaves_madde
    def classify_free_text(self):
        return True

