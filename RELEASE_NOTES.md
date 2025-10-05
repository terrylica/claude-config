
## 2.5.0 - 2025-10-05


### ✨ New Features

- Enable dual SSH tunnel and Pushover notifications Replace fallback logic with parallel dual notification architecture. Both SSH tunnel (macOS audio) and Pushover (mobile) now send simultaneously on Linux SSH environments, ensuring reliable mobile notifications even when tunnel succeeds but lacks listener. - Send to SSH tunnel for local macOS audio playback - Send to Pushover for mobile notifications (always) - Success if either method completes

- Add configurable Pushover notification sound Read sound parameter from CNS config pushover.default_sound, defaulting to 'toy_story' if not specified. Enables consistent notification sounds across both local and remote environments.



### 📝 Other Changes

- Version 2.1.0 → 2.2.0

- Version 2.2.0 → 2.3.0

- Version 2.3.0 → 2.4.0

- Version 2.4.0 → 2.5.0



---
**Full Changelog**: https://github.com/Eon-Labs/rangebar/compare/v2.2.0...v2.5.0
