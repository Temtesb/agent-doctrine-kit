# Static-coupling invariants

## The pattern

CI tests that catch when cross-file references don't resolve — HTML `getElementById('foo')` referring to an ID that doesn't exist in any template; JS `api('foo_endpoint')` referring to an endpoint not in the server's routing table; HTML `onclick="bar()"` referring to a JS function that isn't defined. The bug class is fully determined by cross-file static coupling; the fix shape is sibling invariant tests that scan one side of the boundary and verify each reference resolves on the other side.

**Anchored to:** Foundation [F2](../01_foundations/F2_logic_holds.md) — non-contradiction applied at the file-boundary layer: a name on one side of a cross-file boundary must resolve to a definition on the other side, the same way two columns claiming to represent the same fact must agree. Also [E1](../01_foundations/E1_corpus_is_hypothesis.md) — runtime self-detection's claim to surveil correctness is a hypothesis that must be falsifiable; static-coupling failures are a class the runtime cannot observe, which means runtime detection alone is insufficient evidence the system works.

## Seed evidence

In one project, the shelf-scan upload form had eleven concrete instances of three sibling shapes in a single bug batch:

- **8 HTML/JS ID mismatches.** `getElementById('foo')` calls in JS referring to IDs that didn't exist in any HTML template.
- **2 unrouted endpoint references.** `api('foo_endpoint')` calls referring to endpoints not in the server's routing table.
- **1 missing `onclick` attribute.** An HTML element that the JS expected to have an `onclick` but didn't.

Eight of the eleven would never have produced any server-side exception in any layer — the JS would silently fail (`getElementById` returns null, subsequent property access throws an unhandled error in the browser console that the user never sees, the form's submit button does nothing). The runtime had no way to detect these.

That structural fact — the bug class is invisible to runtime detection — is what motivates filing at the static-invariant level rather than relying on runtime checks.

## The fix shape

Three sibling invariant tests, each using the `_KNOWN_ALLOWED` ratchet pattern (per [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/)):

### Test 1 — JS-IDs-resolve-in-HTML

Every `getElementById\('([a-zA-Z][\w-]*)'\)` literal in `static/js/*.js` resolves to either:

- An `id="..."` attribute in an HTML template, OR
- An `id="..."` literal inside a JS template-string (innerHTML construction — the JS itself emits the ID into the DOM dynamically)

The template-string side requires a regex over JS source to find `id="..."` patterns embedded in template literals.

### Test 2 — JS-API-endpoints-resolve-in-server

Every `api\('([\w_]+)',` (or equivalent fetch-wrapper) literal in JS resolves to a key in the registered handlers dict. The handlers dict is an in-Python literal — parse with `ast`, not regex, so renames stay accurate.

### Test 3 — HTML-handlers-resolve-in-JS

Every `on(click|change|submit|input|blur|focus)="(\w+)\(` (etc.) in HTML templates resolves to a top-level `(async )?function (\w+)` definition in JS. Same template-string caveat as Test 1 — HTML handlers built inside `innerHTML` template literals need to be scanned in JS source too.

### Documented false-negative class

IDs, endpoint names, and function names generated *inside runtime-built innerHTML template strings* won't be visible to a static grep without a brittle regex. The invariants do NOT cover that case — each test's docstring must say so explicitly.

Out-of-scope is acceptable because the bug shape this catches accounts for the vast majority of cross-file coupling instances in projects of this shape; runtime-built coupling is a separate, less-common shape that would warrant its own future check.

## Why this belongs at the stack layer

Any Python+SQLite project bootstrapped with an HTTP frontend with JS handlers will have the same coupling shape:

- `getElementById` against `id="..."`
- `api('endpoint')` against the handlers dict
- `onclick="fn()"` against JS function defs

The bug class is fully determined by the stack choice (HTML+JS+Python+SQLite) and not at all by what the project does. Filing the enforcer here means every project bootstrapped from the same stack inherits it.

## Implementation sketch

```python
# tests/test_static_coupling_invariants.py

import ast
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JS_DIR = REPO_ROOT / "static" / "js"
TEMPLATES_DIR = REPO_ROOT / "templates"


class TestJSIdsResolveInHtml(unittest.TestCase):
    """Every getElementById in JS resolves to an id="..." attribute
    in an HTML template or to a JS template-string id="..." literal."""

    _KNOWN_ALLOWED = {
        # ("filename.js", "id_name"): "reason"
    }

    def test_js_ids_resolve(self):
        # Collect every id="..." attribute from HTML templates
        html_ids = set()
        for html_path in TEMPLATES_DIR.rglob("*.html"):
            for m in re.finditer(r'id="([^"]+)"', html_path.read_text()):
                html_ids.add(m.group(1))

        # Collect every id="..." inside JS template literals (innerHTML
        # construction). This requires scanning JS for template-string
        # patterns and extracting id="..." inside them.
        js_template_ids = set()
        for js_path in JS_DIR.rglob("*.js"):
            src = js_path.read_text()
            # Heuristic: any id="..." inside a template literal (`...`)
            for m in re.finditer(r"`[^`]*id=\"([^\"]+)\"[^`]*`", src, re.DOTALL):
                js_template_ids.add(m.group(1))

        valid_ids = html_ids | js_template_ids

        # Check every getElementById call in JS
        violations = []
        for js_path in JS_DIR.rglob("*.js"):
            for m in re.finditer(
                r"getElementById\(['\"]([\w-]+)['\"]\)",
                js_path.read_text(),
            ):
                id_name = m.group(1)
                if id_name in valid_ids:
                    continue
                if (js_path.name, id_name) in self._KNOWN_ALLOWED:
                    continue
                violations.append(f"  {js_path.name}: getElementById('{id_name}')")

        if violations:
            self.fail(
                "JS getElementById calls reference IDs that don't exist "
                "in any HTML template:\n" + "\n".join(violations) +
                "\n\nFix: either add the id=\"...\" to the template, or "
                "if the ID is generated dynamically, document it in "
                "_KNOWN_ALLOWED with a justification."
            )


# Similar test classes for TestJSApiEndpointsResolveInServer and
# TestHTMLHandlersResolveInJS follow the same shape.
```

## Adopt this in your project

1. Copy the test file into your tests directory.
2. Adapt the paths (JS_DIR, TEMPLATES_DIR, the routing-dict location).
3. Run the test. Baseline existing violations into `_KNOWN_ALLOWED` with inline justifications.
4. Add to CI.

Future static-coupling shapes can land as additional sibling tests in the same file as you encounter them.

## Elevation status

**Currently staged.** Three of four elevation criteria pass:

- ✓ Generative force — explains multiple operational rules (no silent JS failures, agent-detectable bug class, F2 at file-boundary layer)
- ✓ Reduction-resistance — derives from F2 + E1 but not from the existing stack-layer rules
- ✓ Falsifiability — would be falsified by a system where runtime can detect these bugs reliably (no current system does)
- ⚠ Independent triangulation — one project sighting in deep detail; needs at least one more independent sighting before formal promotion

Adopting this in another project counts as the second sighting. File a brief note in your project's `PATTERNS.md` citing this entry as the canonical source.
