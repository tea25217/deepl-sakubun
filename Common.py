from dataclasses import dataclass
from typing import List, Literal

SERVER_URL_DEV = "http://0.0.0.0:8000/"
SERVER_URL_PROD = "https://deepl-sakubun.an.r.appspot.com/"
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
FRONT_URL_PROD = "https://tea25217.github.io/deepl-sakubun/"

LANGUAGES = (
    ("EN-GB", "英語（イギリス）"),
    ("EN-US", "英語（アメリカ）"),
    ("BG", "ブルガリア語"),
    ("CS", "チェコ語"),
    ("DA", "デンマーク語"),
    ("DE", "ドイツ語"),
    ("EL", "ギリシア語"),
    ("ES", "スペイン語"),
    ("ET", "エストニア語"),
    ("FI", "フィンランド語"),
    ("FR", "フランス語"),
    ("HU", "ハンガリー語"),
    ("ID", "インドネシア語"),
    ("IT", "イタリア語"),
    ("JA", "日本語"),
    ("LT", "リトアニア語"),
    ("LV", "ラトビア語"),
    ("NL", "オランダ語"),
    ("PL", "ポーランド語"),
    ("PT-PT", "ポルトガル語"),
    ("PT-BR", "ポルトガル語（ブラジル）"),
    ("RO", "ルーマニア語"),
    ("RU", "ロシア語"),
    ("SK", "スロバキア語"),
    ("SL", "スロベニア語"),
    ("SV", "スウェーデン語"),
    ("TR", "トルコ語"),
    ("ZH", "中国語"),
)

LANGUAGE_GROUP = ({
    "group": "A",
    "languages": ("EN-GB", "EN-US", "CS", "DE", "DA", "JA"),
    "separator": " A."
},)


@dataclass(slots=True)
class Status:
    """DeepLSakubunクラスが取る状態

    WaitingAnswer -> WaitingTranslate -> Finish -> WaitingAnswer
    のサイクルで遷移する
    (3状態の決定性有限オートマトン)

    """
    name: Literal["WaitingAnswer", "WaitingTranslate", "Finish"]


class Language:
    """言語の種類に絡む処理
    """

    def getSeparatorFromLanguage(language: str) -> str | None:
        for g in LANGUAGE_GROUP:
            if language in g["languages"]:
                return g["separator"]
        return None

    def getLanguagesFromSeparatorGroup(separatorGroup: str) -> List[str]:
        for g in LANGUAGE_GROUP:
            if separatorGroup == g["group"]:
                return g["languages"]
        return []

    def canSeparate(language: str) -> bool:

        def f(g):
            return language in g["languages"]

        return any(list(map(f, LANGUAGE_GROUP)))


class Location:
    """URLから環境を判定する
    """

    def getServerURL() -> str:
        from js import window

        hostname = window.location.hostname
        if hostname in FRONT_URL_PROD:
            return SERVER_URL_PROD
        else:
            return SERVER_URL_DEV
