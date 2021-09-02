# UABlacklist

Список запрещённых в Украине сайтов.

## Основания
- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №304/2021 (23.07.2021)

  https://www.president.gov.ua/documents/3042021-39449
- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №266/2021 (24.06.2021)

  https://www.president.gov.ua/documents/2662021-39265
- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №265/2021 (24.06.2021)

  https://www.president.gov.ua/documents/2652021-39261
- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №203/2021 (21.05.2021)

  https://www.president.gov.ua/documents/2032021-38949
- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №184/2020 (14.05.2020)

  https://www.president.gov.ua/documents/1842020-33629
- Cправа № 761/4683/20 (13.02.2020)
  
  https://nkrzi.gov.ua/index.php?r=site/index&pg=99&id=1876
- Cправа № №757/3623/20-к (27.01.2020)

  https://nkrzi.gov.ua/index.php?r=site/index&pg=99&id=1870

- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №82/2019 (19.03.2019) 

  https://www.president.gov.ua/documents/822019-26290

- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №176/2018 (21.06.2018)

  https://www.president.gov.ua/documents/1762018-24362

- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №126/2018 (14.05.2018)

  https://www.president.gov.ua/documents/1262018-24150

- УКАЗ ПРЕЗИДЕНТА УКРАЇНИ №133/2017 (15.05.2017)
  https://www.president.gov.ua/documents/1332017-21850

## Формат domains.json

Массив объектов, где ключ - домен. Значение - объект со свойствами:

- `urls` (масссив, опционально). Список ссылок, которые были перечислены в документе, на том же домене. Отсутствует, 
  если в документе не было ссылок.
- `company` (строка, опционально). Название компании на украинском языке, которой принадлежит домен, как она указана в 
  документе. Изначально отсутствовало, поэтому некоторые домены без этого свойства.
- `alias` (строка, опционально). Алиас латиницей для группировки нескольких доменов разных компаний для удобства. 
  Допустим, у webmoney несколько названий компаний и для группировки используется alias.   
- `reason` (строка, опционально). Ссылка или текстовое описание причины блокировки.
- `term` (строка или null). Дата конца блокировки формата "дд.мм.гггг". `null` в случае безсрочной блокировки.
