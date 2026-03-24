"""Korean and international news and blog site crawlers.

This module contains crawlers for 30 popular tech news and blog sites
(15 Korean + 15 international). Each crawler is customized for the
specific site's HTML structure.
"""

# Korean site crawlers
from .bloter import BloterCrawler
from .techm import TechMCrawler
from .zdnet_korea import ZDNetKoreaCrawler
from .itworld_korea import ITWorldKoreaCrawler
from .ciokorea import CIOKoreaCrawler
from .b2news import B2NewsCrawler
from .digital_daily import DigitalDailyCrawler
from .herald_tech import HeraldTechCrawler
from .mk_tech import MKTechCrawler
from .hankyung_tech import HankyungTechCrawler
from .the_elec import TheElecCrawler
from .naver_tech import NaverTechCrawler
from .danawa_tech import DanawaTechCrawler
from .brunch_tech import BrunchTechCrawler
from .tistory_tech import TistoryTechCrawler
from .okky import OKKYCrawler
from .toss_tech import TossTechCrawler
from .woowahan import WoowahanCrawler
from .daangn import DaangnCrawler
from .hwahae import HwahaeCrawler
from .gangnam_unni import GangnamUnniCrawler
from .kakao_tech import KakaoTechCrawler
from .ridi import RidiCrawler
from .kurly import KurlyCrawler

# International site crawlers
from .techcrunch import TechCrunchCrawler
from .the_verge import TheVergeCrawler
from .engadget import EngadgetCrawler
from .wired import WiredCrawler
from .ars_technica import ArsTechnicaCrawler
from .venturebeat import VentureBeatCrawler
from .hacker_news import HackerNewsCrawler
from .medium_tech import MediumTechCrawler
from .readwrite import ReadWriteCrawler
from .gigaom import GigaomCrawler
from .gizmodo import GizmodoCrawler
from .pcmag import PCMagCrawler
from .techradar import TechRadarCrawler
from .mashable import MashableCrawler
from .nextgov import NextgovCrawler

__all__ = [
    # Korean crawlers
    "BloterCrawler",
    "TechMCrawler",
    "ZDNetKoreaCrawler",
    "ITWorldKoreaCrawler",
    "CIOKoreaCrawler",
    "B2NewsCrawler",
    "DigitalDailyCrawler",
    "HeraldTechCrawler",
    "MKTechCrawler",
    "HankyungTechCrawler",
    "TheElecCrawler",
    "NaverTechCrawler",
    "DanawaTechCrawler",
    "BrunchTechCrawler",
    "TistoryTechCrawler",
    "OKKYCrawler",
    "TossTechCrawler",
    "WoowahanCrawler",
    "DaangnCrawler",
    "HwahaeCrawler",
    "GangnamUnniCrawler",
    "KakaoTechCrawler",
    "RidiCrawler",
    "KurlyCrawler",
    # International crawlers
    "TechCrunchCrawler",
    "TheVergeCrawler",
    "EngadgetCrawler",
    "WiredCrawler",
    "ArsTechnicaCrawler",
    "VentureBeatCrawler",
    "HackerNewsCrawler",
    "MediumTechCrawler",
    "ReadWriteCrawler",
    "GigaomCrawler",
    "GizmodoCrawler",
    "PCMagCrawler",
    "TechRadarCrawler",
    "MashableCrawler",
    "NextgovCrawler",
]

# Mapping of site names to crawler classes
KOREAN_CRAWLERS = {
    "Bloter": BloterCrawler,
    "TechM": TechMCrawler,
    "ZDNet Korea": ZDNetKoreaCrawler,
    "ITWorld Korea": ITWorldKoreaCrawler,
    "CIO Korea": CIOKoreaCrawler,
    "B2News": B2NewsCrawler,
    "Digital Daily": DigitalDailyCrawler,
    "Herald Tech": HeraldTechCrawler,
    "MK Tech": MKTechCrawler,
    "Hankyung Tech": HankyungTechCrawler,
    "The Elec": TheElecCrawler,
    "Naver Tech": NaverTechCrawler,
    "Danawa Tech": DanawaTechCrawler,
    "Brunch Tech": BrunchTechCrawler,
    "Tistory Tech": TistoryTechCrawler,
    "OKKY": OKKYCrawler,
    "Toss Tech": TossTechCrawler,
    "Woowahan": WoowahanCrawler,
    "Daangn": DaangnCrawler,
    "Hwahae": HwahaeCrawler,
    "Gangnam Unni": GangnamUnniCrawler,
    "Kakao Tech": KakaoTechCrawler,
    "Ridi": RidiCrawler,
    "Kurly": KurlyCrawler,
}

INTERNATIONAL_CRAWLERS = {
    "TechCrunch": TechCrunchCrawler,
    "The Verge": TheVergeCrawler,
    "Engadget": EngadgetCrawler,
    "Wired": WiredCrawler,
    "Ars Technica": ArsTechnicaCrawler,
    "VentureBeat": VentureBeatCrawler,
    "Hacker News": HackerNewsCrawler,
    "Medium Tech": MediumTechCrawler,
    "ReadWrite": ReadWriteCrawler,
    "Gigaom": GigaomCrawler,
    "Gizmodo": GizmodoCrawler,
    "PCMag": PCMagCrawler,
    "TechRadar": TechRadarCrawler,
    "Mashable": MashableCrawler,
    "Nextgov": NextgovCrawler,
}

# Combined mapping of all crawlers
ALL_CRAWLERS = {**KOREAN_CRAWLERS, **INTERNATIONAL_CRAWLERS}
