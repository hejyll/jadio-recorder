from __future__ import annotations

import enum
from typing import List, Tuple, Union


class ProgramCategory(enum.Enum):
    """Radio program categories.

    Refers to the program categories at https://podcast.1242.com/.
    """

    COMEDY = "お笑い"
    LEISURE = "エンタメ"
    NEWS = "ニュース"
    BUSINESS = "ビジネス"
    ANIMATION = "アニメ"
    MANGA = "漫画"
    GAMES = "ゲーム"
    SPORTS = "スポーツ"
    HEALTH = "健康"
    EDUCATION = "学習"
    PHILOSOPHY = "哲学"
    MUSIC = "音楽"
    KIDS = "キッズ"
    PARENTING = "子育て"
    NONFICTION = "ノンフィクション"
    ARTS = "アート"
    FASHION = "ファッション"
    TECHNOLOGY = "テクノロジー"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def from_value(
        cls,
        value: Union[ProgramCategory, str, List[Union[ProgramCategory, str]]],
    ) -> Union[str, ProgramCategory, List[ProgramCategory]]:
        if isinstance(value, str):
            return cls(value) if cls.has_value(value) else value
        elif isinstance(value, list):
            return [cls.from_value(v) for v in value]
        return value

    def to_itunes_category(self) -> Tuple[str, ...]:
        """
        See: https://podcasters.apple.com/support/1691-apple-podcasts-categories
        """
        return {
            ProgramCategory.COMEDY: ("Comedy",),
            ProgramCategory.LEISURE: ("Leisure",),
            ProgramCategory.NEWS: ("News",),
            ProgramCategory.BUSINESS: ("News", "Business News"),
            ProgramCategory.ANIMATION: ("Leisure", "Animation &amp; Manga"),
            ProgramCategory.MANGA: ("Leisure", "Animation &amp; Manga"),
            ProgramCategory.GAMES: ("Leisure", "Games"),
            ProgramCategory.SPORTS: ("Sports",),
            ProgramCategory.HEALTH: ("Health &amp; Fitness"),
            ProgramCategory.EDUCATION: ("Education",),
            ProgramCategory.PHILOSOPHY: ("Society &amp; Culture", "Philosophy"),
            ProgramCategory.MUSIC: ("Music",),
            ProgramCategory.KIDS: ("Kids &amp; Family",),
            ProgramCategory.PARENTING: ("Parenting",),
            ProgramCategory.NONFICTION: ("Society &amp; Culture", "Documentary"),
            ProgramCategory.ARTS: ("Arts",),
            ProgramCategory.FASHION: ("Arts", "Fashion &amp; Beauty"),
            ProgramCategory.TECHNOLOGY: ("Technology",),
        }
