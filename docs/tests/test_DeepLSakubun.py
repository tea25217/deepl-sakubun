"""DeepLSakubunモジュールテスト

現段階で粒度の細かいテストを増やしてもテストコードが即寿命を迎えかねないので、
モジュールの入出力をざっくりと確認する。

"""
import os
from typing import Tuple
import pytest
import docs.DeepLSakubun as DeepLSakubun

TRANSLATED_ANSWER = "Q. QQQQQQQQ A. AAAAAAAA"
TRANSLATED_ANSWER_Q = "Q. QQQQQQQQ"
TRANSLATED_ANSWER_A = " A. AAAAAAAA"
NEW_TRANSLATED_ANSWER = "Q. PPPPPPPP A. BBBBBBBB"
NEW_TRANSLATED_ANSWER_Q = "Q. PPPPPPPP"
NEW_TRANSLATED_ANSWER_A = " A. BBBBBBBB"


def mock_callAPI(self, param: dict[str, str | dict[str, str]]) -> None:
    os.getenv("TRANSLATED_ANSWER")
    res = {"translations": [{"text": os.getenv("TRANSLATED_ANSWER")}]}
    self.response = res


# _callAPIの引数確認用
def mock_showCorrectAnswer(self, auth_key: str) -> Tuple[Tuple[str, str]]:
    if not auth_key:
        raise Exception
    param = self._generateParam(auth_key)
    # paramを保持できるようにする
    self.param = param
    self._callAPI(param)

    return self._decideToSplitAnswer()


@pytest.fixture
def deepLSakubun(monkeypatch) -> DeepLSakubun:
    monkeypatch.setattr(
        "docs.DeepLSakubun.DeepLSakubun._callAPI", mock_callAPI)
    monkeypatch.setenv("TRANSLATED_ANSWER", TRANSLATED_ANSWER)

    deepLSakubun = DeepLSakubun.DeepLSakubun()
    deepLSakubun.chooseAQuestion()
    yield deepLSakubun
    poststate = \
        [(k, v) for k, v in deepLSakubun.__dict__.items() if k != "questions"]
    print(poststate)


@pytest.fixture
def appWaitingTranslate(deepLSakubun, default_input):
    deepLSakubun.onClick(*default_input)
    return deepLSakubun


@pytest.fixture
def default_input() -> Tuple[str]:
    return ("なんか気の利いた回答", "XXXX", "EN-GB")


@pytest.fixture
def default_input_translated() -> Tuple[str]:
    return ("Some smart answer", "XXXX", "EN-GB")


def loop_status(deepLSakubun, any_input):
    [deepLSakubun.onClick(*any_input) for _ in range(3)]


class Test_DeepLSakubun__init__:

    def test_インスタンス生成できて_必要なインスタンス変数があること(self):
        instance = DeepLSakubun.DeepLSakubun()
        assert len(instance.questions) > 1
        assert instance.status == DeepLSakubun.Status("WaitingAnswer")

    def test_chooseAQuestionでランダムに質問を取得できること(self):
        instance = DeepLSakubun.DeepLSakubun()
        assert instance.chooseAQuestion()
        assert instance.question

        old_question = instance.question
        for _ in range(100):
            new_question = instance.chooseAQuestion()
            if old_question != new_question:
                assert new_question == instance.question
                break
        else:
            assert False


class Test_DeepLSakubun_WaitingAnswer:

    def test_日本語の回答を受け取り_画面の変更内容を出力できること(self, deepLSakubun, default_input):
        expected_output_answer_original = ("answer_original", default_input[0])
        expected_output_description = ("description", "翻訳先の言語で回答してみましょう")

        actual_output = deepLSakubun.onClick(*default_input)

        assert expected_output_answer_original in actual_output
        assert expected_output_description in actual_output

    def test_ステータスがWaitingTranslateに遷移すること(self, deepLSakubun, default_input):
        expected_status = DeepLSakubun.Status("WaitingTranslate")

        assert deepLSakubun.status == DeepLSakubun.Status("WaitingAnswer")
        deepLSakubun.onClick(*default_input)
        actual_status = deepLSakubun.status

        assert expected_status == actual_status

    def test_二周目以降_新しい回答を元に画面変更内容を出力できること(self, deepLSakubun, default_input):
        old_answer_original = ("answer_original", default_input[0])
        expected_answer_original = ("answer_original", "それなりの回答")

        loop_status(deepLSakubun, default_input)
        new_input = ("それなりの回答", "XXXX", "EN-GB")
        new_output = deepLSakubun.onClick(*new_input)

        assert expected_answer_original in new_output
        assert old_answer_original not in new_output


