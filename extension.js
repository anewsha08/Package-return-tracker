"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
function activate(context) {
    const provider = new ReturnTrackerSidebarProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(ReturnTrackerSidebarProvider.viewType, provider, {
        webviewOptions: {
            retainContextWhenHidden: true
        }
    }));
}
function deactivate() {
    // Clean up resources if necessary.
}
class ReturnTrackerSidebarProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView, _context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(this._extensionUri, 'media')]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // Post initial mocked dashboard data.
        this._postDashboardData();
    }
    _getHtmlForWebview(webview) {
        const cssUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'webview.css'));
        // Self-contained HTML (no Node fs usage in extension build).
        return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Return Dashboard</title>
  <link rel="stylesheet" href="${cssUri.toString()}" />
</head>
<body>
  <div class="container">
    <header class="hero">
      <h1>Package Return Tracker</h1>
      <p>Return deadlines + ML prediction summary</p>
    </header>

    <section class="summary" aria-label="Return summary">
      <div class="summary-card">
        <div class="summary-label">Total Items</div>
        <div id="totalItems" class="summary-value">—</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Not Returned</div>
        <div id="notReturnedItems" class="summary-value">—</div>
        <div class="summary-sub">Satisfied / keep product</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Returned</div>
        <div id="returnedItems" class="summary-value">—</div>
      </div>
    </section>

    <section class="card" aria-label="Items table">
      <div class="card-header">
        <h2>Items</h2>
        <div class="card-meta"><span id="lastUpdated">Last updated: —</span></div>
      </div>
      <div class="table-wrap">
        <table class="items-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Status</th>
              <th>Return Due</th>
              <th>ML Prediction</th>
            </tr>
          </thead>
          <tbody id="itemsTbody"></tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
    const fmtDate = (iso) => {
      try {
        return new Date(iso).toLocaleDateString();
      } catch (e) {
        return iso;
      }
    };

    const el = (id) => document.getElementById(id);

    function render(data) {
      if (!data) return;

      el('totalItems').textContent = String(data.totals.totalItems ?? 0);
      el('notReturnedItems').textContent = String(data.totals.notReturnedItems ?? 0);
      el('returnedItems').textContent = String(data.totals.returnedItems ?? 0);
      el('lastUpdated').textContent = 'Last updated: ' + (data.lastUpdatedISO ? fmtDate(data.lastUpdatedISO) : '—');

      const tbody = el('itemsTbody');
      tbody.innerHTML = '';

      for (const item of data.items || []) {
        const tr = document.createElement('tr');

        const status = item.returned ? 'Returned' : 'Not Returned';
        const statusClass = item.returned ? 'status returned' : 'status not-returned';

        const action = item.mlPrediction?.recommendedAction ?? '—';
        const prob = item.mlPrediction?.returnProbability;
        const conf = item.mlPrediction?.confidence;

        const actionText = action + ' (' + (typeof prob === 'number' ? Math.round(prob * 100) + '%' : '—') + ')';
        const confText = typeof conf === 'number' ? 'Confidence: ' + Math.round(conf * 100) + '%' : '';

        tr.innerHTML = [
          '<td class="cell-product">' + (item.productName ?? '') + '</td>',
          '<td class="cell-status"><span class="' + statusClass + '">' + status + '</span></td>',
          '<td class="cell-due">' + fmtDate(item.dueDateISO) + '</td>',
          '<td class="cell-ml">'
            + '<div class="ml-action">' + actionText + '</div>'
            + '<div class="ml-meta">' + confText + ' • ' + (item.mlPrediction?.modelVersion ?? '') + '</div>'
            + '</td>'
        ].join('');






        tbody.appendChild(tr);
      }
    }

    window.addEventListener('message', (event) => {
      const msg = event.data;
      if (msg && msg.type === 'dashboard-data') {
        render(msg.payload);
      }
    });
  </script>
</body>
</html>`;
    }
    _postDashboardData() {
        if (!this._view)
            return;
        const now = new Date();
        const addDays = (days) => new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
        const toISODate = (d) => d.toISOString();
        const items = [
            {
                id: 'item-001',
                productName: 'Wireless Mouse',
                returned: false,
                dueDateISO: toISODate(addDays(6)),
                mlPrediction: {
                    returnProbability: 0.08,
                    recommendedAction: 'Keep',
                    confidence: 0.86,
                    modelVersion: 'ret-v0.1'
                }
            },
            {
                id: 'item-002',
                productName: 'Noise Cancelling Headphones',
                returned: true,
                dueDateISO: toISODate(addDays(-2)),
                mlPrediction: {
                    returnProbability: 0.72,
                    recommendedAction: 'Return',
                    confidence: 0.74,
                    modelVersion: 'ret-v0.1'
                }
            },
            {
                id: 'item-003',
                productName: 'Smart Watch Band',
                returned: false,
                dueDateISO: toISODate(addDays(13)),
                mlPrediction: {
                    returnProbability: 0.14,
                    recommendedAction: 'Keep',
                    confidence: 0.81,
                    modelVersion: 'ret-v0.1'
                }
            }
        ];
        const totals = {
            totalItems: items.length,
            returnedItems: items.filter((i) => i.returned).length,
            notReturnedItems: items.filter((i) => !i.returned).length
        };
        const data = {
            totals,
            items: items.sort((a, b) => a.dueDateISO.localeCompare(b.dueDateISO)),
            lastUpdatedISO: now.toISOString()
        };
        this._view.webview.postMessage({
            type: 'dashboard-data',
            payload: data
        });
    }
}
ReturnTrackerSidebarProvider.viewType = 'packageReturnTracker.sidebarView';
//# sourceMappingURL=extension.js.map