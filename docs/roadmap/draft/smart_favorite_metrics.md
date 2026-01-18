# Feature Idea: Smart "Favorite Albums" Metric

## Context
Currently, library analysis aggregates album counts generically. The user wants a more nuanced "Favorite Albums" metric.

## Definition
An album is considered a "Favorite" if:
1.  The album itself is marked as 'starred' (favorite).
2.  OR: The album contains at least one track marked as 'starred' (heart).

## Implementation Ideas
- Update `analyze_library` to scan for this specific condition.
- This might require a heavier scan than simple `getAlbumList2(type='starred')`.
- Potential Optimization: Use `getStarred()` for songs, extract unique `albumId`s, and combine with `getStarred()` for albums.

## Impact
- Better "Taste Profile" accuracy.
- More relevant "Rediscover" candidates.
