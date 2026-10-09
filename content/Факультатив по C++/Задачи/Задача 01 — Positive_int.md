## 1. Что хранит класс

Класс представляет **положительное целое число** и его разложение на простые множители.

```cpp
int num;          // само число
int array_size;   // количество простых множителей
int* array;       // C-массив простых множителей
bool array_type;  // режим хранения
```

Пример:

```text
60 = 2 * 2 * 3 * 5
array = [2, 2, 3, 5]
```

---

## 2. Конструктор

```cpp
Positive_int(int n, bool type = false);
```

Основные действия:

```text
проверить n > 0
→ сохранить num и array_type
→ построить массив простых множителей
```

Для некорректного числа лучше не создавать объект:

```cpp
if (n <= 0) {
  throw std::invalid_argument("number must be positive");
}
```

Нужен:

```cpp
#include <stdexcept>
```

> [!WARNING]
> `unsigned int` не заменяет проверку: `0` всё равно допустим, а отрицательное число может преобразоваться в большое положительное.

---

## 3. Поиск простых множителей

Алгоритм перебирает делители начиная с `2`.

```text
пока число делится на divisor:
    записать divisor
    поделить число на divisor
после этого увеличить divisor
```

Используются два прохода:

1. посчитать количество множителей;
2. выделить массив нужного размера и заполнить его.

> [!NOTE]
> Так как `divisor` только увеличивается, множители сразу получаются по возрастанию.
> Дополнительный `std::sort()` после `find_prime_divisors()` не нужен.

`find_prime_divisors()` — служебная функция, поэтому лучше держать её в `private`.

---

## 4. Копирование

Так как внутри есть динамический массив, нужно **глубокое копирование**.

### Copy constructor

```cpp
Positive_int(const Positive_int& other);
```

Нужно:

```text
скопировать num
скопировать array_size
скопировать array_type
выделить новый array
скопировать элементы
```

Можно через:

```cpp
std::memcpy(array, other.array, array_size * sizeof(int));
```

Для этого:

```cpp
#include <cstring>
```

> [!WARNING]
> Третий аргумент `memcpy` — количество **байт**, а не элементов.

---

## 5. Оператор присваивания

```cpp
Positive_int& operator=(const Positive_int& other);
```

Сначала нужна защита от:

```cpp
a = a;
```

```cpp
if (this == &other) {
  return *this;
}
```

Далее:

```text
удалить старый массив
→ скопировать поля
→ выделить новый массив
→ скопировать элементы
→ return *this
```

---

## 6. Деструктор

```cpp
~Positive_int() {
  delete[] array;
}
```

Нужен, потому что память выделяется через `new[]`.

---

## 7. gcd как метод класса

Лучше:

```cpp
int gcd(const Positive_int& other) const;
```

Вызов:

```cpp
num1.gcd(num2);
```

Внутри:

```text
this  -> num1
other -> num2
```

Последний `const` означает, что метод не изменяет объект слева от точки.

### Случай 1: оба массива отсортированы

Используются два индекса:

```text
array[i] == other.array[j] -> множитель общий, result *= ..., ++i, ++j
array[i] <  other.array[j] -> ++i
array[i] >  other.array[j] -> ++j
```

Сложность:

```text
O(n + m)
```

> [!WARNING]
> Писать:
>
> ```cpp
> int i = 0, j = 0;
> ```
>
> а не `int i, j = 0;`, потому что во втором случае `i` не инициализирован.

### Случай 2: хотя бы один массив неотсортирован

Используется массив `used`, чтобы один множитель второго числа не использовать дважды.

```text
для каждого array[i]:
    найти равный other.array[j], который ещё не использован
    умножить result
    отметить used[j]
```

---

## 8. lcm

```cpp
int lcm(const Positive_int& other) const;
```

Формула:

```text
LCM(a, b) = |a * b| / GCD(a, b)
```

Внутри метода:

```cpp
std::abs(num * other.num) / gcd(other)
```

> [!WARNING]
> Не перепутать с `other.num * other.num`.

---

## 9. reinitialize

```cpp
void reinitialize(int n);
```

Логика:

```text
проверить n > 0
→ изменить num
→ удалить старый array
→ заново найти простые множители
```

Дополнительная сортировка не нужна, потому что `find_prime_divisors()` уже строит массив по возрастанию.

---

## 10. Замена множителя

```cpp
void divisor_replace(int from, int to);
```

После замены нужно пересчитать число:

```text
num = произведение всех элементов array
```

Если режим класса требует сортировки после ручного изменения массива, массив можно отсортировать здесь.

---

## 11. Почему без `friend`

Раньше:

```cpp
friend int gcd(...);
```

Лучше:

```cpp
int gcd(const Positive_int& other) const;
```

Причина: `friend` даёт внешней функции доступ к `private` и ослабляет инкапсуляцию.

Метод класса естественно вызывается так:

```cpp
num1.gcd(num2);
num1.lcm(num2);
```

---

## 12. Разделение по файлам

### `positive_int.h`

Только объявление класса и методов.

### `positive_int.cpp`

Реализации:

```cpp
Positive_int::Positive_int(...)
int Positive_int::gcd(...) const
...
```

Класс второй раз объявлять не надо.

### `main.cpp`

Только использование класса.

---

## 13. Makefile

Нужно собрать оба `.cpp`:

```text
main.cpp         -> main.o
positive_int.cpp -> positive_int.o
```

а затем:

```text
main.o + positive_int.o -> main
```

Пример:

```make
all: main

main: main.o positive_int.o
	g++ main.o positive_int.o -o main

main.o: main.cpp positive_int.h
	g++ -g -O0 -c main.cpp

positive_int.o: positive_int.cpp positive_int.h
	g++ -g -O0 -c positive_int.cpp

clean:
	rm -f *.o main
```

---

# Главное, что нужно запомнить

```text
new[]       -> delete[]
динамический массив -> deep copy
метод класса -> object.method(other)
this -> объект слева от точки
const & -> без копирования и без изменения аргумента
method(...) const -> не изменяет текущий объект
memcpy -> количество байт
sorted gcd -> два указателя
unsorted gcd -> used
.h -> интерфейс
.cpp -> реализация
```
