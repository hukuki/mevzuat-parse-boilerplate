from enum import Enum
from utils import (get_attribute, leaves_madde, includes_madde, 
                   pro_strip, only_punctuations, only_digits, 
                   leaves_bend, remove_reference_number, find_nonempty_run,
                   leaves_alt_bend)
import re
from seviye_patterns import *

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
    FIKRA_SONU      = 12    #Fıkra Sonu
    METADATA        = 13    #Metadata
    DEBUG           = 14    #Debug



segment2idx = {segment.name: segment.value for segment in SegmentType}

class SegmentClassifier:
    
    def __init__(self, flattened_runs):
        self.in_madde = False
        self.in_bend = False
        self.in_alt_bend = False
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
    
    @leaves_alt_bend
    @leaves_bend
    def classify_bolum_baslik(self):
        is_centered = get_attribute(self.current_segment, "alignment") == "center"
        
        return is_centered

    @leaves_alt_bend
    @leaves_bend
    @leaves_madde
    def classify_alt_baslik(self):
        text = remove_reference_number(self.current_segment.text)

        is_italic = get_attribute(self.current_segment, 'italic')
        ends_with_colon = pro_strip(text).endswith(':')
        
        #Check if next segment is madde_baslik
        next_nonempty_run = find_nonempty_run(self.flattened_runs, self.current_run_count)
        next_is_madde_baslik = includes_madde(next_nonempty_run)

        return is_italic and next_is_madde_baslik and ends_with_colon

    @leaves_alt_bend
    @leaves_bend
    def classify_madde_baslik(self):
        is_bold = get_attribute(self.current_segment, 'bold')

        inc_madde = includes_madde(self.current_segment)

        if is_bold and inc_madde:
            self.in_madde = True
            return True
        
        return False

    def classify_footnote(self):
        is_italic = get_attribute(self.current_segment, 'italic')
        starts_with_list_pattern = (bool(re.match(r'^\(\d+\)', pro_strip(self.current_segment.text)))
                                    or bool(re.match(r'^[a-z] -', pro_strip(self.current_segment.text))))

        return is_italic and starts_with_list_pattern

    def classify_seviye(self):
        text = pro_strip(self.current_segment.text)
        bold = get_attribute(self.current_segment, 'bold')
        italic = get_attribute(self.current_segment, 'italic')
        
        bend_match = bend_pattern.match(text)
        alt_bend_match = alt_bend_pattern.match(text)
        
        if italic or bold or not self.in_madde:
            return False
        elif alt_bend_match:
            self.in_alt_bend = True
            return SegmentType.ALT_BEND
        elif bend_match:
            self.in_bend = True
            return SegmentType.BEND
        elif self.in_alt_bend:
            return SegmentType.ALT_BEND
        elif self.in_bend:
            return SegmentType.BEND
        else:
            return SegmentType.FIKRA
        
    def classify_table(self):
        #Allaha emanet
        pass
    
    def classify_free_text(self):
        return True

