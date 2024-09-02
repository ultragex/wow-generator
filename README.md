# Что это?
Это небольшой сервис для того, чтобы помочь сгенерировать нужные слова из предоставленных букв. Слова можно использовать в игре ["Words of Wonders"](https://play.google.com/store/apps/details?id=com.fugo.wow) и других подобных.


## Особенности:
- Можно задавать минимальную и максимальную длину слов;
- Валидация данных на входе;
- Ищет и дает определения получившимся словам.

## На чем работает:
- Python 3.12
- Flask для веб-части (+Jinja в качестве шаблонизатора)


## Запуск:
```sh
flask --app app run
```
