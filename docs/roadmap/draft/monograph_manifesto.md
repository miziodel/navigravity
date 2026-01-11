# Recipe: La Monografia Perfetta (Agentic Curator Protocol)

Questo documento formalizza la logica "umana" utilizzata per creare la monografia di Guccini, trasformandola in una specifica tecnica per il server MCP navigravity.

## 1. La Formula del Mix (The "Golden Ratio")
Non più selezioni casuali, ma pesi ponderati.

### Parametri
*   **Pietre Miliari (Milestones): 30%**
    *   *Definizione:* Top 10-20 tracks per ascolti (popularity index) o presenza in "Best Of" ufficiali.
    *   *Funzione:* Ancorare l'ascoltatore, fornire familiarità.
*   **Perle (Pearls): 50%**
    *   *Definizione:* Tracce album di alta qualità (rating > 4/5 o similarità armonica alta con le milestones), ma con popolarità media.
    *   *Funzione:* Costituire il "corpo" nobile della monografia.
*   **Sorprese (Spice): 20%**
    *   *Definizione:* Live versions (se di alta qualità audio), B-sides, collaborazioni, o tracce con energy/valence outlier (per rompere la monotonia).
    *   *Funzione:* Risvegliare l'attenzione, aggiungere unicità.

## 2. Coerenza Organica (Organic Sound Check)
Per evitare l'effetto "Jukebox rotto", la playlist deve suonare coesa.

### Regola "Anti-Cacofonia" (Filtro Sonic Consistency)
Se l'artista ha ere molto diverse (es. Guccini Folk vs Guccini Synth anni '80), definire un `target_era` o `dominant_instrument` (es. Acoustic Guitar/Piano).

