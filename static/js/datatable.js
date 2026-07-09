/**
 * DataTableManager - Centralized DataTable helper for all LEOC pages.
 *
 * Provides consistent initialization, refresh, state preservation, and
 * backward-compatible `initDataTable()` / `destroyDataTable()` globals.
 *
 * Usage:
 *   DataTableManager.init('dataTable');          // first-time init
 *   DataTableManager.init('dataTable', opts);    // with options
 *   DataTableManager.refresh('dataTable', fn);   // destroy, let fn rebuild tbody, re-init
 *   DataTableManager.addRecord('dataTable', html); // append row and redraw
 *   DataTableManager.removeRecord('dataTable', id); // remove row by data-id and redraw
 */
// Global XSS-safe HTML escaper — available on every page
window.esc = function (s) {
  if (!s) return '';
  var d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
};

window.DataTableManager = (function () {
  'use strict';

  var _instances = {};

  /* ------------------------------------------------------------------ */
  /*  CSRF helper                                                        */
  /* ------------------------------------------------------------------ */
  function getCsrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function csrfHeaders() {
    return {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    };
  }

  /* ------------------------------------------------------------------ */
  /*  Internal: count effective columns (respects colspan)               */
  /* ------------------------------------------------------------------ */
  function countCols(row) {
    var n = 0;
    row.querySelectorAll('td, th').forEach(function (c) {
      n += parseInt(c.getAttribute('colspan') || '1', 10) || 1;
    });
    return n;
  }

  /* ------------------------------------------------------------------ */
  /*  Destroy — fully cleans up DataTables 2.x state so re-init works    */
  /* ------------------------------------------------------------------ */
  function destroy(tableId) {
    var id = tableId || 'dataTable';
    try {
      if (window.jQuery && jQuery.fn.DataTable && jQuery.fn.DataTable.isDataTable('#' + id)) {
        // destroy(false) removes DT internal state but keeps the table in the DOM
        jQuery('#' + id).DataTable().destroy(false);
      }
    } catch (e) { /* silent */ }

    // DataTables 2.x leaves a wrapper div; move the table out before removing it
    var el = document.getElementById(id);
    if (el) {
      var wrapper = el.closest('.dataTables_wrapper');
      if (wrapper) {
        var parent = wrapper.parentNode;
        parent.insertBefore(el, wrapper);
        wrapper.remove();
      }
      el.classList.remove('dataTable', 'no-footer', 'cell-border');
      // Remove any extra <thead> rows DataTables may have injected
      var extraRows = el.querySelectorAll('thead tr + tr');
      extraRows.forEach(function(r) { r.remove(); });
    }
    delete _instances[id];
  }

  /* ------------------------------------------------------------------ */
  /*  Init                                                               */
  /* ------------------------------------------------------------------ */
  function init(tableId, opts) {
    var id = tableId || 'dataTable';
    opts = opts || {};

    var el = document.getElementById(id);
    if (!el) return null;
    if (!(window.jQuery && jQuery.fn && jQuery.fn.DataTable)) return null;

    // ---- snapshot tbody BEFORE destroying ----
    // DataTables destroy(false) restores the original tbody content (the data
    // from when DT was first initialized), which would overwrite the new rows
    // the render function just set. We save them here and restore after destroy.
    var tbodySnap = el.querySelector('tbody');
    var savedHtml = tbodySnap ? tbodySnap.innerHTML : '';

    // ---- tear down any existing instance ----
    destroy(id);

    // Re-fetch el: destroy() moves the table out of the dataTables_wrapper
    el = document.getElementById(id);
    if (!el) return null;

    // ---- restore the new rows that destroy() may have reverted ----
    var tbody = el.querySelector('tbody');
    if (tbody && savedHtml) {
      tbody.innerHTML = savedHtml;
    }

    // ---- skip init when tbody has no real data rows ----
    var rows = el.querySelectorAll('tbody tr');
    var hasRealData = false;
    for (var i = 0; i < rows.length; i++) {
      if (!rows[i].querySelector('td[colspan]')) { hasRealData = true; break; }
    }
    if (!hasRealData) return null;

    // ---- column-count sanity check (first thead row only) ----
    var firstHeaderRow = el.querySelector('thead tr');
    var headerCols = firstHeaderRow ? firstHeaderRow.querySelectorAll('th').length : 0;
    var bodyCols = countCols(rows[0]);
    if (headerCols > 0 && bodyCols !== headerCols) return null;

    // suppress DataTables visual error popups
    jQuery.fn.DataTable.ext.errMode = 'none';

    var disableLastSort = opts.disableLastSort !== false;

    try {
      var dt = jQuery('#' + id).DataTable({
        paging: true,
        ordering: true,
        info: true,
        searching: true,
        pageLength: opts.pageLength || 10,
        lengthMenu: opts.lengthMenu || [[10, 25, 50, 100], [10, 25, 50, 100]],
        order: opts.order || [],
        columnDefs: disableLastSort ? [{ orderable: false, targets: -1 }] : [],
        language: {
          search: '',
          searchPlaceholder: 'Search records...',
          lengthMenu: 'Show _MENU_ entries',
          info: 'Showing _START_ to _END_ of _TOTAL_ entries',
          infoEmpty: 'Showing 0 to 0 of 0 entries',
          emptyTable: 'No data available'
        },
        dom:
          '<"row mb-2"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
          '<"row"<"col-sm-12"tr>>' +
          '<"row mt-2"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>'
      });

      _instances[id] = dt;

      return dt;
    } catch (e) {
      console.error('DataTableManager.init error:', e);
      return null;
    }
  }

  /* ------------------------------------------------------------------ */
  /*  Refresh: destroy → let caller rebuild tbody → re-init              */
  /* ------------------------------------------------------------------ */
  function refresh(tableId, rebuildFn) {
    var id = tableId || 'dataTable';
    destroy(id);
    if (typeof rebuildFn === 'function') rebuildFn();
    return init(id);
  }

  /* ------------------------------------------------------------------ */
  /*  Row-level helpers (operate on live DataTable without full refresh)  */
  /* ------------------------------------------------------------------ */

  /** Append a <tr> to the table body and redraw. */
  function addRow(tableId, trHtml) {
    var dt = _instances[tableId || 'dataTable'];
    if (!dt) return false;
    var tbody = document.querySelector('#' + (tableId || 'dataTable') + ' tbody');
    if (!tbody) return false;
    var placeholder = tbody.querySelector('td[colspan]');
    if (placeholder) placeholder.closest('tr').remove();
    var tmp = document.createElement('tbody');
    tmp.innerHTML = trHtml;
    var newRow = tmp.querySelector('tr');
    if (newRow) {
      dt.row.add(newRow).draw(false);
    }
    return true;
  }

  /** Remove a <tr> identified by a data-id attribute and redraw. */
  function removeRow(tableId, recordId) {
    var dt = _instances[tableId || 'dataTable'];
    if (!dt) return false;
    var found = false;
    dt.rows().every(function () {
      var node = this.node();
      if (node && node.getAttribute('data-id') === String(recordId)) {
        this.remove().draw(false);
        found = true;
      }
    });
    return found;
  }

  /** Replace a <tr> identified by data-id and redraw. */
  function updateRow(tableId, recordId, newTrHtml) {
    var dt = _instances[tableId || 'dataTable'];
    if (!dt) return false;
    var replaced = false;
    dt.rows().every(function () {
      var node = this.node();
      if (node && node.getAttribute('data-id') === String(recordId)) {
        var tmp = document.createElement('tr');
        tmp.innerHTML = newTrHtml;
        tmp.setAttribute('data-id', String(recordId));
        var cells = tmp.querySelectorAll('td');
        var oldCells = node.querySelectorAll('td');
        for (var i = 0; i < cells.length && i < oldCells.length; i++) {
          oldCells[i].innerHTML = cells[i].innerHTML;
        }
        dt.draw(false);
        replaced = true;
      }
    });
    return replaced;
  }

  /** Get the stored DataTable instance (or null). */
  function getInstance(tableId) {
    return _instances[tableId || 'dataTable'] || null;
  }

  /* ------------------------------------------------------------------ */
  /*  AJAX helper: generic CRUD fetch with CSRF & toast                  */
  /* ------------------------------------------------------------------ */
  async function apiRequest(url, method, body) {
    var opts = { method: method, headers: csrfHeaders() };
    if (body !== undefined) opts.body = JSON.stringify(body);
    var resp = await fetch(url, opts);
    return resp.json();
  }

  /* ------------------------------------------------------------------ */
  /*  Backward-compatible globals                                        */
  /* ------------------------------------------------------------------ */
  window.destroyDataTable = destroy;
  window.initDataTable = init;

  /* ------------------------------------------------------------------ */
  /*  Public API                                                         */
  /* ------------------------------------------------------------------ */
  return {
    init: init,
    destroy: destroy,
    refresh: refresh,
    addRow: addRow,
    removeRow: removeRow,
    updateRow: updateRow,
    getInstance: getInstance,
    getCsrfToken: getCsrfToken,
    csrfHeaders: csrfHeaders,
    apiRequest: apiRequest
  };
})();
