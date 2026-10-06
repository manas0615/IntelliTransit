/**
 * IntelliTransit - Conductor & Gate Validation Client
 */
import { api } from './api.js';
import { auth } from './auth.js';
import { formatCurrency, formatDateTime } from './utils.js';

document.addEventListener('DOMContentLoaded', async () => {
  const user = auth.getUser();
  if (!auth.isAuthenticated() || !user || user.role !== 'ADMIN') {
    sessionStorage.setItem('auth_flash_message', 'Conductor access required. Please sign in with an authorized conductor account.');
    window.location.replace('/login.html?mode=conductor');
    return;
  }
  await auth.initAuthNav();

  const validateForm = document.getElementById('validateForm');
  const tokenInput = document.getElementById('tokenInput');
  const scanBtn = document.getElementById('scanBtn');
  const clearBtn = document.getElementById('clearBtn');
  const resultSuccess = document.getElementById('resultSuccess');
  const successMessage = document.getElementById('successMessage');
  const ticketDetailsContainer = document.getElementById('ticketDetailsContainer');
  const resultError = document.getElementById('resultError');
  const errorMessage = document.getElementById('errorMessage');
  const errorDetails = document.getElementById('errorDetails');
  const historyTableBody = document.getElementById('historyTableBody');
  const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

  // Load initial validation history
  loadRecentHistory();

  validateForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const token = tokenInput.value.trim();
    if (!token) return;

    scanBtn.disabled = true;
    scanBtn.innerHTML = '<span>Verifying...</span>';
    resultSuccess.style.display = 'none';
    resultError.style.display = 'none';

    try {
      const response = await api.post('/api/validation/validate', {
        token: token,
        remarks: 'Manual Web Conductor Terminal Scan'
      });

      if (response && (response.success === true || response.status === 'success')) {
        renderSuccess(response.data, response.message);
        tokenInput.value = '';
        tokenInput.focus();
        loadRecentHistory();
      } else {
        renderError(response?.message || 'Validation failed.', response?.data);
      }
    } catch (err) {
      renderError(err.message || 'Validation rejected.', err.data);
    } finally {
      scanBtn.disabled = false;
      scanBtn.innerHTML = '<span>🔍 Validate Entry</span>';
    }
  });

  clearBtn.addEventListener('click', () => {
    tokenInput.value = '';
    resultSuccess.style.display = 'none';
    resultError.style.display = 'none';
    tokenInput.focus();
  });

  if (refreshHistoryBtn) {
    refreshHistoryBtn.addEventListener('click', loadRecentHistory);
  }

  function renderSuccess(data, message) {
    resultSuccess.style.display = 'block';
    resultError.style.display = 'none';
    successMessage.textContent = message || 'Ticket successfully consumed.';

    if (data.type === 'PASS') {
      ticketDetailsContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div><strong>Pass Type:</strong> <span class="badge" style="background: #e0e7ff; color: #4338ca;">${data.pass_type} PASS</span></div>
          <div><strong>Applicable Mode:</strong> <span class="badge-mode badge-${data.applicable_mode}">${data.applicable_mode}</span></div>
          <div><strong>Valid Until:</strong> ${formatDateTime(data.valid_until)}</div>
          <div><strong>Pass Status:</strong> <span class="badge badge-success">ACTIVE (UNLIMITED RIDES)</span></div>
        </div>
      `;
    } else {
      ticketDetailsContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div><strong>Mode:</strong> <span class="badge-mode badge-${data.mode || 'BUS'}">${data.mode || 'BUS'}</span></div>
          <div><strong>Operator:</strong> ${data.operator || 'PMPML'}</div>
          <div><strong>Origin:</strong> ${data.origin || 'Origin'}</div>
          <div><strong>Destination:</strong> ${data.destination || 'Destination'}</div>
          <div><strong>Fare Paid:</strong> ${formatCurrency(data.fare || 0)}</div>
          <div><strong>Status:</strong> <span class="badge badge-info">CONSUMED (USED)</span></div>
        </div>
      `;
    }
  }

  function renderError(message, data) {
    resultError.style.display = 'block';
    resultSuccess.style.display = 'none';
    errorMessage.textContent = message;
    if (data && data.code) {
      errorDetails.textContent = `Error Code: ${data.code} | Item: ${data.ticket_id || data.type || 'Unknown'}`;
    } else {
      errorDetails.textContent = '';
    }
  }

  async function loadRecentHistory() {
    try {
      const res = await api.get('/api/validation/history?limit=10');
      if (res && res.data && res.data.validations) {
        const list = res.data.validations;
        if (list.length === 0) {
          historyTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-secondary" style="padding: 16px;">No validation scans recorded yet.</td></tr>`;
          return;
        }

        historyTableBody.innerHTML = list.map(v => {
          const isSuccess = v.validation_status === 'SUCCESS';
          const badgeClass = isSuccess ? 'badge-success' : 'badge-error';
          const route = v.origin && v.destination ? `${v.origin} → ${v.destination}` : 'Pass Scan';
          return `
            <tr style="border-bottom: 1px solid var(--color-border);">
              <td style="padding: 8px;">${formatDateTime(v.validation_time)}</td>
              <td style="padding: 8px; font-family: monospace;">${(v.ticket_id || '').substring(0, 8)}...</td>
              <td style="padding: 8px;"><span class="badge ${badgeClass}">${v.validation_status}</span></td>
              <td style="padding: 8px;">${route} (${v.remarks || ''})</td>
            </tr>
          `;
        }).join('');
      }
    } catch (e) {
      console.warn('Could not load validation history:', e);
    }
  }
});
