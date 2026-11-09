### Założenia projektowania kodu o poprawności wynikającej z konstrukcji

Cel: Budować kod w Pythonie (Airflow, Psycopg, migracje danych), w którym poprawność najmniejszych metod wynika z ich konstrukcji, a większe operacje można tworzyć przez składanie sprawdzonych elementów, bez konieczności ponownego testowania ich wewnętrznej logiki.

### 1\. Podstawowe zasady

1\. Atomowość odpowiedzialności (Single Responsibility) – każda metoda realizuje jedną, ściśle określoną operację.

2\. Poprawność przez konstrukcję (Correctness by Construction) – kod projektujemy tak, aby określone błędy były niemożliwe dzięki zastosowanym mechanizmom, a nie wykrywane dopiero przez testy.

3\. Projektowanie przez kontrakty (Design by Contract) – każda metoda ma jasno określone warunki wejściowe, wynik, gwarancje oraz założenia.

4\. Eliminowanie niepoprawnych stanów (Make Illegal States Unrepresentable) – wykorzystujemy typy, walidację i ograniczone interfejsy, aby uniemożliwiać nieprawidłowe użycie metod.

5\. Funkcje czyste (Pure Functions) – oddzielamy deterministyczną logikę transformacji od operacji na bazie danych i innych skutków ubocznych.

6\. Wykorzystywanie istniejących gwarancji – opieramy kod na mechanizmach PostgreSQL i Psycopg, np. transakcjach, `PRIMARY KEY`, `ON CONFLICT`, zamiast implementować je samodzielnie.

7\. Idempotencja – ponowne wykonanie operacji nie powinno prowadzić do niepożądanych zmian, co ma szczególne znaczenie przy ponowieniach zadań Airflow.

8\. Poprawność przez kompozycję (Compositional Reasoning) – większe operacje budujemy z mniejszych, wykorzystując ich kontrakty, bez ponownej analizy implementacji.

### 2\. Zasady implementacyjne

Każda metoda powinna:

* Mieć jedną odpowiedzialność i minimalną liczbę możliwych stanów.

* Posiadać jednoznaczny kontrakt wejścia i wyjścia.

* Wykorzystywać gotowe gwarancje języka, bibliotek lub bazy danych.

* Minimalizować rozgałęzienia, mutowalność i efekty uboczne.

* Ukrywać szczegóły implementacyjne za wąskim interfejsem.

* Być możliwa do przeanalizowania i zweryfikowania niezależnie.

* Nie wymagać ponownego testowania przy każdym wykorzystaniu, jeśli jej kontrakt i założenia pozostają niezmienione.

### 3\. Docelowa architektura

Warstwa 3 — Orkiestracja (Airflow)

Uruchamianie gotowych procesów, harmonogram, retries

Warstwa 2 — Zaufane prymitywy migracyjne

Pobieranie, walidacja, transformacja, zapis, checkpoint

Warstwa 1 — Gwarancje technologiczne

Python, Psycopg, PostgreSQL, transakcje, ograniczenia SQL

### 4\. Zasada weryfikacji

Prymityw weryfikujemy raz, a następnie używamy go wielokrotnie na podstawie jego kontraktu.

Ponowna weryfikacja jest potrzebna, gdy zmienia się implementacja, kontrakt lub jego założenia. Nowe procesy nadal wymagają sprawdzenia poprawności kompozycji i logiki biznesowej.

### 5\. Najważniejsza idea

Nie chodzi o pisanie jak najkrótszych metod.

Chodzi o minimalizowanie liczby możliwych stanów, ścieżek wykonania i założeń, które trzeba analizować, aby uzasadnić poprawność.

Ostateczna zasada brzmi:

> Projektuj najmniejsze elementy tak, aby ich poprawność wynikała z konstrukcji. Następnie buduj większe elementy wyłącznie z operacji o znanych kontraktach, przenosząc uzasadnienie poprawności z poziomu implementacji na poziom kompozycji.

To podejście można określić jako Correctness by Construction + Design by Contract + Compositional Reasoning, realizowane poprzez własną warstwę zaufanych prymitywów programistycznych.
