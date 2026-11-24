// Browser check of interactive_app.py (Playwright + Chromium).
// 1) streamlit run interactive_app.py   2) node tools/browser_check_app.js <screenshot_dir> [url]
const { chromium, devices } = require('playwright');
(async () => {
  const out = process.argv[2];
  const browser = await chromium.launch();
  const log = (...a) => console.log(...a);
  for (const [name, ctxOpts] of [['desktop', { viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 1 }], ['mobile', devices['iPhone 13']]]) {
    const ctx = await browser.newContext(ctxOpts);
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(process.argv[3] || 'http://localhost:8501/', { waitUntil: 'networkidle' });
    await page.waitForSelector('text=Additive score', { timeout: 60000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${out}/app_${name}.png` });
    const metrics = async () => (await page.locator('[data-testid="stMetricValue"]').allInnerTexts()).slice(0, 2).join(' | ');
    const answer = async (factor, ind, value) => {
      const exp = page.locator('[data-testid="stExpander"]').filter({ hasText: factor + ' ·' }).first();
      const radio = exp.locator('[data-testid="stRadio"]').filter({ hasText: ind + ' ·' }).first();
      if (!(await radio.isVisible())) { await exp.locator('summary').first().click(); await page.waitForTimeout(600); }
      await radio.getByText(value, { exact: true }).click();
      await page.waitForTimeout(1500);
    };
    if (name === 'desktop') {
      await answer('F05', 'I11', 'Sí'); log('I11 Sí ->', await metrics());
      await answer('F11', 'I36', 'Sí'); log('+I36 Sí ->', await metrics());
      await answer('F12', 'I39', 'Sí'); log('+I39 Sí ->', await metrics());
      await answer('F05', 'I9', 'No se sabe'); log('+I9 No se sabe ->', await metrics());
      await page.screenshot({ path: `${out}/app_desktop_after_clicks.png` });
      await answer('F05', 'I9', 'No'); log('I9 No ->', await metrics());
      const body = await page.locator('body').innerText();
      log('procedure text present:', body.includes('Rule 1.6: the case stays active'));
    }
    log(name, 'console/page errors:', errors.length, errors.slice(0, 3));
    await ctx.close();
  }
  await browser.close();
})();
