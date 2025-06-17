krainian morphology toolkit

A powerful Python tool for inflecting Ukrainian names, job titles, and sentences. Built on `pymorphy3`, this toolkit adds a layer of advanced rules and heuristics specifically tailored for the complexities of the Ukrainian language.

Простий у використанні Python-модуль для відмінювання українських ПІБ (Прізвище, Ім'я, По-батькові), слів, посад та речень у будь-якому відмінку. Використовує pymorphy3 як основу, доповнюючи його правилами постобробки для досягнення більш точних та природних результатів, особливо для імен та назв посад.

English Documentation
Features

Full Name Inflection: Correctly inflects Ukrainian surnames, first names, and patronymics.

Sentence Inflection: Inflects every word in a sentence to the specified case.

Specialized Job Title Inflection: A special mode (position=True) correctly handles job titles, where typically only the first one or two words are inflected (e.g., "головний бухгалтер" -> "головного бухгалтера").

Gender Detection: Automatically detects the gender from the first name to apply correct inflection rules.

Post-processing Rules: Applies Ukrainian-specific grammatical rules to fix common errors or handle stylistic variants that pymorphy3 might miss.

Interactive CLI: Comes with a simple command-line interface for quick tests and usage without writing code.

Requirements

Python 3.6+

pymorphy3 library

Installation
pip install pymorphy3


Save the provided code as a Python file (e.g., morpher.py).

How to Use
1. As a Library

Import the NameMorpher or SentenceMorpher class into your project.

The NameMorpher class is designed specifically for full names in the "Surname FirstName Patronymic" format.

from morpher import NameMorpher

# Initialize the morpher
name_morpher = NameMorpher()

fullname = "Іваненко Тарас Петрович"

# Inflect to the genitive case ('gent')
gent_name = name_morpher.morph_name(fullname, "gent")
print(f"Genitive: {gent_name}")
# Output: Genitive: ІВАНЕНКА Тараса Петровича

# Inflect to the dative case ('datv')
datv_name = name_morpher.morph_name(fullname, "datv")
print(f"Dative: {datv_name}")
# Output: Dative: ІВАНЕНКУ Тарасу Петровичу

# Inflect a female name
female_fullname = "Ковальчук Ольга Василівна"
voct_name = name_morpher.morph_name(female_fullname, "voct")
print(f"Vocative: {voct_name}")
# Output: Vocative: КОВАЛЬЧУК Ольго Василівно
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

The SentenceMorpher class is used for general-purpose text inflection.

from morpher import SentenceMorpher

# Initialize the morpher
sentence_morpher = SentenceMorpher()

# --- Example 1: Inflecting a simple phrase ---
phrase = "червона калина"
inflected_phrase = sentence_morpher.morph_sentence(phrase, "ablt")
print(f"Instrumental: {inflected_phrase}")
# Output: Instrumental: червоною калиною

# --- Example 2: Inflecting a job title (special logic) ---
# Use position=True to handle job titles correctly
job_title = "головний спеціаліст - провідний інспектор"
inflected_title = sentence_morpher.morph_sentence(job_title, "datv", position=True)
print(f"Dative (position): {inflected_title}")
# Output: Dative (position): головному спеціалісту - провідному інспектору

job_title_2 = "заступник начальника відділу"
inflected_title_2 = sentence_morpher.morph_sentence(job_title_2, "gent", position=True)
print(f"Genitive (position): {inflected_title_2}")
# Output: Genitive (position): заступника начальника відділу
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
2. Using the Command-Line Interface (CLI)

Run the script from your terminal to use the interactive mode.

python morpher.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The CLI will guide you through the process:

Український універсальний відмінювач
1 - Відмінювання ПІБ
2 - Відмінювання речень/слів
Введіть 'вихід' або 'exit' для завершення

Оберіть режим (1/2): 1

Доступні відмінки:
nomn: називний
gent: родовий
datv: давальний
accs: знахідний
ablt: орудний
loct: місцевий
voct: кличний

Оберіть відмінок (скорочення): gent
Введіть ПІБ (Прізвище Ім'я По-батькові): Шевченко Іван Григорович
Родовий відмінок: ШЕВЧЕНКА Івана Григоровича

Оберіть режим (1/2): 2

...
Оберіть відмінок (скорочення): datv
Введіть речення або слово: головний бухгалтер
Давальний відмінок: головному бухгалтеру
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
Supported Grammatical Cases
Code	Case Name (English)	Case Name (Ukrainian)
nomn	Nominative	Називний
gent	Genitive	Родовий
datv	Dative	Давальний
accs	Accusative	Знахідний
ablt	Instrumental	Орудний
loct	Locative	Місцевий
voct	Vocative	Кличний
<br/>
<hr/>
<br/>

Українська документація
Можливості

Відмінювання ПІБ: Коректно відмінює українські прізвища, імена та по-батькові.

Відмінювання речень: Змінює кожне слово в реченні відповідно до заданого відмінка.

Спеціалізоване відмінювання посад: Спеціальний режим (position=True) правильно обробляє назви посад, де зазвичай відмінюється лише перше або перші два слова (напр., "головний бухгалтер" -> "головного бухгалтера").

Визначення роду: Автоматично визначає рід за іменем для застосування правильних правил відмінювання.

Правила постобробки: Застосовує специфічні для української мови граматичні правила для виправлення поширених помилок або обробки стилістичних варіантів, які pymorphy3 може пропустити.

Інтерактивний CLI: Постачається з простим інтерфейсом командного рядка для швидкого тестування та використання без написання коду.

Вимоги

Python 3.6+

Бібліотека pymorphy3

Встановлення
pip install pymorphy3
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Збережіть наданий код у файл Python (наприклад, morpher.py).

Як використовувати
1. Як бібліотеку

Імпортуйте клас NameMorpher або SentenceMorpher у ваш проєкт.

Клас NameMorpher розроблений спеціально для повних імен у форматі "Прізвище Ім'я По-батькові".

from morpher import NameMorpher

# Ініціалізація відмінювача
name_morpher = NameMorpher()

pib = "Іваненко Тарас Петрович"

# Відмінювання в родовому відмінку ('gent')
rodovyi_pib = name_morpher.morph_name(pib, "gent")
print(f"Родовий: {rodovyi_pib}")
# Вивід: Родовий: ІВАНЕНКА Тараса Петровича

# Відмінювання в давальному відмінку ('datv')
davalnyi_pib = name_morpher.morph_name(pib, "datv")
print(f"Давальний: {davalnyi_pib}")
# Вивід: Давальний: ІВАНЕНКУ Тарасу Петровичу

# Відмінювання жіночого імені
female_pib = "Ковальчук Ольга Василівна"
klychnyi_pib = name_morpher.morph_name(female_pib, "voct")
print(f"Кличний: {klychnyi_pib}")
# Вивід: Кличний: КОВАЛЬЧУК Ольго Василівно
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

Клас SentenceMorpher використовується для відмінювання тексту загального призначення.

from morpher import SentenceMorpher

# Ініціалізація відмінювача
sentence_morpher = SentenceMorpher()

# --- Приклад 1: Відмінювання простої фрази ---
fraza = "червона калина"
orudnyi_fraza = sentence_morpher.morph_sentence(fraza, "ablt")
print(f"Орудний: {orudnyi_fraza}")
# Вивід: Орудний: червоною калиною

# --- Приклад 2: Відмінювання назви посади (спеціальна логіка) ---
# Використовуйте position=True для коректної обробки посад
posada = "головний спеціаліст - провідний інспектор"
davalnyi_posada = sentence_morpher.morph_sentence(posada, "datv", position=True)
print(f"Давальний (посада): {davalnyi_posada}")
# Вивід: Давальний (посада): головному спеціалісту - провідному інспектору

posada_2 = "заступник начальника відділу"
rodovyi_posada_2 = sentence_morpher.morph_sentence(posada_2, "gent", position=True)
print(f"Родовий (посада): {rodovyi_posada_2}")
# Вивід: Родовий (посада): заступника начальника відділу
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END
2. Використання через командний рядок (CLI)

Запустіть скрипт з терміналу, щоб увійти в інтерактивний режим.

python morpher.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

CLI допоможе вам у процесі:

Український універсальний відмінювач
1 - Відмінювання ПІБ
2 - Відмінювання речень/слів
Введіть 'вихід' або 'exit' для завершення

Оберіть режим (1/2): 1

Доступні відмінки:
nomn: називний
gent: родовий
datv: давальний
accs: знахідний
ablt: орудний
loct: місцевий
voct: кличний

Оберіть відмінок (скорочення): gent
Введіть ПІБ (Прізвище Ім'я По-батькові): Шевченко Іван Григорович
Родовий відмінок: ШЕВЧЕНКА Івана Григоровича

Оберіть режим (1/2): 2

...
Оберіть відмінок (скорочення): datv
Введіть речення або слово: головний бухгалтер
Давальний відмінок: головному бухгалтеру
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
Підтримувані граматичні відмінки
Код	Назва відмінка
nomn	Називний
gent	Родовий
datv	Давальний
accs	Знахідний
ablt	Орудний
loct	Місцевий
voct	Кличний
