import itertools
import json
import os
from typing import Dict, Union

from pydantic import BaseModel,Field,NoneStr,ValidationError,root_validator,validator # type: ignore


class WordQuestion(BaseModel):
    sample: str = Field(min_length=1)
    result_min: int = Field(default=2, gt=1, le=10)
    result_max: int = Field(default=10, gt=1, le=10)

    @validator("sample", pre=True)
    def clean_sample(cls, sample):
        """Подчищает строку, удаляе из нее возможную пунктуацию"""

        for symbol in " ,._":
            sample = sample.replace(symbol, "")
        return sample.lower()

    @root_validator()
    def check_data(cls, values):
        """Проверяет строку на условия
        1. только буквы
        2. только РУССКИЕ буквы
        3. введено более 1 буквы
        4. строка меньше или равна максимальному результату
        5. строка больше или равна минимальному результату
        6. длина строки не более 10 символов (иначе очень долго)
        7. минимальный и максимальный результат не перепутаны"""

        _sample: str = values.get("sample")
        _result_min: int = values.get("result_min")
        _result_max: int = values.get("result_max")

        if not _sample.isalpha():  # проверяем, что только буквы
            raise ValueError(
                "Для создания слов нужно указать только буквы. Цифры и прочие символы не нужны."
            )

        if not set(_sample) <= set(
            "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        ):  # проверяем, что буквы именно русские
            raise ValueError(
                "Для создания слов нам нужны только русские буквы. Иначе никак."
            )

        if len(_sample) == 1:  # проверка, что буква не одна
            raise ValueError("Мы не сможем сгенерировать слова из 1 буквы")

        if (
            len(_sample) < _result_max
        ):  # проверямем, что сможем сгенерировать слово нужной максимальной длины
            raise ValueError(
                'Неправильно заданы условия. Букв должно быть больше или равно, чем максимальная длина результата. Например: буквы "ПРИВЕТ" могут дать слова максимум в 6 символов.'
            )

        if (
            len(_sample) < _result_min
        ):  # проверяем, что сможем сгенерировать слово нужной минимальной длины
            raise ValueError(
                'Неправильно заданы условия. Букв должно быть меньше или равно, чем минимальная длина результата. Например: буквы "ДА" не смогут дать слова длиннее 2 символов.'
            )

        if (
            len(_sample) > 10
        ):  # генерация через мутации для 10 символов занимает много времени, поэтому проверка на то, что используем максимум 10 букв
            raise ValueError(
                f"Слишком много букв ({len(_sample)}). Мы будем создавать слова очень долго. Поэтому используйте максимум 10 букв. Простите за такое ограничение."
            )

        if _result_min > _result_max:
            raise ValueError(
                "Длина минимального результата не может быть больше длины максимального. Проверьте, не перепутали ли вы значения местами."
            )

        return values


class WordAnswerData(BaseModel):
    word: str
    definition: str


class WordAnswer(BaseModel):
    success: bool = Field(default=False)
    sample: str
    message: NoneStr = Field(default=None)
    data: list = Field(default=[])


def make_russian_dict() -> Dict[str, Dict[str, str]]:
    """Проверяет, что файл "russian_nouns_with_definition.json":
    1. загружен на сервер
    2. нормально парсится
    3. результат имеет значения (длина не равна нулю)"""

    russian_dict_file = os.path.join(os.getcwd(), "russian_nouns_with_definition.json")
    if os.path.exists(russian_dict_file):
        with open(russian_dict_file, "r") as file:
            try:
                word_base: Dict[str, Dict[str, str]] = json.load(file)
                if len(word_base) > 0:
                    return word_base
                else:
                    raise ValueError(
                        "Файл со словарем русских слов подключился, но почему-то пуст. Проверьте файл."
                    )

            except json.JSONDecodeError:
                raise ValueError(
                    "Не удается подключить файл со словарем русских слов. Он существует, но не в том формате, что нужен. Возможно, используется неправильный файл."
                )

    else:
        raise ValueError(
            "Файл со словарем русских слов не найден. Проверьте, что он загружен."
        )


def get_words(
    sample: str, result_min: int, result_max: int, russ_dict: Dict[str, Dict[str, str]]
) -> WordAnswer:

    try:
        params = WordQuestion(
            sample=sample, result_min=result_min, result_max=result_max
        )
        answer = WordAnswer(success=True, sample=params.sample, message="OK")

        for result_len in range(params.result_min, params.result_max + 1):
            for i in set(itertools.permutations(params.sample, result_len)):
                word = "".join(i)
                if word in russ_dict:
                    answer.data.append(
                        {"word": word, "definition": russ_dict[word]["definition"]}
                    )

        if not len(answer.data):
            return WordAnswer(
                success=False,
                sample=params.sample,
                message="Не получилось создать слова из предоставленных букв заданной длины. Попробуйте другие буквы и другую длину.",
            )

        return answer

    except ValidationError as e:
        answer = WordAnswer(
            sample=sample, message=", ".join([i["msg"] for i in e.errors()])
        )
        return answer
