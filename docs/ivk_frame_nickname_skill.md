# IVK Frame Nickname Skill Update

IVK `frame` accepts a nickname. The intake preserves the original value in `normalized.frame_ref.input` and expands it to a versioned frame pack.

| Nickname | Frame | Use |
|---|---|---|
| `svb` | Sponsor→Value Chain→Bottleneck | sponsor-to-bottleneck tracing |
| `matrix` | Matrix | comparison of a clustered company set |
| `stream` | Upstream→Midstream→Downstream | supply-chain stage and handoff mapping |

Example:

```json
{
  "name": "AI Optical Cluster",
  "seed": ["NVDA", "COHR", "LITE", "CRDO"],
  "frame": "matrix",
  "thesis": "Compare clustered companies by position and bottleneck."
}
```

Normalized output contains `primary_frame` and `frame_ref` with `id`, `version`, `nickname`, and `input`. Frame packs are stored in `packs/frames/` and registered in `registry/ivk_factory_packs.json`. A nickname selects the analysis frame only; it does not auto-confirm companies, relationships, or evidence.
