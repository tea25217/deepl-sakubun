from dataclasses import dataclass
import os
from typing import List, Literal

SERVER_URL_DEV = "http://0.0.0.0:8000/"
SERVER_URL_PROD = "https://deepl-sakubun.an.r.appspot.com/"
SERVER_URL = \
    SERVER_URL_PROD if os.environ.get("GAE_VERSION") else SERVER_URL_DEV
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

LANGUAGE_GROUP = ({
    "group": "QA",
    "languages": ("EN-GB", "EN-US", "JA"),
    "separator": " A."
}, )


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
        def f(g): return language in g["languages"]
        return any(list(map(f, LANGUAGE_GROUP)))
