const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
  page.on('pageerror', e => errors.push('PAGEERR: ' + e.message));

  const base = 'http://127.0.0.1:5055';
  await page.goto(base + '/login', { waitUntil: 'networkidle0' });
  await page.type('input[name=username]', 'admin');
  await page.type('input[name=password]', 'admin123');
  await page.click('button[type=submit]');
  await page.waitForNavigation({ waitUntil: 'networkidle0' }).catch(()=>{});

  const pages = ['differently_abled','volunteers','rrt','high_risk_population','vulnerable_population'];
  for (const p of pages) {
    await page.goto(base + '/' + p, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1500));
    const before = await page.evaluate(() => {
      const dt = window.jQuery && jQuery.fn.DataTable.isDataTable('#dataTable') ? jQuery('#dataTable').DataTable() : null;
      return dt ? dt.rows().count() : document.querySelectorAll('#dataTable tbody tr').length;
    });
    let added = 'skip';
    try {
      if (p === 'differently_abled') {
        await page.click('button[data-bs-target="#daModal"]');
        await new Promise(r => setTimeout(r, 600));
        await page.type('#person_name', 'TESTPERSON_' + Date.now());
        await page.select('#gender', 'Male');
        await page.type('#age', '30');
        await page.click('#daForm button[type=submit]');
        added = 'clicked';
      } else if (p === 'volunteers') {
        await page.click('button[data-bs-target="#volunteerModal"]');
        await new Promise(r => setTimeout(r, 600));
        await page.type('#vol_name', 'TESTVOL_' + Date.now());
        await page.type('#vol_contact', '9800000000');
        await page.select('#vol_ward_id', await page.evaluate(()=>document.querySelector('#vol_ward_id option:not([value=""])').value));
        await page.click('#volunteerForm button[type=button][onclick="saveRecord()"]');
        added = 'clicked';
      } else if (p === 'rrt') {
        await page.click('button[data-bs-target="#formModal"]');
        await new Promise(r => setTimeout(r, 600));
        await page.type('#team_name', 'TESTTEAM_' + Date.now());
        await page.select('#team_type', await page.evaluate(()=>document.querySelector('#team_type option:not([value=""])').value));
        await page.type('#contact_number', '9800000000');
        await page.click('#formModal button[type=button][onclick="saveRecord()"]');
        added = 'clicked';
      }
    } catch (e) { errors.push(p + ' add-err: ' + e.message); }

    await new Promise(r => setTimeout(r, 2500));
    const after = await page.evaluate(() => {
      const dt = window.jQuery && jQuery.fn.DataTable.isDataTable('#dataTable') ? jQuery('#dataTable').DataTable() : null;
      return dt ? dt.rows().count() : document.querySelectorAll('#dataTable tbody tr').length;
    });
    console.log(`PAGE=${p} before=${before} after=${after} added=${added}`);
  }
  if (errors.length) console.log('ERRORS:\n' + errors.join('\n'));
  await browser.close();
})();
