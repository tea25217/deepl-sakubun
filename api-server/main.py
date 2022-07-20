import os
from fastapi import FastAPI
from pydantic import BaseModel
from deepl import Translator, exceptions


class Params(BaseModel):
    text: str | None = None
    auth_key: str | None = None
    target_lang: str | None = None


app = FastAPI()


def prepareTranslator(params: Params):
    # print(f"params are\n {params.dict()}")
    auth_key = params.auth_key or os.getenv("DEEPL_API_KEY_FREE")
    # print(f"{auth_key=}")

    if not auth_key:
        return None

    return Translator(auth_key)


@app.post("/translate/")
def translate(params: Params):
    translator = prepareTranslator(params)

    if not all([translator, params.text, params.target_lang]):
        return {"message": "Required parameters are not completed."}

    try:
        result = translator.translate_text(
            params.text, target_lang=params.target_lang)
    except exceptions.AuthorizationException:
        return {"message": "API key is wrong."}
    except exceptions.DeepLException:
        return {"message": "API access is failed."}

    return {"message": "Successfully translated.",
            "detected_source_lang": result.detected_source_lang,
            "text": result.text}


@app.post("/usage/")
def usage(params: Params):
    translator = prepareTranslator(params)

    try:
        usage = translator.get_usage()
    except exceptions.AuthorizationException:
        return {"message": "API key is wrong."}
    except exceptions.DeepLException:
        return {"message": "API access is failed."}
    except AttributeError:
        return {"message": "API key is required."}

    if usage.character.valid:
        return {"message": "Character usage is checked.",
                "count": usage.character.count,
                "limit": usage.character.limit}

    return {"message": "Something is wrong."}
