# Standard projektowania kodu: Od poprawności przez konstrukcję do kompozycji procesów

> **Cel dokumentu:** Zdefiniowanie zasad tworzenia niezawodnego kodu, w którym określone klasy błędów są wykluczone przez samą budowę podstawowych elementów (prymitywów), a złożone procesy powstają poprzez bezpieczne składanie uprzednio zweryfikowanych komponentów na podstawie ich kontraktów.

Zamiast polegać na rozbudowanym testowaniu setek kombinacji ścieżek wykonania, dążymy do **minimalizacji liczby możliwych stanów, rozgałęzień oraz ukrytych założeń**. Standard dzieli stosowane techniki na trzy spójne kategorie, odpowiadające kolejnym poziomom budowy systemu:

| Kategoria | Poziom | Kluczowe techniki |
|---|---|---|
| **I. Correctness by Construction** | Wnętrze pojedynczego prymitywu | 1. Atomowość odpowiedzialności (*Single Responsibility*)<br>2. Eliminowanie niepoprawnych stanów (*Make Illegal States Unrepresentable*)<br>3. Funkcje czyste (*Pure Functions*)<br>4. Wykorzystywanie istniejących gwarancji (*Underlying Guarantees*) |
| **II. Design by Contract & Idempotency** | Interfejs i zachowanie na zewnątrz | 5. Projektowanie przez kontrakty (*Design by Contract*)<br>6. Idempotencja (*Idempotency*) |
| **III. Compositional Reasoning** | Składanie prymitywów w procesy | 7. Poprawność przez kompozycję (*Compositional Reasoning*) |

---

## I. Konstrukcja pojedynczego prymitywu (*Correctness by Construction*)

Pierwsza kategoria obejmuje techniki kształtujące wewnętrzną budowę pojedynczej metody, funkcji lub struktury danych. Ich zadaniem jest skonstruowanie prymitywu w taki sposób, aby popełnienie określonych błędów wewnątrz niego było fizycznie niemożliwe.

### 1. Atomowość odpowiedzialności (*Single Responsibility Principle*)

* **Istota zasady:**
  Każdy prymityw (metoda, funkcja) odpowiada za realizację dokładnie jednej, dobrze zdefiniowanej operacji. Miarą atomowości nie jest wyłącznie mała liczba linii kodu, lecz przede wszystkim **minimalna liczba rozgałęzień warunkowych (`if/else`, `switch`, `try/catch`) oraz stanów przejściowych**.
* **Realizacja w praktyce:**
  * Rozbijamy metody łączące wiele zadań (np. jednoczesne pobieranie danych, ich transformację i zapis) na osobne, niezależne operacje.
  * Unikamy flag sterujących zachowaniem metody (parametrów zmieniających ścieżkę wykonania wewnątrz funkcji).
* **Efekt architektoniczny:**
  Zredukowanie liczby ścieżek wykonania do minimum sprawia, że zachowanie prymitywu jest w pełni przejrzyste, a wykazanie jego poprawności w izolacji staje się trywialne.

---

### 2. Eliminowanie niepoprawnych stanów (*Make Illegal States Unrepresentable*)

* **Istota zasady:**
  Projektujemy typy, struktury danych oraz obiekty konfiguracyjne tak, aby stan nieprawidłowy, niekompletny lub wewnętrznie sprzeczny w ogóle nie mógł zostać utworzony w pamięci programu.
