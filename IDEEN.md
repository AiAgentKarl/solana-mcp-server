# Ideen-Pipeline — Agent Economy

Wird täglich automatisch aktualisiert. Neue Ideen werden hier gesammelt und bewertet.

## Bewertungskriterien
- **Netzwerkeffekt:** Wird es mit mehr Nutzern besser?
- **Eigenständig baubar:** Kann Claude das ohne Chris-Input bauen?
- **First-Mover:** Gibt es schon Konkurrenz?
- **Zukunftsrelevanz:** Wird das in 1-3 Jahren wichtig?

## Offene Ideen

_Zuletzt aktualisiert: 2026-03-20 (Research-Session)_

### 1. energy-grid-mcp-server — Strom & CO2-Intensitaet
- **APIs:** Electricity Maps (100k Free Calls/Monat), Carbon Intensity API (UK, kostenlos), ENTSO-E (EU-Netzdaten)
- **Tools:** Echtzeit-CO2-Intensitaet pro Land/Region, beste Zeiten fuer energieintensive Tasks, Strommix-Analyse
- **Netzwerkeffekt:** Jeder Agent, der Energie verbraucht (z.B. GPU-Scheduling), braucht das; wächst mit Klimafokus
- **Konkurrenz:** energyatit-mcp-server existiert (enterprise-fokussiert, kompliziert), kein einfacher Free-Tier-Server
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover MITTEL | Baubarkeit HOCH

### 2. political-finance-mcp-server — Wahlkampffinanzierung & Lobbying ✅ GEBAUT 2026-03-20
- **APIs:** OpenSecrets API (kostenlos fuer Forschung), FEC API (US-Wahlkampfdaten, komplett kostenlos), ProPublica Congress API
- **Tools:** Spenden nach Kandidat/Partei, Lobbyausgaben nach Industrie, Abstimmungsverhalten vs. Sponsoren
- **Netzwerkeffekt:** Journalisten, Policy-Agents, Buerger-KI — wächst mit Vertrauen in KI als Watchdog
- **Konkurrenz:** Kein MCP-Server gefunden — echter First-Mover
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover SEHR HOCH | Baubarkeit HOCH

### 3. labor-market-mcp-server — Jobmarkt & Arbeitsmarktdaten
- **APIs:** US Bureau of Labor Statistics (kostenlos), Eurostat Labour API (kostenlos), OECD Employment API
- **Tools:** Arbeitslosenquote nach Region, Lohntrends, Berufe mit Wachstum/Rueckgang, AI-Impact auf Jobs
- **Netzwerkeffekt:** HR-Agents, Karriere-Agents, Policy-Agents — alle brauchen Arbeitsmarktdaten
- **Konkurrenz:** Keiner auf PyPI gefunden mit freien APIs; kommerzielle Anbieter (TalentNeuron) sind teuer
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover HOCH | Baubarkeit HOCH

### 4. geospatial-mcp-server — OpenStreetMap & GIS-Operationen
- **APIs:** OpenStreetMap (Overpass API, kostenlos), Nominatim Geocoding (kostenlos), Natural Earth Data
- **Tools:** POI-Suche, Routing-Analyse, Geofencing, Flaechen-Berechnungen, Reverse Geocoding
- **Netzwerkeffekt:** Jeder Agent mit Standortbezug; wächst mit autonomen Agenten die physisch navigieren
- **Konkurrenz:** gis-mcp existiert (GitHub, sehr technisch), OSM MCP existiert (basic); kein polierter PyPI-Server
- **Bewertung:** Netzwerkeffekt SEHR HOCH | First-Mover MITTEL | Baubarkeit MITTEL

### 5. patent-intelligence-mcp-server — Patente & IP-Daten
- **APIs:** USPTO API (kostenlos), EPO OPS API (kostenlos), Google Patents (scraping-freundlich)
- **Tools:** Patentsuche nach Technologie/Unternehmen, Prior Art Check, Technologie-Trend-Analyse, Ablauf-Tracking
- **Netzwerkeffekt:** Startup-Agents, R&D-Agents, Legal-Agents — IP-Recherche ist universell
- **Konkurrenz:** patent_mcp_server (GitHub, rudimentaer, kein PyPI); Google Patents MCP (proprietaer)
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover HOCH | Baubarkeit HOCH

### 6. agent-context-optimizer-mcp — Tool-Bloat & Context-Overload-Loesung
- **Hintergrund:** Groesstes technisches Problem 2026 — MCP-Server fressen 40-50% des Context-Windows
- **Tools:** Automatisches Tool-Pruning fuer eine Aufgabe, Context-Budget-Tracking, Tool-Relevanz-Scoring
- **Netzwerkeffekt:** INFRASTRUKTUR — jeder der mehrere MCP-Server nutzt profitiert; Netzwerkeffekt durch Nutzungsdaten
- **Konkurrenz:** Kein Server gefunden der das loest — echter White-Space
- **Bewertung:** Netzwerkeffekt SEHR HOCH | First-Mover SEHR HOCH | Baubarkeit MITTEL

### 7. crossref-academic-mcp-server — Wissenschaftliche Zitationen & DOI-Daten
- **APIs:** Crossref API (kostenlos, 180 Mio. Records), OpenAlex API (kostenlos), Semantic Scholar API
- **Tools:** Paper-Suche, Zitations-Netzwerk, Impact-Faktor, Trending Topics, Autoren-Profile
- **Netzwerkeffekt:** Forschungs-Agents, Literaturrecherche, Fact-Checking — akademischer Content explodiert
- **Konkurrenz:** paper-search-mcp existiert (arXiv-fokussiert); Crossref spezifisch noch nicht poliert auf PyPI
- **Hinweis:** Crossref hat 2026 Public Data File mit 180M Records veroeffentlicht — perfektes Timing
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover MITTEL | Baubarkeit SEHR HOCH

