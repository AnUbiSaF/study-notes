# Задача 01 — Positive_int

[[Задачи по C++|← К списку задач]]

## Что хранит объект

```cpp
class Positive_int {
 private:
  int num;
  int array_size;
  int* array;
  bool array_type;  // true — sorted, false — unsorted
};
```

### Поля

- `num` — само положительное число.
- `array_size` — количество простых множителей.
- `array` — динамический C-style массив простых множителей.
- `array_type` — должен ли массив храниться отсортированным.

Пример:

```text
num = 12
array = [2, 2, 3]
array_size = 3
```

---

# Конструктор

```cpp
Positive_int::Positive_int(int n, bool type)
    : num(n), array_type(type) {
  array = find_prime_divisors(num);

  if (array_type) {
    std::sort(array, array + array_size);
  }
}
```

### Что происходит

```cpp
: num(n), array_type(type)
```

Это initializer list.

Поля `num` и `array_type` инициализируются ещё до входа в тело конструктора.

Дальше:

```cpp
array = find_prime_divisors(num);
```

Метод создаёт новый динамический массив и возвращает его адрес.

После конструктора объект должен уже быть полностью корректным:

```text
число известно
массив создан
размер известен
режим sorted/unsorted соблюдён
```

---

# Поиск простых множителей

Для `60`:

```text
60 / 2 = 30  -> 2
30 / 2 = 15  -> 2
15 / 3 = 5   -> 3
5 / 5 = 1    -> 5
```

Получаем:

```text
[2, 2, 3, 5]
```

## Почему два прохода

C-style массив нельзя расширять через `append`.

Поэтому сначала надо узнать его размер.

### Первый проход — считаем количество

```cpp
array_size = 0;
int temp = num;
int d = 2;

while (temp > 1) {
  while (temp % d == 0) {
    ++array_size;
    temp /= d;
  }

  ++d;
}
```

Смысл:

- `temp` — рабочая копия числа;
- `d` — текущий кандидат в множители;
- пока число делится на `d`, этот множитель встречается ещё один раз.

Для `12`:

```text
12 / 2 -> count = 1
6 / 2  -> count = 2
3 / 3  -> count = 3
```

Значит нужен массив из трёх элементов.

### Выделение памяти

```cpp
int* result = new int[array_size];
```

Теперь память уже есть.

### Второй проход — заполняем

Логика та же самая, только найденный множитель записывается в массив:

```text
12 -> [2, 2, 3]
```

---

# Copy constructor

```cpp
Positive_int::Positive_int(const Positive_int& other)
    : num(other.num) {
  array_size = other.array_size;
  array_type = other.array_type;

  array = new int[array_size];

  for (int i = 0; i < array_size; ++i) {
    array[i] = other.array[i];
  }
}
```

## Зачем он нужен

Если просто скопировать указатель:

```text
object1.array ─┐
               ├──> одна память
object2.array ─┘
```

оба объекта будут владеть одной областью памяти.

Когда оба деструктора сделают:

```cpp
delete[] array;
```

получится double free.

Поэтому делается deep copy:

```text
object1.array -> [2, 2, 3]
object2.array -> [2, 2, 3]
```

Значения одинаковые, память разная.

---

# Деструктор

```cpp
Positive_int::~Positive_int() {
  delete[] array;
}
```

Он освобождает память, которую объект получил через:

```cpp
new int[...]
```

Правило:

```text
new       -> delete
new[]     -> delete[]
```

---

# `operator=`

Copy constructor:

```text
новый объект создаётся из старого
```

Присваивание:

```text
оба объекта уже существуют
```

Пример:

```text
a = b
```

Логика оператора:

```cpp
Positive_int& Positive_int::operator=(const Positive_int& other) {
  if (this == &other) {
    return *this;
  }

  delete[] array;

  num = other.num;
  array_size = other.array_size;
  array_type = other.array_type;

  array = new int[array_size];

  for (int i = 0; i < array_size; ++i) {
    array[i] = other.array[i];
  }

  return *this;
}
```

## `this`

`this` — указатель на текущий объект.

```cpp
*this
```

— сам текущий объект.

Проверка:

```cpp
if (this == &other)
```

ловит случай:

```text
a = a
```

чтобы объект не удалил собственный массив перед копированием.

---

# НОД через простые множители

Пример:

```text
12 -> [2, 2, 3]
16 -> [2, 2, 2, 2]
```

Общая часть:

```text
[2, 2]
```

НОД:

```text
2 * 2 = 4
```

## Почему нельзя просто проверить наличие

Важно количество повторов.

Например:

```text
8 -> [2, 2, 2]
6 -> [2, 3]
```

Общая двойка только одна.

Поэтому нельзя одну и ту же `2` из второго массива использовать три раза.

Для этого нужен временный массив:

```cpp
int* used = new int[num2.array_size];
```

Он отмечает, какие элементы второго массива уже использованы.

Идея:

```text
used[j] == false -> элемент ещё свободен
used[j] == true  -> элемент уже участвовал в НОД
```

Алгоритм:

```text
result = 1

для каждого множителя первого числа:
    искать равный неиспользованный множитель второго

    если найден:
        result *= множитель
        пометить второй элемент used
        break
```