* **Realizacja w praktyce:**
  * Stosujemy podejście **parsowania zamiast walidacji (*Parse, don't validate*)** na granicy systemu: surowe, niepewne dane (np. luźne słowniki, napisy, rekordy zewnętrzne) są weryfikowane raz na wejściu i przekształcane w silnie typowane struktury domenowe.
  * Wymuszamy spójność danych w momencie konstrukcji obiektu — jeśli dane są niekompletne lub sprzeczne, obiekt nie zostaje utworzony.
  * Ograniczamy mutowalność struktur danych po ich utworzeniu (*immutability*).
* **Efekt architektoniczny:**
  Sam fakt istnienia obiektu stanowi gwarancję poprawności zawartych w nim danych. Kolejne metody operujące na tym obiekcie są zwolnione z konieczności wielokrotnego wykonywania defensywnych sprawdzeń (np. czy wymagane pola istnieją lub mają właściwy format).

---

### 3. Funkcje czyste (*Pure Functions*)

* **Istota zasady:**
  Oddzielamy logikę obliczeniową, transformację danych oraz podejmowanie decyzji od operacji wejścia/wyjścia (I/O) zmieniających stan zewnętrzny.
* **Realizacja w praktyce:**
  * **Determinizm:** Funkcja czysta dla tych samych argumentów wejściowych zawsze zwraca identyczny wynik. Jej działanie nie zależy od zmiennych globalnych, bieżącego czasu systemowego, stanu bazy danych ani zasobów sieciowych.
  * **Brak efektów ubocznych (*No Side-Effects*):** Funkcja nie modyfikuje żadnych zasobów zewnętrznych ani obiektów przekazanych do niej jako argumenty — zwraca wyłącznie nową wartość wynikową.
* **Efekt architektoniczny:**
  Cała logika przekształcania danych staje się w 100% przewidywalna, niezależna od środowiska wykonawczego i odporna na awarie infrastruktury. Może być weryfikowana bez konieczności uruchamiania baz danych czy usług zewnętrznych.

---

### 4. Wykorzystywanie istniejących gwarancji (*Leveraging Underlying Guarantees*)

* **Istota zasady:**
  Nie implementujemy ręcznie w kodzie aplikacji mechanizmów bezpieczeństwa i spójności, które są natywnie, formalnie i niezawodnie gwarantowane przez niższe warstwy technologiczne.
* **Realizacja w praktyce:**
  * Zamiast pisać w kodzie aplikacji własne pętle sprawdzające istnienie rekordów przed zapisem (podatne na wyścigi i niespójność przy awarii), delegujemy wymuszanie unikalności i integralności do silnika bazodanowego (**klucze główne, ograniczenia `UNIQUE`, `NOT NULL`, klucze obce**).
  * Zamiast ręcznie zarządzać częściowym wycofywaniem zmian po błędzie, opieramy operacje zapisu na **transakcjach bazodanowych (gwarancje ACID)** oraz atomowych instrukcjach silnika danych.
  * Wykorzystujemy gwarancje systemu typów oraz sprawdzonych bibliotek standardowych zamiast tworzyć własne, niskopoziomowe implementacje.
* **Efekt architektoniczny:**
  Eliminujemy z kodu aplikacji najbardziej złożoną i podatną na błędy logikę synchronizacji oraz obsługi awarii, zastępując ją deklaratywnymi gwarancjami platformy.

---

## II. Interfejs i gwarancje zachowania (*Design by Contract & Idempotency*)

Druga kategoria definiuje sposób, w jaki poprawnie skonstruowany prymityw komunikuje się ze światem zewnętrznym oraz jakie gwarancje zapewnia przy wywołaniu (w tym wywołaniu wielokrotnym).

### 5. Projektowanie przez kontrakty (*Design by Contract*)

* **Istota zasady:**
  Każda operacja komunikuje się z otoczeniem wyłącznie poprzez jawny, ściśle określony kontrakt, całkowicie ukrywając szczegóły swojej wewnętrznej implementacji.
* **Realizacja w praktyce:**
  * **Warunki wstępne (*Preconditions*):** Precyzyjnie określają wymagania wobec danych wejściowych i stanu początkowego. Naruszenie warunków wstępnych powoduje **natychmiastowe przerwanie wykonania (*fail-fast*)** z jednoznacznym błędem — operacja nigdy nie próbuje domyślać się intencji ani cicho naprawiać nieprawidłowych danych.
  * **Warunki końcowe (*Postconditions*) i niezmienniki (*Invariants*):** Definiują gwarantowany stan końcowy, strukturę zwracanego wyniku oraz właściwości systemu, które pozostają nienaruszone po zakończeniu operacji.
  * **Wąski interfejs i hermetyzacja:** Kod wywołujący zna wyłącznie sygnaturę oraz kontrakt operacji; nie musi wiedzieć, jak operacja jest zaimplementowana pod spodem.
* **Efekt architektoniczny:**
  Powstaje wyraźna granica odpowiedzialności między wywołującym a wywoływanym prymitywem. Wnętrze prymitywu można bezpiecznie refaktoryzować lub optymalizować bez wpływu na resztę systemu, dopóki jego kontrakt pozostaje nienaruszony.

---

### 6. Idempotencja (*Idempotency*)

* **Istota zasady:**
  Dla wszystkich operacji modyfikujących stan zewnętrzny (operacje I/O, zapis, aktualizacja lub usuwanie danych) kontrakt zostaje rozszerzony o gwarancję idempotencji: **jednokrotne oraz wielokrotne wykonanie operacji z tymi samymi parametrami wejściowymi zawsze doprowadza system do dokładnie tego samego stanu docelowego**.
* **Realizacja w praktyce:**
  * Operacje zapisu projektujemy jako atomowe zastąpienie stanu lub warunkową aktualizację opartą na naturalnych bądź technicznych kluczach unikalności (np. operacje typu *upsert* lub atomowa podmiana partii danych w ramach transakcji).
  * Aktualizację znaczników postępu (*checkpointów*) wiążemy bezpośrednio z pomyślnym zakończeniem zapisu danych.
* **Efekt architektoniczny:**
  Procesy stają się naturalnie odporne na awarie infrastruktury, przerwy sieciowe i ponowienia (*retries*). Ponowne uruchomienie zadania po błędzie nie generuje duplikatów ani nie pozostawia systemu w stanie częściowo zapisanym.

---

## III. Składanie prymitywów w procesy (*Compositional Reasoning*)

Trzecia kategoria określa sposób budowania złożonych procesów biznesowych z elementów spełniających wymagania kategorii I oraz II.

### 7. Poprawność przez kompozycję (*Compositional Reasoning*)

* **Istota zasady:**
  Złożone operacje i procesy budujemy wyłącznie poprzez składanie mniejszych, zaufanych prymitywów na podstawie ich kontraktów, bez konieczności ponownego analizowania i testowania ich wewnętrznej implementacji.
* **Realizacja w praktyce:**
  * **Zasada jednokrotnej weryfikacji prymitywu (*Local Reasoning*):** Każdy prymityw weryfikujemy i testujemy raz, w pełnej izolacji. Dopóki jego wewnętrzna implementacja, kontrakt oraz założenia nie ulegają zmianie, traktujemy go jako komponent zaufany i nie powtarzamy testów jego wewnętrznej logiki w każdym procesie, który go używa.
  * **Weryfikacja na poziomie złożenia:** Tworząc nowy proces biznesowy z gotowych prymitywów, weryfikujemy wyłącznie poprawność samego połączenia — czyli czy dane wyjściowe (*postconditions*) jednej operacji spełniają warunki wejściowe (*preconditions*) kolejnej oraz czy sekwencja kroków realizuje cel biznesowy.
* **Efekt architektoniczny:**
  Złożoność systemu rośnie liniowo, a nie wykładniczo. Dodawanie nowych procesów jest szybkie i bezpieczne, ponieważ opiera się na kompozycji sprawdzonych, idempotentnych operacji, a ciężar dowodu poprawności zostaje przeniesiony z poziomu niskopoziomowego kodu na poziom architektury przepływu.

---

## Podsumowanie — Zasada nadrzędna

1. **Konstruuj prymitywy tak, aby nie mogły działać błędnie** (*Correctness by Construction*: jedna odpowiedzialność, wykluczanie niepoprawnych stanów, czyste funkcje, oparcie na gwarancjach platformy i bazy danych).
2. **Zamykaj prymitywy za jednoznacznymi, powtarzalnymi umowami** (*Design by Contract & Idempotency*: jawne warunki wejścia/wyjścia, *fail-fast*, wąski interfejs, pełna idempotencja zapisu).
3. **Składaj procesy wyłącznie po kontraktach** (*Compositional Reasoning*: weryfikuj prymityw raz w izolacji, a na poziomie procesu weryfikuj wyłącznie zgodność połączonych kontraktów).
