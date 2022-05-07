import itertools
import os
import json


def get_words(sample: str):

    if sample.isalpha():
        if len(sample) <= 10:
            with open(
                os.path.join(os.getcwd(), "russian_nouns_with_definition.json"), "r"
            ) as file:
                word_base = json.load(file)

            answer = {
                "success": True,
                "message": None,
                "sample": sample,
                "data": [],
            }

            for var_len in range(2, len(sample) + 1):
                for i in set(itertools.permutations(sample, var_len)):
                    word = "".join(i)
                    if word in word_base:
                        answer["data"].append(
                            {"word": word, "definition": word_base[word]["definition"]}
                        )
        else:
            answer = {
                "success": False,
                "message": f"Слишком много букв. Их должно быть не более 10, а вы прислали {len(sample)}",
                "sample": sample,
                "data": [],
            }

    else:
        answer = {
            "success": False,
            "message": "В тексте должны быть только буквы",
            "sample": sample,
            "data": [],
        }

    return answer
