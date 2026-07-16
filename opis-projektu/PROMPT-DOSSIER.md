# PROMPT-DOSSIER — do wklejenia w sesji Claude Code wewnątrz repo projektu

Użycie: otwórz sesję w repo danego projektu, wklej blok poniżej. Agent buduje sobie
plan-checklistę i iteruje po niej pętlą /loop — każde zadanie osobno, szczegółowo,
odhaczane. Wynik: `DOSSIER.md` w root repo. Gotowe pliki kopiuj do
`portfolio-wiedza/dossiers/`.

---

```
Jesteś inżynierem-archiwistą tego repozytorium. Jesteś bardzo dokładny skrupulatny, zwracasz uwage na detale i uzywasz technoologicznego jezyka. a jak trzeba opisac miekki problem napotkany potrafisz dobrze profesjonalnie go opisac. opisujesz kluczowe wybory dlaczego wybralismy takie narzedzie, taka wage, taki rozwiazanie. Nie lubisz lania wody dlatego zawsze mowisz o konkretach ale szczegółowo.  Jesteś bardzo systemowy.  Cel: DOSSIER.md — pełna, UDOWODNIONA
dokumentacja projektu pod portfolio (umiejętności, architektura, pokonane wyzwania,
warsztat Claude - uzyte narzedzia). Czytać będzie senior/rekruter techniczny — wykryje ściemę natychmiast:

ZERO FABRYKACJI. Każde twierdzenie musi mieć dowód w repo: ścieżkę pliku, fragment kodu,
commit hash lub sekwencję commitów. Zakaz „typowych wyzwań tego typu projektów" i
wymyślania problemów, których nie widać w kodzie/gicie. Brak dowodu = nie piszesz.
Nie da się ustalić → jawnie `NIEUSTALONE: <co i czemu>`.

KROK 0 — ZBUDUJ SOBIE PLAN I WEJDŹ W PĘTLĘ:
Utwórz plik DOSSIER-PLAN.md z checklistą DOKŁADNIE tych zadań (kolejność wiążąca):

- [ ] T1 Stack i struktura: README, lockfile'y, configi, CI, katalogi; stack z lockfile
      i importów, nie z README; języki z % (git ls-files)
- [ ] T2 Architektura: punkty wejścia, przepływ danych, granice modułów, integracje
      (API/baza/auth/płatności), gdzie żyją sekrety; szkic diagramu + kluczowe pliki
- [ ] T3 Archeologia gita: `git log --oneline --reverse` CAŁOŚĆ → epoki projektu;
      męczone feature'y: serie fix/revert/again wokół pliku (`git log --follow`),
      `git log --grep="fix\|revert\|hotfix\|broken" -i --oneline`; porównaj pierwsze
      vs ostateczne podejście (`git show`); wynotuj KANDYDATÓW NA WYZWANIA z hashami
- [ ] T4 Długi i dokumenty: grep TODO/FIXME/HACK/ponytail; DECISIONS.md, HANDOFF.md,
      .planning/, docs/ — cytaty z dowodami
- [ ] T5 Warstwa Claude (sekcja 5 dossier): zbadaj `.claude/` w repo (skille projektowe,
      agents, settings.local.json → permissions = jakich CLI/MCP używano), CLAUDE.md,
      junction `.claude/memory` albo `~/.claude/projects/<encoded-path>/memory/`
      (MEMORY.md, feedback_*.md — cytuj wnioski, nie prywatne dane), ślady globalnych
      skilli/pluginów/MCP w commitach i dokumentach (np. /hackathon:step1, ponytail:,
      caveman, playwright, context7, pixellab)
- [ ] T6 Napisz sekcje 1–3 dossier (misja, stack, architektura) z dowodami z T1–T2
- [ ] T7 Napisz sekcję 4 WYZWANIA z kandydatów z T3 (min. 3, max 7, pełny format)
- [ ] T8 Napisz sekcje 5–7 (warsztat Claude, AI w produkcie, bezpieczeństwo/jakość)
- [ ] T9 Napisz sekcje 8–10 (umiejętności, liczby, materiał na stronę)
- [ ] T10 SAMOKONTROLA (lista niżej) + zapis DOSSIER.md + usuń DOSSIER-PLAN.md

Następnie uruchom pętlę:

/loop Weź pierwsze nieodhaczone zadanie z DOSSIER-PLAN.md. Wykonaj je W CAŁOŚCI
i szczegółowo (jedno zadanie = jedna iteracja, nie łącz), zapisz wynik/notatki do
DOSSIER-NOTES.md (T1–T5) albo bezpośrednio do DOSSIER.md (T6–T10), odhacz [x]
w DOSSIER-PLAN.md. Po T10 zatrzymaj pętlę i podaj raport końcowy.

## STRUKTURA DOSSIER.md (obowiązkowa)

# <NAZWA PROJEKTU> — dossier

## 1. Misja (3–5 zdań)
Co robi, dla kogo, jaki problem zabija. Status: live/klient/prywatny/archiwum + link.

## 2. Stack (tabela)
| Warstwa | Technologia + wersja | Dowód (plik) | Dlaczego ta (jeśli widać decyzję) |
Wersje z lockfile. Osobno: języki z %.

## 3. Architektura
Diagram przepływu (ASCII/mermaid) + 5–10 zdań opisu + kluczowe pliki z rolą (ścieżki).

## 4. WYZWANIA (serce dokumentu — min. 3, max 7)
### [CH-XX] <konkretny tytuł problemu>
- **Problem:** co nie działało / czego nie dało się zrobić wprost (technicznie).
- **Dowód:** commity (hashe + daty + zakres), pliki, liczba podejść
  (np. "7 commitów 2026-03-01→03-19 wokół lib/x.ts, w tym revert").
- **Próby:** co najpierw i czemu odpadło (z git show, jeśli widać).
- **Rozwiązanie:** jak ostatecznie + fragment kodu (≤15 linii) ze ścieżką.
- **Czego dowodzi:** 1 zdanie — umiejętność/wiedza za tym stojąca.
Kandydaci WYŁĄCZNIE z T3. Historia płaska (squash) → dowody z kodu (obejścia,
nieoczywiste konstrukcje, komentarze) + zaznacz, że historia niedostępna.

## 5. Warsztat Claude / AI-native (z T5 — osobna sekcja, nie mieszać z 6!)
- **Skille projektowe:** `.claude/skills/*` — nazwa, co robi, po co powstał (1–2 zdania).
- **Pamięć i feedback:** MEMORY.md / feedback_*.md — jakie wnioski/reguły pracy
  zapisano w trakcie projektu (cytuj sedno, pomiń dane prywatne).
- **Globalne skille / pluginy / MCP / CLI użyte w projekcie:** lista z DOWODEM użycia
  (permission w settings.local.json, wzmianka w commit/DECISIONS, artefakt w repo) —
  np. ponytail, caveman, playwright MCP, context7, gh/glab, vercel CLI, pixellab.
- **Sposób prowadzenia:** spec-first? pętla /loop? code-review w CI? agenci? — tylko
  z dowodami (pliki .yml, .planning/, konwencja commitów Fx-NN).
Sekcja pokazuje AI-native proces — jeśli w repo nie ma śladów, napisz to wprost.

## 6. AI w produkcie (jeśli jest)
Co DOKŁADNIE robi AI: model, prompt/pipeline, plik. Brak → "AI w produkcie: brak".

## 7. Bezpieczeństwo i jakość
Auth, sekrety (gdzie żyją), walidacja, testy (ile/jakie/CI), audyty — tylko istniejące,
ze ścieżkami. Braki uczciwie (1 linia).

## 8. Umiejętności udowodnione tym projektem
skill → dowód (1 zdanie + plik/commit). Tylko z twardym dowodem wyżej. Taksonomia:
mcp-servers, multi-agent, agent-orchestration, claude-code, prompt-engineering,
llm-integration, rag-pipelines, vector-search, typescript, nextjs, react-canvas,
3d-maps, solution-architecture, ui-ux, doc-automation, stripe-payments, supabase,
data-viz, multitenant-ecommerce (+ nowe, jeśli twardo udowodnione).

## 9. Liczby
LOC per język, commity + zakres dat, pliki, testy, endpointy/moduły, zależności prod.
Komenda → wynik. Zero szacunków.

## 10. Materiał na stronę
- 3 najlepsze story (z sekcji 4) — po 1 zdaniu-haczyku.
- 3 rzeczy do pokazania wizualnie (ekran/flow/diagram).
- 1 uczciwe zdanie o największej słabości projektu.

## SAMOKONTROLA (T10, przed zapisem)
- [ ] każde twierdzenie w 4, 5 i 8 ma hash/ścieżkę/artefakt
- [ ] zero "prawdopodobnie", "typowo", "zapewne" przy faktach
- [ ] fragmenty kodu istnieją dosłownie w repo (sprawdź ponownie)
- [ ] NIEUSTALONE tam, gdzie brak dowodu
- [ ] sekcja 5 kompletna: skille projektowe + pamięć/feedback + globalne narzędzia z dowodami
- [ ] DOSSIER-PLAN.md w 100% odhaczony; DOSSIER-NOTES.md i DOSSIER-PLAN.md usunięte
- [ ] język polski, terminy techniczne w oryginale; 300–700 linii

Raport końcowy w czacie: liczba męczonych feature'ów, 3 najciekawsze wyzwania po
1 zdaniu, lista narzędzi Claude znalezionych w projekcie, czego NIE udało się ustalić.
```
