import json
import random

with open("personas.json", "r", encoding="utf-8") as f:
    config = json.load(f)


def generate_dynamic_persona():
    # Пол
    gender = random.choice(list(config["gender"].keys()))
    gender_text = random.choice(config["gender"][gender])

    # Темперамент
    temperament_key = random.choice(list(config["temperament"].keys()))
    temperament_text = config["temperament"][temperament_key]

    # Черты: выбираем по одной из каждой группы
    traits_texts = []
    for group in config["traits"].values():
        trait_key = random.choice(list(group.keys()))
        traits_texts.append(group[trait_key])

    # Собираем системный промпт
    content = f"{gender_text}. {temperament_text} " + " ".join(traits_texts)
    return {"role": "system", "content": content}


# Пример
persona = generate_dynamic_persona()
print(persona)
