import json
from typing import Iterable, Iterator, Sequence, Type
from functools import total_ordering


with open("russian_nouns_with_definition.json", "r", encoding="utf-8") as glossary_file:
    glossary: dict[str, dict[str, str]] = json.load(glossary_file)
    glossary_min = len(min(glossary, key=len))
    glossary_max = len(max(glossary, key=len))


@total_ordering
class Word:
    """Слово из словаря с определением"""

    def __init__(self, word: str) -> None:
        self.word = word

    def __repr__(self) -> str:
        return f"{__class__.__name__}({self.word!r})"

    def __str__(self) -> str:
        return self.word

    def __len__(self) -> int:
        return len(self.word)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (len(self), self.word) > (len(other), other.word)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.word == other.word

    @property
    def definition(self) -> str | None:
        return glossary[self.word]["definition"]


class RussianLetters:
    """Дескриптор, проверяющий вхождение только русских букв"""

    def __set_name__(self, cls, attr):
        self._attr = attr

    def __get__(self, obj, cls) -> tuple[str, ...]:
        if self._attr in obj.__dict__:
            return obj.__dict__[self._attr]
        else:
            raise AttributeError("Атрибута не существует")

    def __set__(self, obj: Type["Words"], value: Sequence[str]):
        if not isinstance(value, Sequence):
            raise TypeError

        if not self.__validate_russian_letters(value):
            raise ValueError("Все буквы должны быть русскими")

        obj.__dict__[self._attr] = tuple(map(str.lower, value))

    def __validate_russian_letters(self, letters: Iterable[str]) -> bool:
        """Валидатор русских букв"""
        RUSSIAN_LETTERS = (
            "а",
            "б",
            "в",
            "г",
            "д",
            "е",
            "ё",
            "ж",
            "з",
            "и",
            "й",
            "к",
            "л",
            "м",
            "н",
            "о",
            "п",
            "р",
            "с",
            "т",
            "у",
            "ф",
            "х",
            "ц",
            "ч",
            "ш",
            "щ",
            "ъ",
            "ы",
            "ь",
            "э",
            "ю",
            "я",
        )
        for letter in letters:
            if letter.lower() not in RUSSIAN_LETTERS:
                return False
        return True


class Words:
    """Основной класс, выдающий слова по запрошенным буквам"""

    symbols = RussianLetters()

    def __init__(
        self,
        symbols: Sequence[str],
        minimum: int = glossary_min,
        maximum: int = glossary_max,
    ) -> None:
        self.symbols = symbols
        self.minimum = minimum
        self.maximum = maximum

    def __word_in_symbols(self, word: str) -> bool:
        if len(self.symbols) < len(word):
            return False

        symbols = list(self.symbols)
        for letter in word:
            if letter in symbols:
                symbols.remove(letter)
            elif letter == "ё" and "е" in symbols:  # частный случай для 'Ë'
                symbols.remove("е")
            else:
                return False
        return True

    def get_words(self) -> Iterator[Word] | None:
        possible_words = filter(
            lambda word: max(glossary_min, self.minimum)
            <= len(word)
            <= min(self.maximum, len(word), glossary_max),
            glossary,
        )
        filtered_words = tuple(
            filter(
                lambda word: self.__word_in_symbols(word),
                possible_words,
            )
        )

        if not filtered_words:
            return None

        return map(Word, sorted(filtered_words, key=lambda x: (len(x), x)))
