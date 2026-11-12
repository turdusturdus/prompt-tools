Correctness by Construction (CbC)

Cel

Tworzyć oprogramowanie, którego poprawność można łatwo uzasadnić na podstawie jego konstrukcji, ograniczając liczbę potencjalnych błędów, złożoność analizy oraz konieczność powtarzania testów już sprawdzonych mechanizmów.

Podejście opiera się na trzech kategoriach:

1. Zasady ogólne — powszechnie uznane praktyki inżynierskie, na które kładziemy szczególny nacisk.
2. Zasady CbC — istniejące, uznane praktyki, których stosowanie świadomie przyjmujemy jako element strategii zapewniania poprawności.
3. Model konstrukcyjny — nasza specyfikacja podstawowych elementów kodu, nazywanych roboczo prymitywami, oraz sposobu budowania z nich większych operacji.

Celem jest minimalizowanie liczby możliwych błędów przez konstrukcję oprogramowania, a nie zastępowanie uzasadnienia poprawności samymi testami.

---

I. Zasady ogólne

Powszechnie uznane praktyki inżynierskie, przydatne w zasadzie każdym projekcie. Nie stanowią specyfiki naszej strategii, ale świadomie nadajemy im wysoki priorytet.

1. Don't Reinvent the Wheel

Wykorzystuj istniejące, sprawdzone rozwiązania zamiast niepotrzebnie tworzyć własne odpowiedniki.

Preferujemy mechanizmy języka, biblioteki standardowej, dojrzałe biblioteki oraz natywne możliwości wykorzystywanych systemów.

Szczególnie istotne jest ponowne wykorzystywanie mechanizmów, które już zapewniają potrzebne gwarancje poprawności.

Przykład: Korzystamy z ograniczenia "UNIQUE" w PostgreSQL zamiast implementować własne sprawdzanie duplikatów przed zapisem.

2. KISS (Keep It Simple, Stupid)

Preferuj najprostsze rozwiązanie, które w pełni realizuje wymagany kontrakt.

Ograniczamy niepotrzebne abstrakcje, stany przejściowe, rozgałęzienia, ukryte zależności i złożoność przepływu sterowania.

Nie utożsamiamy jednak prostoty z minimalną liczbą linii kodu. Prostsza konstrukcja to taka, której zachowanie i poprawność łatwiej zrozumieć oraz uzasadnić.

3. Information Hiding

Oddzielaj publiczny interfejs komponentu od szczegółów jego implementacji.

Kod korzystający z komponentu powinien zależeć od jego udokumentowanego zachowania, a nie od sposobu realizacji tego zachowania.

Pozwala to wymieniać lub modyfikować implementacje bez naruszania poprawności pozostałych elementów systemu, o ile kontrakt zostaje zachowany.

---

II. Zasady specyficzne dla naszej strategii CbC

Istniejące, uznane koncepcje, których stosowanie przyjmujemy jako świadomą decyzję projektową.

1. Design by Contract (DbC)

Każda istotna operacja powinna mieć jasno określony kontrakt obejmujący:

- Preconditions — warunki, które muszą być spełnione przed wykonaniem operacji.
- Postconditions — gwarancje po jej poprawnym wykonaniu.
- Invariants — właściwości, które muszą zostać zachowane.

Kontrakt powinien także określać istotne skutki uboczne, możliwe błędy oraz warunki środowiskowe, od których zależą gwarancje.

Nie zakładamy, że używany komponent zapewnia więcej, niż wynika z jego specyfikacji.

2. Make Illegal States Unrepresentable

Projektuj reprezentacje danych tak, aby niepoprawne stany były niemożliwe do utworzenia lub istotnie trudniejsze do osiągnięcia.

Wykorzystujemy w tym celu typy, ograniczenia konstruktorów, niemutowalne struktury oraz mechanizmy integralności danych zapewniane przez bazę.

Technika: Parse, Don't Validate

Na granicy systemu przekształcamy surowe, niezaufane dane w odpowiednio skonstruowaną reprezentację domenową.

