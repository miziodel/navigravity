# Technical Note: MCP Server Feedback (Black Box Analysis)

**Date**: 2026-01-11
**Source**: User Session Feedback
**Context**: Black box analysis of `navigravity` MCP server during agentic interaction.

## Executive Summary
This document captures critical functional issues observed "from the outside" during agent usage. These issues directly impact the reliability of automation chains and user trust in the tool's filtering capabilities.

---

## 1. ID Inconsistency ("Song not found")
**Severity**: Critical
**Component**: `assess_playlist_quality` / ID Persistence

### Observation
During the playlist verification phase (`assess_playlist_quality`), the server responded with "Song not found" for an ID that the server itself had provided just moments earlier in a candidate list.

### Impact
- **Breaks Automation Chains**: The agent cannot trust the IDs returned by the server for subsequent operations.
- **Workflow Interruption**: Causes fatal errors in strict verification steps.

### Hypothesis
- **Transient IDs**: There may be a persistence issue where IDs are volatile between calls.
- **Indexing Latency**: A potential latency in the Subsonic/Navidrome indexing or cache where an ID is "invisible" immediately after retrieval.

### Proposed Action
- Investigate ID stability in the Subsonic API integration.
- Implement robust retry logic or cache coherency checks.
- Ensure `assess_playlist_quality` performs a fresh lookup if the cached instance is missing.

---

## 2. Silent Parameters (The Case of the Ignored Mood)
**Severity**: Medium
**Component**: `get_smart_candidates` (Mode: `top_rated`)

### Observation
Explicitly requested candidates with `mode='top_rated'` combined with `mood='energy'`.
**Result**: Returned tracks like "Comfortably Numb" (Pink Floyd) or Nick Drake songs—excellent quality, but effectively ZERO energy.

### Feedback
It appears the `mood` parameter is silently ignored in certain modes (specifically `top_rated`).
- **Misleading Behavior**: The agent assumes the filter is applied and trusts the output, leading to contextually inappropriate results.

### Proposed Action
- **Explicit Validation**: If a parameter combination is unsupported (e.g., `top_rated` does not support `mood` filtering), the server should either:
    1.  Return a warning in the response metadata.
    2.  Throw a descriptive error (Fail Fast).
    3.  Correctly implement the intersection of Top Rated + Mood.

---

## 3. "All or Nothing" Search
**Severity**: Medium
**Component**: `search_music_enriched`

### Observation
Performed searches for specific artists (e.g., "Bicep", "Populous") returning completely empty lists `[]`.

### Feedback
The current search behavior is opaque:
- It is unclear if the artist is genuinely missing from the library.
- Or if the search is too strict (e.g., case-sensitive, exact match requirements).

### Proposed Action
- **Fuzzy Fallback**: If an exact match returns 0 results, trigger a "fuzzy" search mechanism.
- **Did You Mean?**: Return partial matches or similar names to help the agent correct its query (e.g. knowing it's a spelling or formatting issue vs. missing content).
