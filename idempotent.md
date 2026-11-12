Correctness by Construction (CbC)

Cel

Tworzyć oprogramowanie, którego poprawność można łatwo uzasadnić na podstawie jego konstrukcji, ograniczając liczbę potencjalnych błędów, złożoność analizy oraz konieczność powtarzania testów już sprawdzonych mechanizmów.

Podejście opiera się na trzech kategoriach.

I. Zasady ogólne

Powszechnie uznane praktyki inżynierskie, przydatne w zasadzie każdym projekcie. Nie stanowią specyfiki naszej strategii, ale świadomie nadajemy im wysoki priorytet.

Zasada| Na co kładziemy nacisk
Don't Reinvent the Wheel| Preferujemy istniejące, sprawdzone rozwiązania — szczególnie mechanizmy języka, biblioteki standardowej i bazy danych.
KISS (Keep It Simple, Stupid)| Unikamy niepotrzebnej złożoności konstrukcji, implementacji i przepływu sterowania.
Information Hiding| Oddzielamy interfejs komponentu od szczegółów jego implementacji. Ograniczamy zależności między elementami systemu.

Zasady te wspierają spójność kodu, jego czytelność, łatwość analizy i dalszego rozwoju.

II. Zasady specyficzne dla naszej strategii CbC

Istniejące, uznane koncepcje, których stosowanie przyjmujemy jako świadomą decyzję projektową.

Zasada| Rola w naszej strategii
Design by Contract (DbC)| Określamy warunki wstępne, końcowe i niezmienniki operacji. Poprawność rozpatrujemy względem jawnego kontraktu.
Make Illegal States Unrepresentable| Wykorzystujemy typy, konstrukcje danych i ograniczenia bazy, aby niepoprawne stany były niemożliwe lub trudniejsze do osiągnięcia.
Assume–Guarantee Reasoning| Budujemy poprawne operacje z komponentów o znanych gwarancjach, upewniając się, że spełniamy ich założenia.
Functional Core, Imperative Shell| Preferujemy oddzielenie czystej logiki od operacji posiadających efekty uboczne.
Fail Fast| Naruszenia założeń i nieoczekiwane błędy powinny być jawne, zamiast prowadzić do dalszego wykonywania kodu w niepoprawnym stanie.

Dodatkowo stosujemy odpowiednio do charakteru operacji:

- Exception Safety — zachowanie określonych gwarancji stanu w przypadku błędów.
- Atomicity (ACID) — niepodzielność powiązanych zmian, gdy jest wymagana.
- Idempotency — bezpieczeństwo ponownego wykonania operacji, gdy dopuszczamy ponowienia.

Nie są to wymagania dla każdej funkcji, lecz właściwości obowiązkowe tam, gdzie wynikają z kontraktu operacji.

III. Model konstrukcyjny — prymitywy

1. Definicja robocza

Prymityw to podstawowy element konstrukcyjny o znanym kontrakcie, którego poprawność w zakresie tego kontraktu uznajemy za dostatecznie uzasadnioną, aby wykorzystywać go bez ponownej weryfikacji jego wewnętrznej implementacji przy każdym użyciu.

Prymitywem może być zarówno gotowy mechanizm języka, biblioteki lub bazy danych, jak i prosty komponent naszego kodu, którego poprawność została osobno uzasadniona.

2. Wymagane właściwości

A. Znany kontrakt

Prymityw ma jasno określone wejścia, wyniki, warunki użycia, możliwe błędy i istotne niezmienniki.

B. Uzasadniona poprawność

Istnieje podstawa, aby ufać jego implementacji, np. dojrzały i udokumentowany mechanizm standardowej biblioteki, gwarancja silnika bazy danych albo prosta implementacja, której poprawność można bezpośrednio przeanalizować.

C. Łatwość lokalnego rozumowania

Zachowanie prymitywu jest możliwe do zrozumienia bez analizowania niepowiązanych fragmentów aplikacji. Prymityw nie powinien ukrywać niejawnych zależności ani niepotrzebnej logiki.

D. Kontrolowane efekty uboczne

Preferujemy operacje bez efektów ubocznych, kiedy jest to możliwe.

Efekty uboczne nie dyskwalifikują jednak prymitywu. Operacje bazy danych, systemu plików czy sieci mogą być prymitywami, jeśli ich skutki, warunki i zachowanie w przypadku błędów są określone.

E. Możliwość bezpiecznej kompozycji

Prymityw udostępnia wystarczające gwarancje, aby można było uzasadniać poprawność większych operacji, które z niego korzystają.

3. Zasada budowania

Preferujemy konstruowanie nowego kodu z już uzasadnionych elementów.

Nowy komponent może zostać uznany za prymityw, jeżeli jego poprawność da się ustalić na podstawie gwarancji użytych elementów oraz prostej, przejrzystej kompozycji.

Nie zakładamy jednak, że każda kompozycja poprawnych elementów automatycznie jest poprawna. Musimy uwzględnić warunki ich połączenia.

4. Zasada testowania

Nie powtarzamy testowania wewnętrznego działania mechanizmów, których gwarancje zostały już wiarygodnie ustalone.

Skupiamy testy i weryfikację na:

- nowej logice, której poprawność nie jest jeszcze dostatecznie uzasadniona;
- granicach między komponentami;
- poprawności ich połączenia;
- zachowaniu wobec błędów, efektów ubocznych i warunków środowiskowych.

Celem jest ograniczenie liczby potrzebnych testów dzięki konstrukcji, a nie rezygnacja z testów bez uzasadnienia.

Relacja między kategoriami

Zasady ogólne ograniczają niepotrzebną złożoność i sprzyjają wykorzystaniu sprawdzonych mechanizmów.

Zasady CbC pozwalają określać kontrakty, unikać niepoprawnych stanów i uzasadniać poprawność kompozycji.

Model konstrukcyjny wykorzystuje oba poprzednie poziomy, aby budować oprogramowanie z elementów o znanych, wiarygodnych gwarancjach.