Zamiast wielokrotnie sprawdzać te same właściwości surowych danych:

1. Analizujemy i sprawdzamy dane podczas ich przyjmowania.
2. Tworzymy obiekt reprezentujący poprawne dane.
3. Dalsze operacje wykorzystują gwarancje wynikające z tej reprezentacji.

Przykładowo wejściowy słownik z konfiguracją migracji przekształcamy w strukturę, której konstruktor wymaga poprawnych wartości. Logika migracji nie musi następnie ponawiać tych samych sprawdzeń.

W Pythonie nie każdą niepoprawną sytuację da się całkowicie wykluczyć za pomocą systemu typów. Gwarancje reprezentacji muszą więc wynikać również z rzeczywistych ograniczeń konstrukcji i modyfikacji obiektów.

3. Assume–Guarantee Reasoning

Uzasadniaj poprawność większych operacji na podstawie założeń i gwarancji ich komponentów.

Przy każdej kompozycji upewniamy się, że:

- założenia używanego komponentu są spełnione;
- jego udokumentowane gwarancje są wystarczające;
- sposób połączenia komponentów zachowuje wymagane niezmienniki;
- efekty uboczne i możliwe błędy nie naruszają poprawności całej operacji.

Poprawność części nie oznacza automatycznie poprawności ich połączenia.

4. Functional Core, Imperative Shell

Oddzielaj czystą logikę obliczeniową od operacji powodujących efekty uboczne.

Functional Core obejmuje przede wszystkim deterministyczne przekształcenia danych i decyzje, które można analizować niezależnie od środowiska.

Imperative Shell odpowiada za interakcje z bazą danych, systemem plików, siecią i innymi zasobami zewnętrznymi.

Preferujemy czyste funkcje tam, gdzie pozwala na to charakter problemu. Nie wymagamy jednak czystości od wszystkich komponentów — operacje I/O są niezbędne, ale powinny mieć jawne, kontrolowane skutki.

5. Fail Fast

Naruszenia założeń i nieoczekiwane błędy powinny być wykrywane i sygnalizowane możliwie blisko miejsca ich wystąpienia.

Nie ukrywamy naruszeń kontraktów ani nie kontynuujemy działania na stanie, którego poprawności nie możemy uzasadnić.

Nie oznacza to automatycznego przerywania całego procesu przy każdym błędzie. Przewidywane błędy zewnętrzne mogą być obsługiwane, jeśli odpowiednie zachowanie zostało określone w kontrakcie.

Dodatkowe wymagania zależne od sytuacji

Exception Safety

Określaj, jakie gwarancje dotyczące stanu i zasobów pozostają zachowane, jeżeli operacja zakończy się wyjątkiem.

Atomicity (ACID)

Jeżeli kilka zmian musi zostać wykonanych niepodzielnie, wykorzystuj odpowiednie mechanizmy transakcyjne zamiast implementować ręczne wycofywanie częściowych zmian.

Idempotency

Jeżeli operacja może być ponawiana, projektuj ją tak, aby powtórzenie nie powodowało niezamierzonych dodatkowych skutków.

Idempotency, Atomicity i checkpointy

W procesach przetwarzania danych, migracjach i zadaniach Airflow należy rozpatrywać te właściwości łącznie.

- Idempotency zapewnia bezpieczeństwo ponowienia operacji w określonym zakresie.
- Atomicity chroni przed częściowym wykonaniem zbioru zmian objętych jedną transakcją.
- Checkpoint zapisuje postęp, od którego proces może wznowić wykonywanie.

Checkpoint nie powinien wskazywać zakończenia pracy, której wynik nie został trwale zapisany.

Jeśli zapis danych i aktualizacja checkpointu odbywają się w tej samej bazie i mogą zostać objęte jedną transakcją, preferujemy atomowe zatwierdzenie obu zmian.

Jeśli nie jest to możliwe, projektujemy sposób odzyskiwania poprawnego stanu po awarii, np. przez bezpieczne ponowienie operacji lub uzgodnienie zapisanego postępu z rzeczywistym stanem danych.

