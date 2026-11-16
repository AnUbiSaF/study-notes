# Задача 02 — Polynomial

[[Задачи по C++|← К списку задач]]

> [!abstract] Суть задачи
> Реализовать класс многочлена с собственным хранением коэффициентов, глубоким копированием, перегрузкой операторов, производной и вычислением значения методом Горнера.

## Исходный код

Все файлы приведены без изменений в сворачиваемых блоках Obsidian.

> [!example]- `polynomial.h`
> ```cpp
> #include <iostream>
> #ifndef POLYNOMIAL_H
> #define POLYNOMIAL_H
>
> class Polynomial {
>     private:
>         mutable double cache_x;
>         mutable bool cache_valid;
>         mutable double cache_value;
>         double* coefficents;
>         int size;
>     public:
>         Polynomial(const double in_array[], int size);
>         Polynomial(const Polynomial& other);
>         ~Polynomial();
>         void print_polynominal() const;
>         double value(const double x) const;
>         Polynomial derivative() const;
>         Polynomial& operator=(const Polynomial& other);
>         double& operator[](size_t index);
>         const double& operator[](size_t index) const;
>         Polynomial& operator+=(const Polynomial& other);
>         Polynomial operator+(const Polynomial& other) const;
>         Polynomial& operator-=(const Polynomial& other);
>         Polynomial operator-(const Polynomial& other) const;
>         Polynomial& operator*=(const Polynomial& other);
>         Polynomial operator*(const Polynomial& other) const;
>         Polynomial operator-() const;
>         bool operator==(const Polynomial& other) const;
>         bool operator!=(const Polynomial& other) const;
> };
>
> #endif
> ```

> [!example]- `polynomial.cpp`
> ```cpp
> #include <iostream>
> #include "polynomial.h"
>
> Polynomial::Polynomial(const double in_array[], int size)
>     : size(size), cache_valid(false) {
>     coefficents = new double[size];
>     for (int i = 0; i < size; i++) coefficents[i] = in_array[i];
> }
> Polynomial::Polynomial(const Polynomial& other)
>     : size(other.size), cache_valid(false) {
>     coefficents = new double[size];
>     for (int i = 0; i < size; i++) coefficents[i] = other.coefficents[i];
> }
> Polynomial::~Polynomial() { delete[] coefficents; }
> void Polynomial::print_polynominal() const {
>     bool first = true;
>     for (int i = size - 1; i >= 0; i--) {
>         if (coefficents[i] == 0) continue;
>         if (coefficents[i] > 0 && first == false) std::cout << " + ";
>         if (i == 0) std::cout << coefficents[i];
>         else if (i == 1) std::cout << coefficents[i] << "x";
>         else std::cout << coefficents[i] << "x^" << i;
>         first = false;
>     }
>     if (first == true) std::cout << "0";
>     std::cout << "\n";
> }
> Polynomial Polynomial::derivative() const {
>     if (size == 1) { double zero[] = {0}; return Polynomial(zero, 1); }
>     double* coefficents_new = new double[size - 1];
>     for (int i = size - 1; i > 0; i--)
>         coefficents_new[i - 1] = coefficents[i] * i;
>     Polynomial result(coefficents_new, size - 1);
>     delete[] coefficents_new;
>     return result;
> }
> Polynomial& Polynomial::operator=(const Polynomial& other) {
>     if (&other == this) return *this;
>     delete[] coefficents;
>     size = other.size;
>     coefficents = new double[size];
>     std::memcpy(coefficents, other.coefficents, size * sizeof(double));
>     cache_valid = false;
>     return *this;
> }
> double& Polynomial::operator[](size_t index) {
>     cache_valid = false;
>     return coefficents[index];
> }
> const double& Polynomial::operator[](size_t index) const { return coefficents[index]; }
> Polynomial& Polynomial::operator+=(const Polynomial& other) {
>     if (size < other.size) {
>         double* new_coeff = new double[other.size]{0};
>         std::memcpy(new_coeff, coefficents, size * sizeof(double));
>         delete[] coefficents;
>         coefficents = new_coeff;
>         size = other.size;
>     }
>     for (int i = 0; i < other.size; i++) coefficents[i] += other.coefficents[i];
>     cache_valid = false;
>     return *this;
> }
> Polynomial Polynomial::operator+(const Polynomial& other) const {
>     Polynomial result(*this); result += other; return result;
> }
> Polynomial& Polynomial::operator-=(const Polynomial& other) {
>     if (size < other.size) {
>         double* new_coeff = new double[other.size]{0};
>         std::memcpy(new_coeff, coefficents, size * sizeof(double));
>         delete[] coefficents; coefficents = new_coeff; size = other.size;
>     }
>     for (int i = 0; i < other.size; i++) coefficents[i] -= other.coefficents[i];
>     cache_valid = false; return *this;
> }
> Polynomial Polynomial::operator-(const Polynomial& other) const {
>     Polynomial result(*this); result -= other; return result;
> }
> Polynomial& Polynomial::operator*=(const Polynomial& other) {
>     double* new_coeff = new double[other.size + size - 1]{0};
>     for (int i = 0; i < size; i++)
>         for (int j = 0; j < other.size; j++)
>             new_coeff[i + j] += coefficents[i] * other.coefficents[j];
>     delete[] coefficents;
>     coefficents = new_coeff; size = other.size + size - 1;
>     cache_valid = false; return *this;
> }
> Polynomial Polynomial::operator*(const Polynomial& other) const {
>     Polynomial result(*this); result *= other; return result;
> }
> Polynomial Polynomial::operator-() const {
>     Polynomial result(*this);
>     for (int i = 0; i < result.size; i++) result.coefficents[i] = -result.coefficents[i];
>     return result;
> }
> bool Polynomial::operator==(const Polynomial& other) const {
>     if (size != other.size) return false;
>     for (int i = 0; i < size; i++) if (coefficents[i] != other.coefficents[i]) return false;
>     return true;
> }
> double Polynomial::value(const double x) const {
>     if (cache_valid && cache_x == x) return cache_value;
>     double result = coefficents[size - 1];
>     for (int i = size - 2; i >= 0; i--) result = result * x + coefficents[i];
>     cache_x = x; cache_valid = true; cache_value = result;
>     return result;
> }
> bool Polynomial::operator!=(const Polynomial& other) const { return !(*this == other); }
> ```

