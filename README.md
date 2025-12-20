# prompt-tools

Mały zestaw narzędzi CLI.

## Instalacja (dev)

Z użyciem virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Uruchom testy:

```bash
pytest
```

## Instalacja (systemowo, polecane)

Z użyciem pipx:

```bash
sudo apt update
sudo apt install -y pipx
pipx ensurepath
# otwórz nowy terminal albo:
# source ~/.bashrc

pipx install -e .
```

## Użycie

### `pt context`

Tworzy plik YAML z kontekstem dla podanego katalogu (lista plików + oryginalna zawartość).
Selekcja polega na tym, które pliki zostaną znalezione (respektowane są ignory).

```bash
pt context .
pt context /sciezka/do/projektu
```

Pliki są zapisywane do:

```
./data/contexts/
```

Nazwa pliku zaczyna się od nazwy katalogu, który kontekstujesz:

```
<dir>_YYYYMMDD_HHMM.yaml
```

Przykład:

```
onathoerfolder_20251110_1240.yaml
```

### `pt tree`

Tworzy plik YAML z drzewem plików (tylko te, które byłyby brane do kontekstu), bez wbudowywania treści.
W środku jest tylko:

- `tree: |-` (ASCII tree; przy plikach dopisana jest liczba linii albo `(?)` jeśli nie da się policzyć)

```bash
pt tree .
pt tree /sciezka/do/projektu
```

Pliki są zapisywane do:

```
./data/trees/
```

### `pt apply`

Zapisuje pliki do wskazanego katalogu na podstawie pliku YAML (`files: ...`).
Taki YAML może pochodzić z `pt context`, ale często jest generowany przez LLM jako „plan zmian”.

```bash
pt apply . data/contexts/myproj_20251110_1240.yaml
```

Domyślnie `YAML_FILE` to `files.yaml`, więc możesz też:

```bash
pt apply .
```

Przydatne flagi:

- `--dry-run` – pokaż co byłoby zapisane bez zapisu.
- `--no-clobber` – nie nadpisuj istniejących plików.
- `--write-placeholders` – zapisuj placeholdery (`[binary file omitted]`, itd.); domyślnie są pomijane.

## Format pliku YAML (`files`)

Plik to pojedynczy dokument YAML:

```yaml
files:
  - path: "relative/path/to/file.ext"
    content: |-
      <file contents>
  - path: "another/file.txt"
    content: |-
      ...
```

Uwagi:

- `files` to lista wpisów.
- `path` jest **ścieżką względną względem katalogu przekazanego do `pt context`** (albo względem katalogu docelowego w `pt apply`).
- `content` jest YAML block scalar (`|-`), więc zawartość pliku jest zachowana „as-is”.
- Pliki binarne nie są wbudowywane w YAML — zamiast tego pojawia się:

  ```
  [binary file omitted]
  ```

## Ignore rules

- Jeśli katalog jest repozytorium git, `pt context` używa `git ls-files` i respektuje `.gitignore`.
- W przeciwnym wypadku spada do `rg --files` (ripgrep), które też respektuje `.gitignore`.
- Jeśli w kontekstowanym katalogu istnieje `.ppignore`, jego wzorce są stosowane jako dodatkowe wykluczenia.
