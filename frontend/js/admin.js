/**
 * IntelliTransit - Admin Console Client
 */
import { api } from './api.js';
import { auth } from './auth.js';
import { formatCurrency, formatDateTime } from './utils.js';

document.addEventListener('DOMContentLoaded', async () => {
  await auth.initAuthNav();

  // Check admin role
  const user = auth.getUser();
  if (!user || user.role !== 'ADMIN') {
    alert('Access restricted to administrators only.');
    window.location.href = '/login.html';
    return;
  }

  const statUsers = document.getElementById('statUsers');
  const statJourneys = document.getElementById('statJourneys');
  const statRevenue = document.getElementById('statRevenue');
  const statTickets = document.getElementById('statTickets');
  const statPasses = document.getElementById('statPasses');
  const refreshMetricsBtn = document.getElementById('refreshMetricsBtn');

  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  const servicesTableBody = document.getElementById('servicesTableBody');
  const faresTableBody = document.getElementById('faresTableBody');
  const usersTableBody = document.getElementById('usersTableBody');
  const validationsTableBody = document.getElementById('validationsTableBody');

  // Tab switching
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.getAttribute('data-tab');
      document.getElementById(target)?.classList.add('active');
    });
  });

  if (refreshMetricsBtn) {
    refreshMetricsBtn.addEventListener('click', loadAllAdminData);
  }

  // Initial load
  loadAllAdminData();

  async function loadAllAdminData() {
    loadMetrics();
    loadServicesAndFares();
    loadUsers();
    loadValidations();
  }

  async function loadMetrics() {
    try {
      const res = await api.get('/api/admin/metrics');
      if (res && res.data) {
        const m = res.data;
        statUsers.textContent = m.total_users || 0;
        statJourneys.textContent = m.total_journeys || 0;
        statRevenue.textContent = formatCurrency(m.total_revenue || 0);
        statTickets.textContent = m.active_tickets || 0;
        statPasses.textContent = m.active_passes || 0;
      }
    } catch (e) {
      console.warn('Could not load admin metrics:', e);
    }
  }

  async function loadServicesAndFares() {
    try {
      const sRes = await api.get('/api/admin/services');
      if (sRes && sRes.data && sRes.data.services) {
        servicesTableBody.innerHTML = sRes.data.services.map(s => `
          <tr style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 8px; font-weight: 600;">${s.service_name}</td>
            <td style="padding: 8px;">${s.operator_name}</td>
            <td style="padding: 8px;"><span class="badge badge-mode badge-${s.mode}">${s.mode}</span></td>
            <td style="padding: 8px;"><span class="badge ${s.is_active ? 'badge-success' : 'badge-error'}">${s.is_active ? 'ACTIVE' : 'INACTIVE'}</span></td>
          </tr>
        `).join('');
      }

      const fRes = await api.get('/api/admin/fares');
      if (fRes && fRes.data && fRes.data.fares) {
        faresTableBody.innerHTML = fRes.data.fares.map(f => `
          <tr style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 8px; font-weight: 600;">${f.service_name || f.mode || 'Transit Service'}</td>
            <td style="padding: 8px;">${formatCurrency(f.base_fare || 0)}</td>
            <td style="padding: 8px;">${formatCurrency(f.per_km_rate || 0)}/km</td>
            <td style="padding: 8px;">${formatCurrency(f.min_fare || 0)}</td>
            <td style="padding: 8px;">${formatDateTime(f.effective_from)}</td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.warn('Could not load services/fares:', e);
    }
  }

  async function loadUsers() {
    try {
      const uRes = await api.get('/api/admin/users?limit=20');
      if (uRes && uRes.data && uRes.data.users) {
        usersTableBody.innerHTML = uRes.data.users.map(u => `
          <tr style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 8px; font-weight: 600;">${u.full_name}</td>
            <td style="padding: 8px;">${u.email}</td>
            <td style="padding: 8px;"><span class="badge badge-info">${u.role}</span></td>
            <td style="padding: 8px;"><span class="badge ${u.is_active ? 'badge-success' : 'badge-error'}">${u.is_active ? 'Active' : 'Suspended'}</span></td>
            <td style="padding: 8px;">
              <button class="btn btn-outline btn-sm" onclick="alert('User status managed.')">Manage</button>
            </td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.warn('Could not load users:', e);
    }
  }

  async function loadValidations() {
    try {
      const vRes = await api.get('/api/admin/validations?limit=20');
      if (vRes && vRes.data && vRes.data.validations) {
        validationsTableBody.innerHTML = vRes.data.validations.map(v => `
          <tr style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 8px;">${formatDateTime(v.validation_time)}</td>
            <td style="padding: 8px;">${v.validator_name || 'Inspector'}</td>
            <td style="padding: 8px;"><span class="badge ${v.validation_status === 'VALID' ? 'badge-success' : 'badge-error'}">${v.validation_status}</span></td>
            <td style="padding: 8px;">${v.origin && v.destination ? `${v.origin} → ${v.destination}` : 'Pass Scan'}</td>
            <td style="padding: 8px; font-size: 0.85rem; color: var(--color-text-secondary);">${v.remarks || '-'}</td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.warn('Could not load validations:', e);
    }
  }
});
