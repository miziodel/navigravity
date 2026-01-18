# Developer Feedback: NaviGravity MCP v0.1.8

**Date**: 2026-01-18
**Context**: "Bridge Playlist" task execution.

## 1. Robustezza della Ricerca Tagged
`search_music_enriched` con query strutturate (es. artist:"The Beatles" title:"Help!") è molto fragile. Basta una differenza nel tipo di virgolette o la presenza di un punto esclamativo per restituire zero risultati, anche se l'album è presente.

**Suggerimento**: Implementare un fallback fuzzy o una normalizzazione più aggressiva delle stringhe di ricerca.

## 2. Output di assessment non parlante
`assess_playlist_quality` restituisce gli ID dei brani nei warnings.

**Suggerimento**: Includere title e artist nei messaggi di warning per evitare che l'agente debba fare lookup aggiuntivi per capire quale brano sta violando le regole di diversità.

## 3. Nuova Funzionalità: Discovery Bridge
Manca un tool che, dati due artisti o brani distanti, suggerisca dei "nodi di connessione" o artisti ponte presenti nella libreria. Attualmente l'agente deve iterare manualmente su similarità e generi.

**Suggerimento**: Un tool `find_bridge_artists(start_artist, end_artist)` aumenterebbe drasticamente la velocità di cura.

## 4. Smart Candidates Combinati
Il parametro `mode` accetta liste separate da virgola, ma il logica di scoring risultante è opaca.

**Suggerimento**: Restituire il breakdown dello score (es. base_score + recency_bonus + mood_multiplier) permetterebbe all'agente di spiegare meglio all'utente perché un brano è stato scelto.
