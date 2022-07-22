"""APIコール回り
"""
import json
from Common import DEEPL_API_URL, SERVER_URL


class DeepLSakubunCallAPI:

    def _generateParam(self, auth_key: str) -> dict[str, str]:
        URL = DEEPL_API_URL
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = "auth_key=" + auth_key + \
            "&text=Q." + self.question + \
            " A." + self.answer_original + \
            "&target_lang=" + self.target_lang
        param = {"URL": URL, "headers": headers, "body": body}
        return param

    def _generateParamForAPIServer(self, auth_key: str) -> dict[str, str]:
        URL = SERVER_URL + "translate/"
        headers = {"Content-Type": "application/json"}
        body = json.dumps({
                "text": "Q." + self.question + " A." + self.answer_original,
                "target_lang": self.target_lang,
                "auth_key": auth_key
        })
        param = {"URL": URL, "headers": headers, "body": body}
        return param

    def _callAPI(self, param: dict[str, str | dict[str, str]]) -> None:
        # モジュールテストを可能にするため、PyScriptのjsモジュールはlazy importする
        from js import XMLHttpRequest
        req = XMLHttpRequest.new()
        req.open("POST", param["URL"], False)
        for k, v in param["headers"].items():
            req.setRequestHeader(k, v)
        print(f'{param["URL"]} {param["body"]}')
        req.send(param["body"])
        self.response = json.loads(req.response)