*   **Opzionalità:** `allow_evolution` (True/False).
    *   Se `True`, ordinare cronologicamente o per "sonic gradient" (dal acustico all'elettrico).
    *   Se `False`, escludere gli outlier sonori troppo marcati (es. Remix dance).

## 3. Dinamica del Flusso (The "Wave" Flow)
Evitare blocchi monolitici di tristezza o euforia.

### Algoritmo "Wave"
1.  **Start Strong:** Iniziare sempre con una Pietra Miliare o una Perla "iconica" (Track 1-3).
2.  **Density Management:**
    *   Assegnare un punteggio di "Densità" a ogni brano (basato su durata, complessità testo, BPM invertito).
    *   *Regola:* Non accodare mai più di 3 brani ad "Alta Densità" (> 5 min, slow tempo).
    *   *Azione:* Inserire un "Breather" (Sorpresa o brano più leggero) ogni 3-4 brani pesanti.
3.  **The Bridge:** A metà playlist, inserire un cambio di passo (es. una sequenza live o un cambio di mood tematico).
4.  **The Outro:** Chiudere con brani ad alto contenuto emozionale/nostalgico ("Leave them wanting more").

## 4. Input Schema per MCP (JSON Draft)

```json
{
  "recipe_name": "monograph_golden_ratio",
  "target_artist": "Francesco Guccini",
  "constraints": {
    "total_tracks": 50,
    "mix_ratio": {
      "milestones": 0.3,
      "pearls": 0.5,
      "surprises": 0.2
    },
    "duration_min": "02:30:00"
  },
  "filters": {
    "organic_sound": {
      "mode": "tolerant", 
      "exclude_genres": ["dance remix", "electronic experiment"]
    },
    "language": "strict_artist_native"
  },
  "sorting": {
    "strategy": "wave",
    "wave_params": {
      "peak_interval": 4, 
      "start_with_hit": true,
      "end_with_deep_cut": true
    }
  }
}
```

## 5. Passaggi Operativi per l'Agente (Step-by-Step)
1.  **Harvest:** Recuperare TUTTE le tracce dell'artista (excl. duplicati bassa qualità).
2.  **Cluster:** Etichettare ogni traccia come Milestone (top 20%), Pearl (mid 60% high rating), Surprise (bottom 20% o flagged 'live').
3.  **Select:**
    *   Prendere le top 15 Milestones.
    *   Prendere 25 Pearls randomizzate (weighted by rating).
    *   Prendere 10 Sorprese (weighted by diversity).
4.  **Arrange:** Applicare l'algoritmo "Wave" per ordinare la lista combinata.
5.  **Audit:** Verificare se ci sono 2 canzoni identiche (studio vs live) troppo vicine. Se sì, spostarle.

## 6. 🔴 Limitazione Tecnica Rilevata (Black Box Test)
Durante il "deployment" della monografia su Navidrome, è emersa una criticità fondamentale:

**Perdita di Sequenza:** Il server Navidrome (o l'implementazione attuale del tool MCP) tende a riordinare le tracce (spesso alfabeticamente o per ID) ignorando l'ordine di invio.

*   **Impatto:** L'algoritmo "Wave" (Sezione 3) è attualmente teorico lato client, ma non garantito lato server senza un intervento manuale o un aggiornamento del protocollo MCP per supportare il `playlist_index` o l'ordinamento forzato.
*   **Soluzione Temporanea:** Accettare la playlist come un "Unordered Mix" o tentare un riordinamento manuale nell'interfaccia di Navidrome dopo la creazione.

---

# MCP Design: The "Monograph" Capability

Questo documento risponde allo scenario: *"Come rendiamo questa capacità nativa nel server MCP e come l'Agente la scopre?"*

## A. Come istruiamo il Server (The Instruction)
Non basta un prompt; dobbiamo implementare una Logica Deterministica nel server MCP navigravity. Creiamo un nuovo Tool: `create_monograph_playlist`.

### 1. The Logic (Backend)
Il server implementerà la classe `MonographCurator` che incapsula la "Ricetta" definita:

*   **Database Access:** Query diretta al DB musicale (SQLite/MySQL di Navidrome).
*   **Weighted Random Selection:** Algoritmo che pesca brani rispettando i bucket:
    *   `bucket_milestones` (Top 20% play_count)
    *   `bucket_pearls` (Rating >= 4)
    *   `bucket_surprises` (Rating < 3 OR Genre='Live' OR Year < 1970)
*   **Wave Sorter:** Algoritmo di ordinamento che calcola la density di ogni brano e li alterna.

### 2. The Tool Definition (Interface)
Esponiamo questa logica come tool MCP.

```python
@mcp.tool()
def create_monograph_playlist(
    artist_name: str, 
    playlist_name: str = None, 
    mix_preset: str = "golden_ratio",
    length: int = 50,
    cultural_anchors: List[str] = None
) -> str:
    """
    Creates a curated Monograph playlist for a specific artist using advanced mixing logic.
    
    Args:
        artist_name: The exact name of the artist (e.g., "Francesco Guccini").
        playlist_name: Optional name. Defaults to "Monograph: {ArtistName}".
        mix_preset: The recipe to use. Options: 
                    - 'golden_ratio' (30% Hits, 50% Pearls, 20% Rarities)
                    - 'deep_dive' (10% Hits, 70% Pearls, 20% Rarities)
                    - 'greatest_hits' (Standard logic)
        length: Number of tracks (default 50).
        cultural_anchors: Optional list of "must-have" song titles. 
                          These are injected by the Agent based on cultural knowledge
                          to bridge the "Semantic Gap".
        
    Returns:
        Summary of the created playlist and the Playlist ID.
    """
```

## B. Come l'Agente lo Scopre (The Discovery)
Immagina di aprire una nuova sessione. Non sai nulla di Guccini.

1.  **Connection Handshake**
    *   Allo start, il client MCP interroga il server: `GET /tools/list`.

2.  **The Agent's View**
    *   L'Agente riceve la lista dei tool disponibili. Tra i soliti `search_music` e `manage_playlist`, appare una novità illuminata:
    ```json
    {
      "name": "create_monograph_playlist",
      "description": "Creates a curated Monograph playlist... [Golden Ratio logic]...",
      "inputSchema": { ... }
    }
    ```

3.  **The Trigger**
    *   L'utente chiede: *"Fammi una playlist seria su Guccini, non la solita roba."*
    *   L'Agente, leggendo la descrizione del tool `create_monograph_playlist`, capisce (grazie al Semantic Matching del suo LLM) che "playlist seria" mappa perfettamente su `mix_preset="golden_ratio"` o `deep_dive`.
    *   Senza questo tool, l'Agente dovrebbe fare 50 chiamate a `search_music` e decidere lui i brani (lento, costoso, prono a errori). Con questo tool, l'Agente fa 1 chiamata: `create_monograph_playlist(artist_name="Francesco Guccini", mix_preset="golden_ratio")`.

## C. Architectural Decision Record (ADR): Fat Server vs Smart Client

### Domanda Critica
*"Il server MCP riesce a pescare brani rispettando i bucket o deve passare tutto all'Agente?"*

### Decisione: Fat Server (Logic-on-Server)
Abbiamo scelto di implementare la logica di filtering e sorting **dentro** il server MCP (Python), non nel Client (Agent/LLM).

**Motivazione:**
1.  **Efficienza del Context Window:**
    *   *Scenario Smart Client:* Per scegliere le "Top 20%" di Guccini (su 500 brani), l'agente dovrebbe scaricare i metadati di TUTTI i 500 brani, *leggerli* nel context window, e fare i calcoli. Costoso, lento e sprecone.
    *   *Scenario Fat Server:* L'agente invia 1 comando. Il server (in Python) scarica i 500 brani in memoria (nanosecondi), li filtra, li ordina e ritorna solo l'ID della playlist creata.
2.  **Limite Tecnico Attuale:**
    *   Il server attuale (`navidrome_mcp_server.py`) usa `libsonic` (API HTTP) e non SQL diretto. Tuttavia, possiede già pattern simili (vedi `get_smart_candidates`) dove scarica *batch* di dati (es. 500 items), li filtra in Python e ne restituisce pochi.
    *   Useremo questo pattern: il server farà multiple chiamate API veloci (es. `getTopSongs`, `getRandomSongs`, `search3`) per riempire i "Bucket" in memoria e poi assemblare la playlist.

### Implementation Strategy
Non potendo fare una query SQL unica combinata (es. `SELECT * ... WHERE rating > 4 OR playCount > 100`), il tool `create_monograph_playlist` orchestrerà la raccolta così:
1.  **Harvesting Parallelo (Simulato):**
    *   `getTopSongs(artist)` -> Riempe Bucket *Milestones*.
    *   `search3(artist)` (con iterazione) -> Recupera catalogo per Bucket *Pearls* (filtrando per rating in Python).
    *   `search3(artist, "Live")` -> Riempe Bucket *Surprises*.
2.  **Local Mixing:**
    *   Applica il *Golden Ratio* (30/50/20) selezionando dagli array in memoria.
    *   Applica il *Wave Sort* calcolando la densità sui dati in RAM.
3.  **Execution:**
    *   Chiama `createPlaylist` con la lista finale di ID.

## D. The Knowledge Gap Strategy (Hybrid Pattern)

**Problema:** Il server ha i dati statistici (PlayCount, Rating) ma ignora il "Significato Culturale" (es. "Auschwitz" di Guccini è un capolavoro anche se hai 0 ascolti). L'Agente ha la conoscenza culturale (LLM) ma non ha i dati locali.

**Soluzione: Cultural Bridges** (`cultural_anchors`)
L'Agente inietta la conoscenza semantica nel processo statistico del server.

### Workflow Aggiornato
1.  **User:** "Voglio una monografia su Guccini."
2.  **Agent (Knowledge Retrieval):**
    *   *LLM Thinking:* "Guccini richiede 'L'avvelenata', 'Dio è morto', 'Auschwitz', 'La locomotiva'."
3.  **Agent Action (Injection):**
    ```json
    {
      "artist_name": "Francesco Guccini",
      "mix_preset": "golden_ratio",
      "cultural_anchors": ["L'avvelenata", "Dio è morto", "Auschwitz", "La locomotiva"]
    }
    ```
4.  **Server Logic (Merger):**
    *   Cerca specificamente gli *Anchors*. Se li trova, li forza nel Bucket *Milestones* (o *Pearls*), garantendone la presenza.
    *   Riempie il resto degli slot coi criteri statistici normali.
    *   Risultato: Playlist Bilanciata (Statistica locale + Cultura globale).