Ważne: Idempotencja nie zastępuje atomowości. Transakcja nie zapewnia też automatycznie idempotencji całego procesu. Każda z tych właściwości wymaga osobnego uzasadnienia.

---

III. Model konstrukcyjny — prymitywy

1. Definicja robocza

Prymityw to podstawowy element konstrukcyjny o znanym kontrakcie, którego poprawność w zakresie tego kontraktu uznajemy za dostatecznie uzasadnioną, aby wykorzystywać go bez ponownej weryfikacji jego wewnętrznej implementacji przy każdym użyciu.

Prymitywem może być:

- operacja lub mechanizm dostarczany przez język programowania;
- mechanizm biblioteki standardowej lub innej sprawdzonej biblioteki;
- mechanizm bazy danych o udokumentowanych gwarancjach;
- własny, odpowiednio prosty i zweryfikowany komponent.

Prymityw nie musi być niewielki pod względem liczby linii kodu. Musi natomiast udostępniać odpowiednio precyzyjny kontrakt, na którego gwarancjach można bezpiecznie opierać dalszą konstrukcję.

Jego poprawność nie wynika automatycznie z prostoty ani popularności użytej biblioteki.

2. Wymagane właściwości prymitywu

A. Znany kontrakt

Prymityw ma określone wejścia, wyniki, warunki użycia, możliwe błędy, istotne efekty uboczne i wymagane niezmienniki.

B. Uzasadniona poprawność

Istnieje wiarygodna podstawa zaufania do implementacji.

Może nią być udokumentowana gwarancja dojrzałej platformy, wcześniejsza weryfikacja komponentu albo bezpośrednio uzasadniona poprawność jego konstrukcji.

C. Local Reasoning

Poprawność prymitywu można uzasadnić lokalnie, na podstawie:

- jego własnej implementacji;
- jego kontraktu;
- kontraktów i gwarancji użytych komponentów;
- jawnych założeń dotyczących środowiska.

Nie powinna być do tego potrzebna analiza niepowiązanych fragmentów aplikacji.

D. Ograniczona złożoność

Prymityw powinien być możliwie prosty do zrozumienia i analizy.

Preferujemy wąską odpowiedzialność, ograniczoną liczbę stanów przejściowych, czytelny przepływ sterowania i brak niejawnych zależności.

Nie narzucamy arbitralnego limitu długości funkcji lub liczby rozgałęzień — istotna jest łatwość uzasadnienia poprawności.

E. Kontrolowane efekty uboczne

Preferujemy czyste funkcje, gdy charakter operacji na to pozwala.

Prymityw może jednak modyfikować stan bazy danych, pliki lub inne zasoby. W takim przypadku zakres skutków ubocznych oraz zachowanie w razie błędu muszą być określone w kontrakcie.

F. Możliwość bezpiecznej kompozycji

Gwarancje prymitywu muszą być wystarczająco jasne i stabilne, aby można było wykorzystywać je przy budowaniu większych operacji.

G. Określony zakres zaufania

Zaufanie do prymitywu obowiązuje w zakresie jego kontraktu oraz przyjętych założeń.

Zmiana implementacji, wersji zależności, konfiguracji lub istotnych warunków środowiskowych może wymagać ponownej weryfikacji.

3. Uznawanie komponentu za zaufany

Nie każdy komponent automatycznie staje się zaufanym prymitywem.

W przypadku gotowego mechanizmu ustalamy, czy jego udokumentowane gwarancje i przyjęte założenia odpowiadają naszym wymaganiom.

W przypadku własnego komponentu musimy uzasadnić jego poprawność. Możemy wykorzystać analizę kodu, kontrakty zastosowanych elementów, testy lub inne odpowiednie metody weryfikacji.

Local Reasoning jest tutaj kluczowym kryterium: uzasadnienie poprawności powinno być możliwe bez odtwarzania zachowania całego systemu.

