"""DeepLSakubunモジュールテスト

現段階で粒度の細かいテストを増やしてもテストコードが即寿命を迎えかねないので、
モジュールの入出力をざっくりと確認する。

"""
from typing import Tuple
import pytest
import docs.DeepLSakubun as DeepLSakubun


def mock_callAPI(self, *_) -> None:
    res = {"translations": [{"text": "Q. QQQQQQQQ A. AAAAAAAA"}]}
    self.response = res


@pytest.fixture
def deepLSakubun(monkeypatch) -> DeepLSakubun:
    monkeypatch.setattr(
        "docs.DeepLSakubun.DeepLSakubun._callAPI", mock_callAPI)

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

    def test_二周目以降_新しい回答を元に画面変更内容を出力できること(self):
        ...


class Test_DeepLSakubun_WaitingTranslate:

    def test_翻訳先言語の回答を受け取り_画面の変更内容を出力できること(
            self, appWaitingTranslate, default_input):
        ...

    def test_ステータスがFinishに遷移すること(self, appWaitingTranslate, default_input):
        expected_status = DeepLSakubun.Status("Finish")

        assert appWaitingTranslate.status == \
            DeepLSakubun.Status("WaitingTranslate")
        appWaitingTranslate.onClick(*default_input)
        actual_status = appWaitingTranslate.status

        assert expected_status == actual_status

    def test_二周目以降_新しい回答を元に画面変更内容を出力できること(self):
        ...

    def test_選択した言語が_callAPIの引数に渡されること(self):
        ...

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
