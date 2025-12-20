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

### `pt get`

Tworzy snapshot YAML dla podanego katalogu:

```bash
pt get .
pt get /sciezka/do/projektu
```

Snapshoty są zapisywane do:

```
./data/snapshots/
```

Nazwa pliku zaczyna się od nazwy katalogu, który snapshotujesz:

```
<dir>_YYYYMMDD_HHMM.yaml
```

Przykład:

```
onathoerfolder_20251110_1240.yaml
```

### `pt apply`

Odtwarza pliki z pliku YAML (snapshot w formacie `pt get`) do wskazanego katalogu:

```bash
pt apply . data/snapshots/myproj_20251110_1240.yaml
```

Domyślnie `YAML_FILE` to `files.yaml`, więc możesz też:

```bash
pt apply .
```

Przydatne flagi:

- `--dry-run` – pokaż co byłoby zapisane bez zapisu.
- `--no-clobber` – nie nadpisuj istniejących plików.
- `--write-placeholders` – zapisuj placeholdery (`[binary file omitted]`, itd.); domyślnie są pomijane.

## Format pliku snapshot (YAML)

Generowany plik to pojedynczy dokument YAML:

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
- `path` jest **ścieżką względną względem katalogu przekazanego do `pt get`**.
- `content` jest YAML block scalar (`|-`), więc zawartość pliku jest zachowana „as-is”.
- Pliki binarne nie są wbudowywane w YAML — zamiast tego pojawia się:

  ```
  [binary file omitted]
  ```

## Ignore rules

- Jeśli katalog jest repozytorium git, `pt get` używa `git ls-files` i respektuje `.gitignore`.
- W przeciwnym wypadku spada do `rg --files` (ripgrep), które też respektuje `.gitignore`.
- Jeśli w snapshotowanym katalogu istnieje `.ppignore`, jego wzorce są stosowane jako dodatkowe wykluczenia.
