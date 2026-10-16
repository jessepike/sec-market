import { chromium } from '@playwright/test'
const browser = await chromium.launch()
for (const [label, width, height] of [['1440x900',1440,900],['390x844',390,844]]) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)
  const data = await page.evaluate(() => {
    const main = document.querySelector('main')
    const h1 = document.querySelector('h1')
    const firstSectionInMain = main ? main.querySelector('section') : null
    function top(el) { return el ? Math.round(el.getBoundingClientRect().top + window.scrollY) : null }
    return { mainTop: top(main), h1Top: top(h1), firstSectionTop: top(firstSectionInMain) }
  })
  console.log(label, JSON.stringify(data), 'chromePct(mainTop/vh)=', Math.round(data.mainTop/height*1000)/10, '%')
  await page.close()
}
await browser.close()
