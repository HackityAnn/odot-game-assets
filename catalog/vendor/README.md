# Bundled viewer dependencies

`model-viewer.min.js` and `LICENSE-model-viewer` are the locally bundled files
reused from this repository's original review gallery. Its dependency notices
are embedded in the bundle. No runtime CDN is used by the catalog.

Compression support is also local, configured before the first viewer is created:

| Files | Upstream version and source | License |
| --- | --- | --- |
| `draco/*` | [Draco 1.5.6](https://www.gstatic.com/draco/versioned/decoders/1.5.6/) | `LICENSE-draco` |
| `basis/*` | [Basis Universal 2021-04-15-ba1c3e4](https://www.gstatic.com/basis-universal/versioned/2021-04-15-ba1c3e4/) | `LICENSE-basis` |
| `meshopt_decoder.js` | [meshoptimizer v0.20](https://github.com/zeux/meshoptimizer/tree/v0.20/js) | `LICENSE-meshopt` |

The Draco and Basis versions match the bundled viewer's original decoder defaults.
The catalog does not enable AR, remote environments, or animated Lottie textures.
Repository GLBs embed their own geometry and materials. If upgrading the viewer,
review its decoder compatibility and retain the dependency license notices.
