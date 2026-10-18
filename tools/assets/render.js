#!/usr/bin/env node
'use strict';
/* Render the startupbase.uno image assets from the HTML templates in ./src.
   Reproduces the local build geometry: CSS viewport size x deviceScaleFactor 2. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SRC = path.resolve(__dirname, 'src');
const OUT = path.resolve(__dirname, 'out');

// [template, width, height, scale, outName, transparent]
const JOBS = [
  ['fig1.html',       1440, 810, 2, 'fig-1-architecture.png', false],
  ['fig2.html',       1440, 810, 2, 'fig-2-terminal.png',     false],
  ['fig3.html',       1440, 810, 2, 'fig-3-benchmarks.png',   false],
  ['cover.html',      1440, 810, 2, 'cover.png',              false],
  ['og-article.html', 1200, 630, 2, 'og-article@2x.png',      false],
  ['og-blog.html',    1200, 630, 2, 'og-blog@2x.png',         false],
  ['logo-dark.html',   900, 160, 2, 'logo-dark@2x.png',       true],
  ['logo-light.html',  900, 160, 2, 'logo-light@2x.png',      true],
  ['mark-512.html',    512, 512, 2, 'mark-m4-512.png',        true],
  ['appicon.html',     512, 512, 2, 'app-icon.png',           false],
];

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
  });

  for (const [tpl, w, h, scale, name, transparent] of JOBS) {
    const ctx = await browser.newContext({
      viewport: { width: w, height: h },
      deviceScaleFactor: scale,
    });
    const page = await ctx.newPage();
    await page.goto('file://' + path.join(SRC, tpl), { waitUntil: 'load' });
    // make sure webfont/installed fonts are resolved before shooting
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);
    await page.screenshot({
      path: path.join(OUT, name),
      omitBackground: transparent,
      fullPage: false,
    });
    const size = fs.statSync(path.join(OUT, name)).size;
    console.log(`${name}: ${w}x${h}@${scale} -> ${size} B`);
    await ctx.close();
  }

  await browser.close();
  console.log('render done');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