> [!example]- `main.cpp`
> ```cpp
> #include <iostream>
> #include "polynomial.h"
>
> int main(void) {
>     double arr[] = {1.0, 2.0, 3.0};
>     double arr2[] = {1.0, 3.0};
>     Polynomial a(arr, 3);
>     a.print_polynominal();
>     Polynomial b = a;
>     Polynomial c = a.derivative();
>     c[0] = 10;
>     const Polynomial d(arr, 3);
>     double x = d[0];
>     Polynomial e(arr2, 2);
>     e += a;
>     Polynomial i = e + a;
>     i -= a;
>     double arr3[] = {2.0, 5.0, 3.0};
>     Polynomial test1(arr3, 3), test2(arr3, 3);
>     test1 *= test2;
>     Polynomial test3 = test2 * test2;
>     Polynomial test5 = -test3;
>     std::cout << (test2 == test2) << '\n';
>     std::cout << (test5 != test3) << '\n';
>     std::cout << i.value(2) << '\n';
>     return 0;
> }
> ```

> [!example]- `Makefile`
> ```makefile
> all: main
>
> main: main.o polynomial.o
> 	g++ main.o polynomial.o -o main
>
> main.o: main.cpp polynomial.h
> 	g++ -g -O0 -c main.cpp
>
> polynomial.o: polynomial.cpp polynomial.h
> 	g++ -g -O0 -c polynomial.cpp
>
> clean:
> 	rm -f *.o main
> ```

## 1. Представление полинома

Полином степени не выше `size - 1` хранится в динамическом массиве:

$$
P(x) = a_0 + a_1x + \dots + a_{n-1}x^{n-1}.
$$

`coefficents[i]` — коэффициент при `x^i`, а `size` — количество коэффициентов. Например, `{1, 2, 3}` задаёт `1 + 2x + 3x²`.

```cpp
class Polynomial {
private:
    mutable double cache_x;
    mutable bool cache_valid;
    mutable double cache_value;
    double* coefficents;
    int size;

public:
    Polynomial(const double in_array[], int size);
    Polynomial(const Polynomial& other);
    ~Polynomial();
    Polynomial& operator=(const Polynomial& other);

    void print_polynominal() const;
    double value(double x) const;
    Polynomial derivative() const;
    double& operator[](size_t index);
    const double& operator[](size_t index) const;
    Polynomial& operator+=(const Polynomial& other);
    Polynomial operator+(const Polynomial& other) const;
    Polynomial& operator-=(const Polynomial& other);
    Polynomial operator-(const Polynomial& other) const;
    Polynomial& operator*=(const Polynomial& other);
    Polynomial operator*(const Polynomial& other) const;
    Polynomial operator-() const;
    bool operator==(const Polynomial& other) const;
    bool operator!=(const Polynomial& other) const;
};
```

`cache_x`, `cache_value` и `cache_valid` запоминают последнее вычисление `value(x)`.

---

## 2. Управление памятью

Класс вручную владеет массивом `double*`, поэтому реализует **Rule of Three**: деструктор, конструктор копирования и копирующее присваивание.

Обычный и копирующий конструкторы должны выделять новый массив и копировать коэффициенты. Это глубокое копирование: изменение копии не меняет оригинал.

