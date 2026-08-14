import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

CHECKO_API_KEY = os.getenv("CHECKO_API_KEY")
CHECKO_API_URL = "https://api.checko.ru/v2/company"


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/api/company")
def get_company(inn: str):
    inn = inn.strip()

    if not inn.isdigit() or len(inn) != 10:
        raise HTTPException(
            status_code=400,
            detail="ИНН организации должен состоять из 10 цифр.",
        )

    if not CHECKO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API-ключ Чекко не настроен.",
        )

    try:
        response = httpx.post(
            CHECKO_API_URL,
            json={
                "key": CHECKO_API_KEY,
                "inn": inn,
            },
            timeout=20.0,
        )
        response.raise_for_status()
        result = response.json()

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Не удалось получить ответ от сервиса Чекко.",
        )

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Сервис Чекко вернул некорректный ответ.",
        )

    meta = result.get("meta", {})

    if meta.get("status") != "ok":
        raise HTTPException(
            status_code=502,
            detail=meta.get("message") or "Чекко не смог обработать запрос.",
        )

    data = result.get("data")

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Организация не найдена.",
        )

    legal_address = data.get("ЮрАдрес") or {}

    risks = []

    if legal_address.get("Недост"):
        risks.append("Недостоверный юридический адрес")

    if data.get("НедобПост"):
        risks.append("Включение в реестр недобросовестных поставщиков")

    if data.get("ДисквЛица"):
        risks.append("Дисквалифицированные лица в руководстве")

    if data.get("МассРуковод"):
        risks.append("Массовый руководитель")

    if data.get("МассУчред"):
        risks.append("Массовый учредитель")

    if data.get("НелегалФин"):
        risks.append("Признак нелегальной деятельности на финансовом рынке")

    if data.get("Санкции"):
        risks.append("Организация включена в санкционные списки")

    if data.get("СанкцУчр"):
        risks.append("Санкции в отношении учредителей")

    managers = data.get("Руковод") or []
    manager = managers[0] if managers else {}

    okved = data.get("ОКВЭД") or {}
    status = data.get("Статус") or {}

    return {
        "name": data.get("НаимСокр") or data.get("НаимПолн"),
        "status": status.get("Наим"),
        "inn": data.get("ИНН"),
        "ogrn": data.get("ОГРН"),
        "kpp": data.get("КПП"),
        "registration_date": data.get("ДатаРег"),
        "legal_address": legal_address.get("АдресРФ"),
        "okved": {
            "code": okved.get("Код"),
            "name": okved.get("Наим"),
        },
        "manager": {
            "name": manager.get("ФИО"),
            "position": manager.get("НаимДолжн"),
        },
        "risk_checks": {
            "Недостоверный адрес": bool(legal_address.get("Недост")),
            "Массовый руководитель": bool(data.get("МассРуковод")),
            "Массовый учредитель": bool(data.get("МассУчред")),
            "Дисквалифицированные лица в руководстве": bool(
                data.get("ДисквЛица")
            ),
            "Включение в реестр недобросовестных поставщиков": bool(
                data.get("НедобПост")
            ),
            "Признак нелегальной деятельности на фин. рынке": bool(
                data.get("НелегалФин")
            ),
            "Организация включена в санкционные списки": bool(
                data.get("Санкции")
            ),
            "Санкции в отношении учредителей": bool(
                data.get("СанкцУчр")
            ),
        },
        "risks": risks,
    }