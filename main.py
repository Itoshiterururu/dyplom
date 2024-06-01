from pymongo import MongoClient

# Підключення до MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['dyplom']
cadets_collection = db['officers']

# Очищення колекції курсантів (якщо потрібно)
cadets_collection.delete_many({})

# Додавання тестових даних
test_data = [
    {
        "_id": "1",
        "name": "Иванов Иван Иванович",
        "rank": "Капитан",
        "specialty": "Военная тактика",
        "years_of_service": {
            "2020": {
                "assignments": ["Участие в учениях", "Командировка"],
                "courses": ["Курс тактической подготовки", "Курс лидерства"],
                "evaluations": {
                    "leadership": 90,
                    "tactics": 85,
                    "physical_fitness": 88,
                    "discipline": 92
                }
            },
            "2021": {
                "assignments": ["Командование ротой", "Участие в международных учениях"],
                "courses": ["Курс управления подразделением", "Курс стратегического планирования"],
                "evaluations": {
                    "leadership": 93,
                    "tactics": 87,
                    "physical_fitness": 90,
                    "discipline": 95
                }
            }
        },
        "skills": ["Лидерство", "Стратегическое мышление", "Тактическое планирование"]
    }

]



cadets_collection.insert_many(test_data)
print("Тестові дані додано успішно")