class Test_DeepLSakubun_WaitingTranslate:

    def test_翻訳先言語の回答を受け取り_画面の変更内容を出力できること(
            self, appWaitingTranslate, default_input_translated):
        expected_output_answer_translated = (
            "answer_translated", default_input_translated[0])
        expected_output_answer_correct_q = (
            "answer_correct_q", TRANSLATED_ANSWER_Q)
        expected_output_answer_correct_a = (
            "answer_correct_a", TRANSLATED_ANSWER_A)
        expected_output_button = ("btn", "クリア")
        assert default_input_translated[2] in DeepLSakubun.LanguagesUsingQA

        actual_output = appWaitingTranslate.onClick(*default_input_translated)

        assert expected_output_answer_translated in actual_output
        assert expected_output_answer_correct_q in actual_output
        assert expected_output_answer_correct_a in actual_output
        assert expected_output_button in actual_output

    def test_ステータスがFinishに遷移すること(self, appWaitingTranslate, default_input):
        expected_status = DeepLSakubun.Status("Finish")

        assert appWaitingTranslate.status == \
            DeepLSakubun.Status("WaitingTranslate")
        appWaitingTranslate.onClick(*default_input)
        actual_status = appWaitingTranslate.status

        assert expected_status == actual_status

    def test_二周目以降_新しい回答を元に画面変更内容を出力できること(
            self, monkeypatch, appWaitingTranslate, default_input_translated):
        old_output_answer_translated = (
            "answer_translated", default_input_translated[0])
        old_output_answer_correct_q = (
            "answer_correct_q", TRANSLATED_ANSWER_Q)
        old_output_answer_correct_a = (
            "answer_correct_a", TRANSLATED_ANSWER_A)
        expected_output_answer_translated = (
            "answer_translated", "Some stupid answer")
        expected_output_answer_correct_q = (
            "answer_correct_q", NEW_TRANSLATED_ANSWER_Q)
        expected_output_answer_correct_a = (
            "answer_correct_a", NEW_TRANSLATED_ANSWER_A)

        loop_status(appWaitingTranslate, default_input_translated)
        new_input = ("Some stupid answer", "XXXX", "EN-GB")
        monkeypatch.setenv("TRANSLATED_ANSWER", NEW_TRANSLATED_ANSWER)

        actual_output = appWaitingTranslate.onClick(*new_input)

        assert old_output_answer_translated not in actual_output
        assert old_output_answer_correct_q not in actual_output
        assert old_output_answer_correct_a not in actual_output
        assert expected_output_answer_translated in actual_output
        assert expected_output_answer_correct_q in actual_output
        assert expected_output_answer_correct_a in actual_output

    def test_onClickの引数を元にcallAPIの引数が生成されること(
            self, monkeypatch,
            deepLSakubun, default_input, default_input_translated):
        deepLSakubun.onClick(*default_input)

        URL = "https://api-free.deepl.com/v2/translate"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = "auth_key=" + default_input_translated[1] + \
            "&text=Q." + deepLSakubun.question + \
            " A." + deepLSakubun.answer_original + \
            "&target_lang=" + default_input_translated[2]
        expected_param = {"URL": URL, "headers": headers, "body": body}

        monkeypatch.setattr(
            "docs.DeepLSakubun.DeepLSakubun._showCorrectAnswer",
            mock_showCorrectAnswer)
        deepLSakubun.onClick(*default_input_translated)

        assert expected_param == deepLSakubun.param

    def test_APIキー未入力の場合は例外を吐くこと(self, appWaitingTranslate):
        with pytest.raises(Exception):
            appWaitingTranslate.onClick("気の利いてない回答", "", "EN-GB")

    def test_分割可能な言語ではDeepLの回答を質問と答えに分割して出力すること(self):
        ...

    def test_分割できない言語ではDeepLの回答を1つのタプルで出力すること(self):
        ...


class Test_DeepLSakubun_Finish:

    def test_インスタンス変数を空にして_画面の変更内容を出力できること(self, deepLSakubun):
        ...

    def test_ステータスがWaitingAnswerに遷移すること(self):
        ...


class Test_others:

    def test_存在しないステータスでonClickを叩くと例外を吐くこと(self):
        ...

    def test_onClickを叩くたびに次のステータスへ遷移すること(self):
        ...
