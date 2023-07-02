from enum import Enum
from utils import get_attribute
import re

class SegmentType(Enum):
    ANA_BASLIK      = 0     #Ana Başlık
    MEVZUAT_BILGI   = 1     #Mevzuat Bilgi
    BOLUM_BASLIK    = 2     #Bölüm Başlıkları
    ALT_BASLIK      = 3     #Alt Başlıklar
    MADDE_BASLIK    = 4     #Madde Başlık
    FOOTNOTE        = 5     #Footnote
    IGNORE          = 6     #Ignore
    TABLE           = 7     #Table
    MADDE_METADATA  = 8     #Madde metadata
    FREE_TEXT       = 9     #Free text
    SEVIYE_0        = 10    #Seviye-#
    SEVIYE_1        = 11    #Seviye-#
    SEVIYE_2        = 12    #Seviye-#
    SEVIYE_3        = 13    #Seviye-#
    SEVIYE_4        = 14    #Seviye-#
    SEVIYE_5        = 15    #Seviye-#
    SEVIYE_6        = 16    #Seviye-#
    SEVIYE_7        = 17    #Seviye-#
    SEVIYE_8        = 18    #Seviye-#


segment2idx = {segment.name: segment.value for segment in SegmentType}

class SegmentClassifier:
    
    def __init__(self, flattened_runs):
        self.in_madde = False
        self.seviye = 0
        self.seviye_classes = []
        self.first_header = False   

        self.current_segment = None
        self.parag_idx = -1
        self.run_idx = -1
        
        self.flattened_runs = flattened_runs
        self.current_run_count = -1

    def classify_next(self, segment, parag_idx, run_idx):
        self.current_segment = segment
        self.parag_idx = parag_idx
        self.run_idx = run_idx

        self.current_run_count += 1

        if self.classify_ignore(): return SegmentType.IGNORE
        if self.classify_ana_baslik(): return SegmentType.ANA_BASLIK
        if self.classify_mevzuat_bilgi(): return SegmentType.MEVZUAT_BILGI
        if self.classify_bolum_baslik(): return SegmentType.BOLUM_BASLIK
        if self.classify_madde_baslik(): return SegmentType.MADDE_BASLIK
        if self.classify_alt_baslik(): return SegmentType.ALT_BASLIK
        if self.classify_seviye(): return SegmentType.SEVIYE_0
        if self.classify_footnote(): return SegmentType.FOOTNOTE
        if self.classify_table(): return SegmentType.TABLE
        if self.classify_madde_metadata(): return SegmentType.MADDE_METADATA
        if self.classify_free_text(): return SegmentType.FREE_TEXT


    def leaves_madde(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)

            if result:
                args[0].in_madde = False
        
            return result

        return inner

    def classify_ana_baslik(self):
        if not self.first_header and \
            get_attribute(self.current_segment, "alignment") == "center" and \
            get_attribute(self.current_segment, 'bold'):
            
            self.first_header = True
            return True

    def classify_mevzuat_bilgi(self):
        return False
    
    @leaves_madde
    def classify_bolum_baslik(self):
        is_centered = get_attribute(self.current_segment, "alignment") == "center"
        is_bold = get_attribute(self.current_segment, 'bold')
        
        return self.first_header and is_centered and is_bold

    def classify_madde_metadata(self):
        is_bold = get_attribute(self.current_segment, 'bold')

        return self.in_madde and is_bold

    @leaves_madde
    def classify_alt_baslik(self):
        is_bold = get_attribute(self.current_segment, 'bold')

        if self.current_segment.text == "Netice sebebiyle ağırlaşmış suç":
            print("Next run:", self.flattened_runs[self.current_run_count + 1].text)
            print("Second run:", self.flattened_runs[self.current_run_count + 2].text)
            print("Third run:", self.flattened_runs[self.current_run_count + 3].text)

        next_is_madde_baslik = self.includes_madde(self.flattened_runs[self.current_run_count + 1])

        return self.first_header and is_bold and next_is_madde_baslik

    def classify_madde_baslik(self):
        is_first = self.run_idx == 0
        is_bold = get_attribute(self.current_segment, 'bold')

        includes_madde = self.includes_madde(self.current_segment)

        if is_first and is_bold and includes_madde:
            self.in_madde = True
            return True
        
        return False
    
    def includes_madde(self, segment):
        trimmed = segment.text.strip().lower()
        madde_pattern = re.compile(r'madde \d+')    
        includes_madde = madde_pattern.search(trimmed) is not None
        return includes_madde

    @leaves_madde
    def classify_footnote(self):
        return False

    def classify_seviye(self):
        not_bold = not get_attribute(self.current_segment, 'bold')

        altMaddeRegex = [
            [re.compile(r'^[^\wığüşöç]*\(\d+\)')],  # (1), (2), (3) etc.
            [re.compile(r'^[^\wığüşöç(]*[a-zığüşöç]\)')],  # a), b), c) etc.
            [re.compile(r'^[^\wığüşöç(]*\d+\)')],  # 1), 2), 3) etc.
            [re.compile(r'^[^\wığüşöç(]*[a-zığüşöç][a-zığüşöç]\)')],  # aa), bb), cc) etc.
            [re.compile(r'^[^\wığüşöç]*\([a-zığüşöç]\)')],  # (a), (b), (c) etc.
            [re.compile(r'^[^\wığüşöç]*\([a-zığüşöç][a-zığüşöç]\)')]  # (aa), (bb), (cc) etc.
        ]
        
        return self.in_madde and not_bold
    
    @leaves_madde
    def classify_table(self):
        #Allaha emanet
        pass
    
    @leaves_madde
    def classify_free_text(self):
        return True

    def classify_ignore(self):
        pattern = r"^[^a-zA-Z0-9]+$" # match any non-alphanumeric character
        matches = re.search(pattern, self.current_segment.text)
        if matches:
            return True

