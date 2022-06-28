"""DeepLSakubun.py

deepl-sakubunの本体。
DOM操作はDeepLSakubun.execから対象のidと値を返してindex.htmlでやる。
それ以外はここでやる。

"""
from random import randint
from typing import List, Tuple
from Common import Status
from DeepLSakubunFinish import DeepLSakubunFinish
from DeepLSakubunWaitingAnswer import DeepLSakubunWaitingAnswer
from DeepLSakubunWaitingTranslate import DeepLSakubunWaitingTranslate


class DeepLSakubun(DeepLSakubunWaitingAnswer,
                   DeepLSakubunWaitingTranslate, DeepLSakubunFinish):
    """deepl-sakubunの主処理を行う

    index.htmlのハンドラーから画面入力を受け取り、
    状態に応じた処理結果をlabelタグの変更内容として返す。

    (index.html, 初期状態)画面に質問を表示
    ↓
    (ユーザー)テキストエリアに日本語で回答を入力し、決定ボタン押下
    ↓
    (DeepLSakubun)画面の変更内容を出力し、翻訳先言語の回答待ち状態に遷移
    ↓
    (ユーザー)テキストエリアに翻訳先言語で回答を入力し、決定ボタン押下
    ↓
    (DeepLSakubun)DeepLの翻訳APIに質問と入力された日本語回答を結合してPOST
    ↓
    (DeepLSakubun)APIのレスポンスをパースし、画面の変更内容を出力、完了状態へ遷移
    ↓
    (ユーザー)クリアボタン押下
    ↓
    (DeepLSakubun)画面の変更内容を出力、初期状態へ遷移

    Args:
        DeepLSakubunWaitingAnswer:
        DeepLSakubunWaitingTranslate:
        DeepLSakubunFinish:
            それぞれstatusが"WaitingAnswer", "WaitingTranslate", "Finish"の際の
            処理を定義したクラス

    Attributes:
        questions [List[str]]: question.txtから読み出した全ての質問
        question [str]: 現在の質問
        status [Status[Literal
            ["WaitingAnswer", "WaitingTranslate", "Finish"]]]:
            現在の状態。
            "WaitingAnswer": 日本語の回答を待っている
            "WaitingTranslate": 翻訳先言語の回答を待っている
            "Finish": DeepLによる回答を出力し終え、状態クリア待ち
        target_lang [str]: 翻訳先言語。画面で選択したものを受け取る。
        answer_original [str]: ユーザーが画面で入力した日本語の回答
        answer_translated [str]: ユーザーが画面で入力した翻訳先言語の回答
        response [JSON]: DeepL APIのレスポンス
        answer_correct [str]: DeepLによる翻訳結果
        answer_correct_q [str]: DeepLによる翻訳結果の質問部分
        answer_correct_a [str]: DeepLによる翻訳結果の回答部分

    """

    def __init__(self):
        self.questions = self._readQuestionFile()
        self.status = Status("WaitingAnswer")

    def _readQuestionFile(self) -> List[str]:
        try:
            with open("./question.txt", encoding="utf-8") as f:
                return f.readlines()
        except Exception:
            raise Exception

    def chooseAQuestion(self) -> str:
        idx = randint(0, len(self.questions) - 1)
        self.question = self.questions[idx]
        return self.question

    def exec(self, text: str, auth_key: str, language: str, *args) \
            -> Tuple[Tuple[str, str]] | List[Tuple[str, str]]:
        match self.status:
            # 日本語の回答を受け付ける状態
            case Status("WaitingAnswer"):
                newLabels = self._readOriginalAnswer(text)
            # 翻訳先言語の回答を受け付ける状態
            case Status("WaitingTranslate"):
                newLabels = []
                newLabels.append(self._readTranslatedAnswer(text, language))
                for label in self._showCorrectAnswer(auth_key):
                    newLabels.append(label)
                newLabels.append(("btn", "クリア"))
            # 終了後のクリアボタンを押された時
            case Status("Finish"):
                newLabels = self._clear()
            case _:
                raise Exception
        return newLabels
