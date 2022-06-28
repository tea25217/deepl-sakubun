from dataclasses import dataclass
from typing import List, Literal

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
