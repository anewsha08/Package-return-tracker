# TODO - Package Return Tracker Dashboard

- [ ] Inspect existing webview HTML/CSS and extension webview wiring
- [x] Plan approved: update dashboard UI + wire postMessage
- [ ] Update `media/webview.html` to render dashboard (summary cards + items table)
- [ ] Update `media/webview.css` for dashboard styling
- [ ] Update `src/extension.ts` to:
  - [ ] load `media/webview.html` and `media/webview.css` rather than inline HTML
  - [ ] send mocked dashboard data into the webview via `postMessage`
- [ ] Add `window.addEventListener('message', ...)` in the webview script to render dynamic data

- [ ] Build/compile extension (`npm run compile`)
- [ ] Validate in VS Code sidebar that counts/due dates/predictions render

