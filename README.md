# VD17-SRU

## Script für die SRU-Abfrage des VD17 (auch anwendbar für VD18). 

Es werden folgende Felder erfasst:
- IDN: Controlfield 001
- VD-Nummer: Datafield 024, Subfield a
- Verfasser: Datafield 100, Subfield a
- Titel: Datafield 245, Subfield a
- Erscheinungsort: Datafield 264, Subfield a (Gibt alle angegebenen Orte als Liste aus)
- Erscheinungsjahr: Datafield 264, Subfield c

Abfragen via PICA-Suche:
- nach Titel: pica.tit
- nach Person: pica.per
- nach Jahr: pica.jah
- nach Ort: pica.vlo

## Script für die Visualisierung der Ergebnisse.

Folgende Visualisierungen werden ausgegeben:
- Anzahl der Werke des Datasets pro Jahr
- Anzahl der Werke des Datasets in den Einrichtungen (geordnet nach Sigel)
- Anzahl der verwendeten Sprachen der Werke des Datasets
- Anzal der verwendeten Sprachen der Werke im Laufe der Zeit