Prymityw uznany za zaufany może następnie służyć jako element konstrukcyjny kolejnych komponentów.

4. Budowanie przez kompozycję

Nowe operacje preferencyjnie tworzymy przez składanie zaufanych elementów.

Podczas kompozycji sprawdzamy przede wszystkim:

1. Czy warunki wstępne każdego komponentu są spełnione.
2. Czy gwarancje jednego komponentu wystarczają do użycia kolejnego.
3. Czy zachowane są niezmienniki całego procesu.
4. Czy efekty uboczne, awarie i ponowienia nie naruszają wymaganego rezultatu.

Nowy komponent może sam stać się zaufanym prymitywem, jeśli jego kontrakt i poprawność zostaną odpowiednio uzasadnione.

Nie zakładamy, że kompozycja poprawnych komponentów zawsze jest poprawna. To właśnie sposób ich połączenia wymaga osobnej analizy.

5. Testowanie i ponowna weryfikacja

Nie powtarzamy bez potrzeby testów wewnętrznego działania mechanizmów, których gwarancje zostały już wiarygodnie ustalone.

W szczególności nie testujemy ponownie implementacji standardowych operacji Pythona czy mechanizmów integralności PostgreSQL tylko dlatego, że korzysta z nich kolejna funkcja.

Koncentrujemy weryfikację na:

- nowej, niezweryfikowanej logice;
- poprawności kompozycji;
- granicach pomiędzy komponentami;
- zgodności rzeczywistego środowiska z założeniami;
- zachowaniu podczas awarii i ponowień;
- zmianach, które mogły naruszyć wcześniejsze uzasadnienie poprawności.

Wcześniejsza weryfikacja prymitywu nie eliminuje potrzeby testowania integracji ani sprawdzania nowych warunków użycia.

Celem jest ograniczanie zbędnych testów dzięki lepszej konstrukcji i lokalnemu uzasadnianiu poprawności, a nie bezwarunkowe testowanie każdego komponentu tylko jeden raz.

---

Przykład zastosowania — migracja danych w PostgreSQL

Rozważmy proces, który pobiera dane, przekształca je i zapisuje do tabeli docelowej, a następnie aktualizuje checkpoint.

Zasady ogólne

Wykorzystujemy natywne ograniczenia integralności, transakcje i odpowiednie operacje PostgreSQL, zamiast samodzielnie odtwarzać ich działanie w Pythonie.

Zasady CbC

Dane wejściowe parsujemy do określonej reprezentacji. Logikę transformacji projektujemy jako czystą funkcję, jeśli to możliwe.

Kontrakty określają wymagania danych i gwarantowane rezultaty.

Zapis projektujemy z uwzględnieniem idempotencji, a zapis danych i checkpointu obejmujemy wspólną transakcją, gdy pozwala na to architektura.

Model prymitywów

Traktujemy udokumentowane operacje PostgreSQL oraz zweryfikowane funkcje transformacji jako elementy konstrukcyjne.

Przy budowaniu procesu analizujemy ich kompozycję, a nie implementujemy ani nie testujemy ponownie wewnętrznych algorytmów silnika bazy danych.

Sprawdzamy natomiast, czy połączenie tych elementów rzeczywiście realizuje kontrakt procesu, również po awarii lub ponownym uruchomieniu.

---

Podsumowanie

I. Zasady ogólne wspierają prostotę, spójność i wykorzystanie istniejących rozwiązań.

II. Zasady CbC określają sposób konstruowania poprawnych stanów, definiowania kontraktów, kontrolowania efektów ubocznych oraz rozumowania o gwarancjach komponentów.

III. Model konstrukcyjny definiuje, kiedy element może zostać uznany za zaufany prymityw oraz jak budować z takich elementów większe operacje.

Zasada nadrzędna: Buduj oprogramowanie z elementów o znanych i uzasadnionych gwarancjach. Ograniczaj możliwość wystąpienia błędów przez konstrukcję, a poprawność całości uzasadniaj na podstawie kontraktów komponentów i sposobu ich połączenia.