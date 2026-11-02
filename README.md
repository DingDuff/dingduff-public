# viewer-vendor

Unmodified third-party libraries that the `dingduff-citation-check` skill's
standalone review panel (`review.html`) loads when it shows a PDF or Word source
in its native layout. They live on this branch, not in the plugin, so the plugin
ships only readable source.

Each file is byte-identical to the upstream npm package named in the skill's
`viewer/vendor/MANIFEST.json`, which pins its URL (by commit) and sha256. The
panel downloads each file, checks the sha256, and refuses to run a file that
does not match. Each library's license is in its folder.

| Library | Version | File(s) | Upstream | License |
|---|---|---|---|---|
| PDF.js (`pdfjs-dist`) | 5.7.284 | `pdfjs/pdf.min.mjs`, `pdfjs/pdf.worker.min.mjs` | `package/legacy/build/` | Apache-2.0 |
| docx-preview | 0.4.0 | `docx-preview/docx-preview.min.js` | `package/dist/` | Apache-2.0 |
| JSZip | 3.10.1 | `jszip/jszip.min.js` | `package/dist/` | MIT (dual MIT/GPLv3; used under MIT) |

Never edit a file in place. To upgrade, add the new upstream file, commit, and
repin the URL and sha256 in the skill's manifest.
