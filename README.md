### Einleitung

Dieses Projekt nutz das RESTful Application Programming Interface (REST API) der comdirect um den Kontostand anzuzeigen und automatisiert trades auszuführen.


Die Idee dieses Projektes ist aus dem Podcast Marktgeflüster von [finanzfluss](https://www.finanzfluss.de/) entstanden:

[![IMAGE ALT TEXT](http://img.youtube.com/vi/6Z86BnoHD50/0.jpg)](http://www.youtube.com/watch?v=6Z86BnoHD50&t=996 "#85 LIVE: Marktgeflüster bei den Heuschrecken | Marktgeflüster Podcast")

Die Aktion Winter-Trading mit Cashback ist hier im detail beschrieben [Winter-Trading](https://www.comdirect.de/wertpapierhandel/tradingspecials-winteraktion.html?sc_cid=6833&cid=comdirect_web:teaser:wintertrading:ms_23_24:aktionen_seite_gro%C3%9F:brokerage)

Zusammenfassung:

- Gültig bis zum 31.03.2024
- Mindestvolumen >= 1.000 €
- Nur bei der Börse Stuttgart ([EASY EUWAX](https://www.boerse-stuttgart.de/de-de/nachrichten/blog/easy-euwax))
- 1 € Cashback pro Trade für maximal 500 Trades


## 1. Nutzung des comdirect REST API

- Zunächst mus einmalig ein Zugang über diesen [LINK](https://www.comdirect.de/cms/kontakt-zugaenge-api.html) benatragt werden.

- Die erhaltenen Daten müssen dan in die config.ini Datei eingetragen werden (client_id und client_secret).

- Username und password sind die Logindaten der comdirect Seite.

- Die Wertpapierkennummer (WKN) und die Anzahl können über die Börse Stuttgart oder über die comdirect Seite gesucht werden.


Falls du noch kein Depot bei der comdirect hast:
[Kostenloses Depot bei der comdirect eröffnen](http://www.comdirect.de/pbl/a.do?rd=/cms/lp/kwk-depot.html&ci=201012740000000EM000000000000&wc=N3965)*

*Affiliate-Link


***Alle hier angegebenen Informationen stellen keine Anlageberatung oder Kaufempfehlung dar!***