В конце:

```cpp
delete[] used;
```

---

# НОК

Используется формула:

```text
НОК(a, b) = a * b / НОД(a, b)
```

Например:

```text
12 * 16 / 4 = 48
```

---

# Реинициализация

Объект уже существует, но должен начать представлять другое число.

Например:

```text
было:
num = 12
array = [2, 2, 3]

стало:
num = 20
array = [2, 2, 5]
```

Метод должен:

```text
проверить новое число
↓
удалить старый array
↓
поменять num
↓
заново найти множители
↓
при необходимости отсортировать
```

Фрагмент логики:

```cpp
delete[] array;
array = find_prime_divisors(num);
```

Важно: старый массив сначала освобождается, иначе будет leak.

---

# Замена множителя

Пример:

```text
12 -> [2, 2, 3]
```

Нужно заменить один `2` на `5`.

Получаем:

```text
[5, 2, 3]
```

После этого число пересчитывается:

```text
5 * 2 * 3 = 30
```

То есть массив простых множителей позволяет однозначно восстановить число произведением элементов.

## Если массив должен быть sorted

После:

```text
[5, 2, 3]
```

надо снова получить:

```text
[2, 3, 5]
```

иначе `array_type == true` будет врать о реальном состоянии массива.

---

# Sorted / unsorted

```cpp
bool array_type;
```

Смысл:

```text
true  -> массив должен быть отсортирован
false -> порядок не гарантируется
```

Сам факт наличия `bool` недостаточен.

Если операция меняет содержимое массива, надо сохранить инвариант:

```text
array_type == true
    =>
array реально отсортирован
```

---

# `const`

## Передача объекта без копирования

```cpp
const Positive_int& other
```

Смысл:

- `&` — не делать копию объекта;
- `const` — запрещено менять `other`.

Это особенно важно в copy constructor и функциях вроде `gcd`.

## `const`-метод

Если метод только читает объект:

```cpp
void print_divisors() const;
```

`const` после скобок означает:

> метод не меняет поля объекта.

---

# Разделение на файлы

## `positive_int.h`

Здесь хранится только интерфейс класса:

```cpp
#ifndef POSITIVE_INT_H_
#define POSITIVE_INT_H_

class Positive_int {
 private:
  int num;
  int array_size;
  int* array;
  bool array_type;

 public:
  Positive_int(int n, bool type);
  Positive_int(const Positive_int& other);

  int* find_prime_divisors(int num);
  void reinitialize(int n);
  void divisor_replace(int from, int to);

  Positive_int& operator=(const Positive_int& other);

  friend int gcd(const Positive_int& num1, const Positive_int& num2);
  friend int lcm(const Positive_int& num1, const Positive_int& num2);

  ~Positive_int();
};

#endif
```

`.h` отвечает на вопрос:

```text
что класс умеет?
```

---

## `positive_int.cpp`

Тут находится реализация.

Подключение:

```cpp
#include "positive_int.h"
```

Метод класса снаружи пишется через `::`:

```cpp
void Positive_int::reinitialize(int n) {
  ...
}
```

`::` означает:

```text
эта функция относится к классу Positive_int
```

Конструктор:

```cpp
Positive_int::Positive_int(int n, bool type)
    : num(n), array_type(type) {
  ...
}
```

Деструктор:

```cpp
Positive_int::~Positive_int() {
  ...
}
```

`gcd` и `lcm` — `friend`, но они не являются методами класса, поэтому:

```cpp
int gcd(const Positive_int& num1, const Positive_int& num2) {
  ...
}
```

без `Positive_int::`.

`.cpp` отвечает на вопрос:

```text
как класс это делает?
```

---

## `main.cpp`

Только использование класса:

```text
создать объекты
проверить копирование
найти НОД/НОК
реинициализировать
заменить множитель
показать результат
```

`main.cpp` не должен знать внутреннюю механику класса.

---

# Как всё собирается

```text
main.cpp         -> main.o
positive_int.cpp -> positive_int.o

main.o + positive_int.o
        ↓
   исполняемый файл
```

Header нужен обоим `.cpp`, чтобы компилятор знал объявления.

---

# Makefile — смысл

Makefile описывает:

```text
что получить
↓
из чего получить
↓
какой командой
```

Общая форма:

```make
цель: зависимости
	команда
```

Обязательные флаги:

```text
-Wall   -> основные warnings
-Wextra -> дополнительные warnings
-Werror -> warning считается ошибкой
```

Debug:

```text
-g -O0
```

Release:

```text
-O2
```

---

# Что тренирует эта задача

- класс и инкапсуляцию;
- динамический C-style массив;
- `new[] / delete[]`;
- constructor;
- copy constructor;
- destructor;
- deep copy;
- `operator=`;
- `this`;
- `friend`;
- `const`;
- работу с состоянием объекта;
- разбиение `.h / .cpp / main.cpp`;
- линковку;
- Makefile.

## Главная идея

Объект сам отвечает за:

```text
свои данные
+
свою динамическую память
+
согласованность своего состояния
```

Если объект говорит, что он представляет число `12`, то `num`, массив множителей, его размер и режим сортировки должны соответствовать друг другу.
