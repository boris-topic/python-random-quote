# Aktivitet-checklista med tidtagning

Det här projektet är nu ett enkelt CLI-verktyg i Python för att planera dagen med aktiviteter,
markera vad som är klart och mäta tid per aktivitet.

## Funktioner

- Skapa aktiviteter i en checklista.
- Starta/stoppa tidtagning per aktivitet.
- Markera aktiviteter som klara/inte klara.
- Se total sammanfattning av tid och status.
- Data sparas i `activities.json` i samma mapp.

## Exempel

```bash
python get-quote.py add "Skriva rapport"
python get-quote.py add "Träna"
python get-quote.py start 1
python get-quote.py stop 1
python get-quote.py check 1
python get-quote.py list
python get-quote.py summary
```

## Kommandon

- `add "titel"` – skapar en aktivitet.
- `list` – visar checklistan.
- `start <id>` – startar tidtagning.
- `stop <id>` – stoppar tidtagning.
- `check <id>` – markerar aktivitet som klar.
- `uncheck <id>` – tar bort klar-markering.
- `remove <id>` – tar bort aktivitet.
- `summary` – visar total statistik.
