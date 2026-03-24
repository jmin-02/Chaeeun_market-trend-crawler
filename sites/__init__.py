"""Korean and international news and blog site crawlers.

This module contains crawlers for 30 popular tech news and blog sites
(15 Korean + 15 international). Each crawler is customized for the
specific site's HTML structure.
"""

# Korean site crawlers
from .sites.bloter import BloterCrawler
from .sites.techm import TechMCrawler
from .sites.zdnet_korea import ZDNetKoreaCrawler
from .sites.itworld_korea import ITWorldKoreaCrawler
from .sites.ciokorea import CIOKoreaCrawler
from .sites.b2news import B2NewsCrawler
from .sites.digital_daily import DigitalDailyCrawler
from .sites.herald_tech import HeraldTechCrawler
from .sites.mk_tech import MKTechCrawler
from .sites.hankyung_tech import HankyungTechCrawler
from .sites.the_elec import TheElecCrawler
from .sites.naver_tech import NaverTechCrawler
from .sites.danawa_tech import DanawaTechCrawler
from .sites.brunch_tech import BrunchTechCrawler
from .sites.tistory_tech import TistoryTechCrawler
from .sites.okky import OKKYCrawler

# International site crawlers
from .sites.techcrunch import TechCrunchCrawler
from .sites.the_verge import TheVergeCrawler
from .sites.engadget import EngadgetCrawler
from .sites.wired import WiredCrawler
from .sites.ars_technica import ArsTechnicaCrawler
from .sites.venturebeat import VentureBeatCrawler
from .sites.hacker_news import HackerNewsCrawler
from .sites.medium_tech import MediumTechCrawler
from .sites.readwrite import ReadWriteCrawler
from .sites.gigaom import GigaomCrawler
from .sites.gizmodo import GizmodoCrawler
from .sites.pcmag import PCMagCrawler
from .sites.techradar import TechRadarCrawler
from .sites.mashable import MashableCrawler
from .sites.nextgov import NextgovCrawler

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
