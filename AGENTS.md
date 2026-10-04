# Asset workspace

- Build, check, cache, and worker commands: [README.md — Asset development checks](README.md#asset-development-checks).
- Art references and shared components: [README.md — Reference asset set](README.md#reference-asset-set).
- Catalog metadata and export selection: [catalog/SCHEMA.md](catalog/SCHEMA.md).
- Keep GUI Blender for review; run builds and tests in isolated workers. Check commands export existing sources and never regenerate their geometry.
- Tool discovery should return names first; load one relevant schema. Print one result representation and short log tails. Full Blender logs are in `.cache/asset-check/logs/`.
