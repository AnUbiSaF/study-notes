# C++ — занятие 2

[[Практики по C++|← К списку практик]]

## `new` / `delete`

```cpp
int* p = new int(100);   // один int со значением 100
int* a = new int[100];   // массив из 100 int

delete p;
delete[] a;
```

`new int(100)` — не массив.

## Ссылки

```cpp
int x = 5;
int& r = x;
```

`r` — другое имя для `x`.

```cpp
r = 10;   // x тоже станет 10
```

В функции:

```cpp
void increment(int& x) {
    ++x;
}
```

## Указатель vs ссылка

```cpp
int* p = nullptr;
```

Указатель может быть `nullptr`, поэтому:

```cpp
if (p) {
    ++(*p);
}
```

- `p` — адрес
- `*p` — объект по адресу

Ссылка должна быть привязана к существующему объекту.

## Dangling reference

```cpp
int* p = new int(100);
int& r = *p;

delete p;
```

После `delete` объект уничтожен, а `r` стала dangling reference.

Использование `r` после этого — UB.

## Copy constructor

Если класс хранит динамическую память, обычное копирование указателей опасно.

```cpp
Student(const Student& other)
    : n(other.n)
{
    name = new char[std::strlen(other.name) + 1];
    std::strcpy(name, other.name);

    grades = new int[n];
    for (std::size_t i = 0; i < n; ++i)
        grades[i] = other.grades[i];
}
```

Это deep copy: у объектов разные области памяти.

## `copy ctor` vs `operator=`

```cpp
Student s2 = s1;  // copy constructor

Student s3("Temp", 1);
s3 = s1;          // operator=
```

## Copy-and-swap

```cpp
Student& operator=(Student other) {
    swap(*this, other);
    return *this;
}
```

`other` — копия правого объекта.

После `swap`:
- текущий объект получает новые ресурсы;
- `other` получает старые;
- при выходе из функции `other` уничтожается и освобождает старую память.

## `swap`

```cpp
friend void swap(Student& a, Student& b) noexcept {
    std::swap(a.name, b.name);
    std::swap(a.grades, b.grades);
    std::swap(a.n, b.n);
}
```

Для указателей `std::swap` меняет местами адреса, а не двигает данные в heap.

`noexcept` — гарантия, что функция не выбросит исключение.

## UB и AddressSanitizer

Примеры UB:
- разыменование `nullptr`;
- использование памяти после `delete`;
- dangling reference.

Проверка:

```bash
clang++ -fsanitize=address -g demo.cpp -o demo
./demo
```

ASan показывает место невалидного доступа к памяти.

---

# Makefile — база

## Общая форма

```make
цель: зависимости
	команда
```

Пример:

```make
app:
	g++ main.cpp utils.cpp -o app
```

```bash
make app
```

запустит команду под целью `app`.

## Переменные

```make
CXX = g++
WARNINGS = -Wall -Wextra -Werror
```

Использование:

```make
$(CXX) $(WARNINGS) main.cpp -o app
```

## Обязательные флаги

```text
-Wall   — основные предупреждения
-Wextra — дополнительные предупреждения
-Werror — считать warnings ошибками
```

## Debug / Release

Debug:

```text
-g   — добавить отладочную информацию
-O0  — не оптимизировать
```

Release:

```text
-O2  — оптимизировать программу
```

Базовый Makefile:

```make
CXX = g++
WARNINGS = -Wall -Wextra -Werror

debug:
	$(CXX) $(WARNINGS) -g -O0 main.cpp utils.cpp -o app

release:
	$(CXX) $(WARNINGS) -O2 main.cpp utils.cpp -o app

clean:
	rm -f app

.PHONY: debug release clean
```

Команды:

```bash
make debug
make release
make clean
```

## `.o` и зависимости

```bash
g++ -c main.cpp    # main.cpp -> main.o
g++ -c utils.cpp   # utils.cpp -> utils.o
```

Потом объектные файлы линкуются:

```bash
g++ main.o utils.o -o app
```

Пример зависимостей:

```make
app: main.o utils.o
	g++ main.o utils.o -o app

main.o: main.cpp
	g++ -c main.cpp

utils.o: utils.cpp
	g++ -c utils.cpp
```

`make` сам проверяет, какие зависимости устарели, и пересобирает только нужные части.

Схема:

```text
main.cpp  -> main.o \\
                    -> app
utils.cpp -> utils.o /
```

`clean` обычно удаляет результаты сборки:

```make
clean:
	rm -f *.o app
```

`.PHONY: clean` означает, что `clean` — служебная цель, а не файл.