```cpp
Polynomial::~Polynomial() {
    delete[] coefficents;
}

Polynomial& Polynomial::operator=(const Polynomial& other) {
    if (this == &other)
        return *this;

    double* new_coefficents = new double[other.size];
    std::memcpy(new_coefficents, other.coefficents,
                other.size * sizeof(double));
    delete[] coefficents;
    coefficents = new_coefficents;
    size = other.size;
    cache_valid = false;
    return *this;
}
```

Сначала выделяется новая память, затем удаляется старая: так объект остаётся корректным, если `new` выбросит исключение. Для `std::memcpy` нужен `#include <cstring>`.

---

## 3. Производная и вывод

Производная считается по правилу:

$$
(a_i x^i)' = i a_i x^{i-1}.
$$

```cpp
Polynomial Polynomial::derivative() const {
    if (size == 1) {
        double zero[] = {0};
        return Polynomial(zero, 1);
    }

    double* result = new double[size - 1];
    for (int i = 1; i < size; ++i)
        result[i - 1] = coefficents[i] * i;

    Polynomial derivative(result, size - 1);
    delete[] result;
    return derivative;
}
```

`print_polynominal()` обходит массив от старшей степени к младшей и пропускает нулевые коэффициенты. Если все коэффициенты нулевые, выводится `0`.

---

## 4. Перегрузка операторов

| Операция | Логика |
|---|---|
| `a[i]` | доступ к коэффициенту при `x^i` |
| `a += b`, `a -= b` | поэлементное сложение / вычитание с расширением массива |
| `a + b`, `a - b` | копия `a`, затем `+=` / `-=` |
| `a *= b` | свёртка коэффициентов при умножении |
| `a * b` | копия и `*=` |
| `-a` | смена знака коэффициентов в копии |
| `a == b`, `a != b` | сравнение коэффициентов / отрицание равенства |

Два `operator[]` нужны для чтения из `const`-объекта и изменения обычного:

```cpp
double& operator[](size_t index);
const double& operator[](size_t index) const;
```

Неконстантная версия должна сбрасывать кеш, потому что через возвращённую ссылку коэффициент может измениться.

При умножении членов `a_i x^i` и `b_j x^j` получается `a_i b_j x^{i+j}`, поэтому вклад идёт в `result[i + j]`:

```cpp
for (int i = 0; i < size; ++i)
    for (int j = 0; j < other.size; ++j)
        new_coeff[i + j] += coefficents[i] * other.coefficents[j];
```

Размер результата равен `size + other.size - 1`.

---

## 5. Метод Горнера и кеш

Вычисление многочлена выполняется за `O(n)` по схеме Горнера:

$$
P(x) = a_0 + x(a_1 + x(a_2 + \dots + x a_{n-1})).
$$

```cpp
double Polynomial::value(double x) const {
    if (cache_valid && cache_x == x)
        return cache_value;

    double result = coefficents[size - 1];
    for (int i = size - 2; i >= 0; --i)
        result = result * x + coefficents[i];

    cache_x = x;
    cache_value = result;
    cache_valid = true;
    return result;
}
```

Для `{1, 2, 3}` при `x = 2` получается `17`. Поля кеша помечены `mutable`, чтобы `value(...) const` мог обновлять служебный кеш, не меняя сам полином.

---

## 6. Ограничения исходной реализации

1. Для `std::memcpy` в `polynomial.cpp` нужен `#include <cstring>`.
2. Конструктор должен запрещать `size < 1`: иначе `value()` обратится к `coefficents[size - 1]`.
3. `operator[]` не проверяет границы, поэтому неверный индекс приводит к неопределённому поведению.
4. `{1, 2}` и `{1, 2, 0}` математически равны, но сравнение вернёт `false`, если не нормализовать старшие нули.
5. Сохранённая ссылка `double& r = p[0]` может изменить коэффициент после вычисления `value(x)` и оставить кеш устаревшим.
6. Упрощённый вывод отрицательных коэффициентов может форматировать знаки не так, как ожидается.

---

## 7. Сборка и проверка

```makefile
all: main

main: main.o polynomial.o
	g++ main.o polynomial.o -o main

main.o: main.cpp polynomial.h
	g++ -g -O0 -c main.cpp

polynomial.o: polynomial.cpp polynomial.h
	g++ -g -O0 -c polynomial.cpp

clean:
	rm -f *.o main
```

```bash
make
./main
make clean
```

Полезные проверки:

- `{1, 2, 3}` представляет `1 + 2x + 3x²`;
- производная — `2 + 6x`;
- `value(2)` равно `17`;
- `(2 + 5x + 3x²)²` равно `4 + 20x + 37x² + 30x³ + 9x⁴`.

## Краткая шпаргалка

- Глубокая копия создаёт новый массив, а не копирует адрес.
- `+=`, `-=`, `*=` меняют левый объект и возвращают `Polynomial&`.
- `+`, `-`, `*` возвращают новый объект.
- `const`-перегрузка `[]` разрешает чтение, но не изменение.
- `mutable` подходит для кеша в `const`-методе.
- Метод Горнера вычисляет полином за линейное время.
