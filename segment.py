from enum import Enum

class SegmentType(Enum):

    ANA_BASLIK      = 0    #Ana Başlık
    MEVZUAT_BILGI   = 1         #Mevzuat Bilgi
    BOLUM_BASLIK    = 2       #Bölüm Başlıkları
    ALT_BASLIK      = 3        #Alt Başlıklar
    MADDE_BASLIK    = 4       #Madde Başlık
    FOOTNOTE        = 5     #Footnote
    IGNORE          = 6    #Ignore
    SEVIYE          = 7    #Seviye-#
    TABLE           = 8    #Table
    MADDE_METADATA  = 9    #Madde metadata
    FREE_TEXT       = 10    #Free text