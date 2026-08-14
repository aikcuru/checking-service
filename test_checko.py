import os

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("CHECKO_API_KEY")
test_inn = os.getenv("CHECKO_TEST_INN")

if not api_key:
    raise RuntimeError("CHECKO_API_KEY не найден в .env")

if not test_inn:
    raise RuntimeError("CHECKO_TEST_INN не найден в .env")

test_inn = test_inn.strip()

if not test_inn.isdigit() or len(test_inn) != 10:
    raise ValueError("CHECKO_TEST_INN должен состоять ровно из 10 цифр")

response = httpx.post(
    "https://api.checko.ru/v2/company",
    json={
        "key": api_key,
        "inn": test_inn,
    },
    timeout=20.0,
)

response.raise_for_status()

result = response.json()

meta = result.get("meta", {})
data = result.get("data", {})

print("HTTP:", response.status_code)
print("API status:", meta.get("status"))
print("Название:", data.get("НаимСокр"))
print("ИНН:", data.get("ИНН"))
print("Статус:", data.get("Статус", {}).get("Наим"))
print("Запросов сегодня:", meta.get("today_request_count"))
