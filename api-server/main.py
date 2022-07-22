import os
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deepl import Translator, exceptions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Params(BaseModel):
    text: str | None = None
    auth_key: str | None = None
    target_lang: str | None = None


@app.get("/")
def get():
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


def prepareTranslator(params: Params):
    print(f"params are\n {params}")
    auth_key = params.auth_key or os.getenv("DEEPL_API_KEY_FREE")
    # print(f"{auth_key=}")

    if not auth_key:
        return None

    return Translator(auth_key)


@app.post("/translate/")
def translate(params: Params):
    translator = prepareTranslator(params)

    if not all([translator, params.text, params.target_lang]):
        return {
            "result": "NG",
            "message": "Required parameters are not completed."
        }

    try:
        response = translator.translate_text(params.text,
                                             target_lang=params.target_lang)
    except exceptions.AuthorizationException:
        return {"result": "NG", "message": "API key is wrong."}
    except exceptions.DeepLException:
        return {"result": "NG", "message": "API access is failed."}

    print(f"{response.detected_source_lang=}")
    print(f"{response.text=}")

    return {
        "result":
        "OK",
        "message":
        "Successfully translated.",
        "translations": [{
            "detected_source_language": response.detected_source_lang,
            "text": response.text
        }]
    }


@app.post("/usage/")
def usage(params: Params):
    translator = prepareTranslator(params)

    try:
        usage = translator.get_usage()
    except exceptions.AuthorizationException:
        return {"result": "NG", "message": "API key is wrong."}
    except exceptions.DeepLException:
        return {"result": "NG", "message": "API access is failed."}
    except AttributeError:
        return {"result": "NG", "message": "API key is required."}

    if usage.character.valid:
        return {
            "result": "OK",
            "message": "Character usage is checked.",
            "count": usage.character.count,
            "limit": usage.character.limit
        }

    return {"result": "NG", "message": "Something is wrong."}