### 8. supply-chain-mcp-server — Lieferketten & Handelsrouten ✅ GEBAUT 2026-03-20
- **APIs:** UN Comtrade API (kostenlos), World Bank Trade API, Open Supply Hub (Fabrikdaten)
- **Tools:** Import/Export-Daten nach Land/Produkt, Lieferketten-Risiko, Hafen-Status, Handelspartner-Analyse
- **Netzwerkeffekt:** Procurement-Agents, Risiko-Agents, Business Intelligence — Supply Chain ist post-COVID Dauerthema
- **Konkurrenz:** Kein oeffentlicher MCP-Server gefunden — echter First-Mover
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover SEHR HOCH | Baubarkeit HOCH

### 9. agent-server-card-mcp — MCP Server Cards & .well-known Discovery
- **Hintergrund:** Neues MCP-Protokoll-Feature 2026: Server-Metadaten via .well-known URL
- **Tools:** Server Card Generator, Capability-Discovery, Schema-Validator, Registry-Submission
- **Netzwerkeffekt:** INFRASTRUKTUR — wenn alle Server Cards nutzen, ist dieser Server der Hub dafuer
- **Konkurrenz:** Noch nicht implementiert (gemaess Roadmap in Arbeit) — Timing perfekt
- **Bewertung:** Netzwerkeffekt SEHR HOCH | First-Mover SEHR HOCH | Baubarkeit MITTEL

### 10. climate-risk-mcp-server — Klimarisiko & ESG-Daten
- **APIs:** Climate TRACE (kostenlos), NOAA Climate Data (kostenlos), Global Forest Watch API
- **Tools:** CO2-Emissionen nach Sektor/Land, Klimarisiko-Scores fuer Standorte, Extremwetter-Ereignisse, ESG-Benchmarks
- **Netzwerkeffekt:** Investment-Agents, Compliance-Agents, Real-Estate-Agents — ESG-Regulierung wird staerker
- **Konkurrenz:** Climatiq MCP existiert (nur Emissionsberechnung); breiter Klimarisiko-Server fehlt
- **Bewertung:** Netzwerkeffekt HOCH | First-Mover HOCH | Baubarkeit HOCH

---

### Prioritaetsranking (nach Netzwerkeffekt x First-Mover)
1. **agent-context-optimizer-mcp** — Loest DAS groesste MCP-Problem 2026
2. **political-finance-mcp-server** — Echter First-Mover, riesige Nachfrage
3. **agent-server-card-mcp** — Protokoll-Infrastruktur, perfektes Timing
4. **supply-chain-mcp-server** — First-Mover, B2B-relevant
5. **energy-grid-mcp-server** — Starke APIs, Klimafokus waechst

## Umgesetzte Ideen

| Datum | Idee | Server | Status |
|-------|------|--------|--------|
| 2026-03-20 | Solana Blockchain-Daten | solana-mcp-server | ✅ Live |
| 2026-03-20 | Germany Open Data | germany-mcp-server | ✅ Live |
| 2026-03-20 | Agriculture Data | agriculture-mcp-server | ✅ Live |
| 2026-03-20 | EU Company Data | eu-company-mcp-server | ✅ Live |
| 2026-03-20 | Space/NASA Data | space-mcp-server | ✅ Live |
| 2026-03-20 | Aviation Data | aviation-mcp-server | ✅ Live |
| 2026-03-20 | Weather/Climate | openmeteo-mcp-server | ✅ Live |
| 2026-03-20 | Cybersecurity/CVE | cybersecurity-mcp-server | ✅ Live |
| 2026-03-20 | Health/Medical | medical-data-mcp-server | ✅ Live |
| 2026-03-20 | MCP Hub (App Store) | mcp-appstore-server | ✅ Live |
| 2026-03-20 | API-to-MCP Converter | api-to-mcp-converter | ✅ Live |
| 2026-03-20 | Agent Memory | agent-memory-mcp-server | ✅ Live |
| 2026-03-20 | Agent Directory | agent-directory-mcp-server | ✅ Live |
| 2026-03-20 | Agent Reputation | agent-reputation-mcp-server | ✅ Live |
| 2026-03-20 | Agent Feedback | agent-feedback-mcp-server | ✅ Live |
| 2026-03-20 | Prompt Library | prompt-library-mcp-server | ✅ Live |
| 2026-03-20 | Agent Coordination | agent-coordination-mcp-server | ✅ Live |
| 2026-03-20 | Agent Workflow | agent-workflow-mcp-server | ✅ Live |
| 2026-03-20 | Agent Analytics | agent-analytics-mcp-server | ✅ Live |
| 2026-03-20 | x402 Payments | x402-mcp-server | ✅ Live |
| 2026-03-20 | Agent Interface Standard | agent-interface-standard | ✅ Live |
| 2026-03-20 | Agent Validator | agent-validator-mcp-server | ✅ Live |
| 2026-03-20 | Business Bridge | business-bridge-mcp-server | ✅ Live |
| 2026-03-20 | Agent Commerce | agent-commerce-mcp-server | ✅ Live |
| 2026-03-20 | Agent Identity | agent-identity-mcp-server | ✅ Live |
| 2026-03-20 | Hive Mind | hive-mind-mcp-server | ✅ Live |
| 2026-03-20 | Political Finance | political-finance-mcp-server | ✅ Live |
| 2026-03-20 | Supply Chain Trade | supply-chain-mcp-server | ✅ Live |

## Verworfene Ideen

| Idee | Grund |
|------|-------|
| Crypto Arbitrage Bot | Polymarket in DE illegal, Bot-Konkurrenz zu stark |
| Smithery-Eintrag | Braucht VPS/URL, Phase 2 |
