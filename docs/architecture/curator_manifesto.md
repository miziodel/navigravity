# The Curator Manifesto
> "L'agente 'bibliotecario' è morto. Viva il Curatore."

This protocol defines the strict **Quality First** methodology for all playlist generation tasks. No more "trial and error". 

## 1. The Core Philosophy
**Stop Guessing. Start Curating.**
Every playlist must pass through three rigorous stages: **Harvest ➔ Filter ➔ Execute**.

## 2. The Information Hierarchy
Reliability over Randomness.
1.  **Harvest (The Broad Net)**: Gather 3x-5x the required tracks.
    *   *Target*: 150+ candidates for a 50-song playlist.
    *   *Tools*: `get_smart_candidates`, `search_music_enriched`.
2.  **Filter (The Quality Gate)**: Ruthlessly cull candidates.
    *   *Diversity Check*: Use `assess_playlist_quality` to ensure no artist dominates (max 2-3 tracks per artist unless specified).
    *   *Library Presence*: Use `batch_check_library_presence` to verify availability.
    *   *Analysis*: Check `diversity_score` and `repetition_metrics`.
3.  **Execute (The Precision Strike)**: Create the final product.
    *   *Action*: `manage_playlist` (create).
    *   *Verification*: Final `assess_playlist_quality` run on the created playlist.

## 3. The Rules of Engagement
*   **Harvest Ratio**: Always fetch **300%-500%** of the target length.
*   **Quality Gate**: NEVER create a playlist without passing the `assess_playlist_quality` check first.
*   **Batch Verification**: NEVER assume tracks exist; verify them.

## 4. Operational Workflow
1.  **Request Analysis**: Understand the vibe/genre/mood.
2.  **Harvesting**:
    *   Call `get_smart_candidates(limit=150, ...)`
3.  **Filtering**:
    *   Local processing to filter duplicates and heavy repetition.
    *   Consult `assess_playlist_quality` on the draft list.
4.  **Finalization**: 
    *   Push to server via `manage_playlist`.

---
*Signed: The Curator*
