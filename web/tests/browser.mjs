import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
const result={checks:[],externalRequests:[],consoleErrors:[],axe:[],screenshots:[],passed:false};
const label=process.argv[2]||'baseline';
if(!/^[a-z0-9-]+$/.test(label))throw new Error('Invalid audit label');
const out=`../results/screenshots/${label}`;fs.mkdirSync(out,{recursive:true});
let browser;
try{
 browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext();
 const page=await context.newPage();
 page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4173')&&!r.url().startsWith('data:'))result.externalRequests.push(r.url())});
 page.on('pageerror',e=>result.consoleErrors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')result.consoleErrors.push(m.text())});
 for(const [width,height] of [[1920,1080],[1440,900],[1280,720],[768,1024]]){
  await page.setViewportSize({width,height});await page.goto('http://127.0.0.1:4173');
  for(const theme of ['light','dark']){
   if(theme==='dark')await page.getByRole('button',{name:'Night desk',exact:true}).click();
   for(const section of await page.locator('main section').all()){
    const id=await section.getAttribute('id');await section.scrollIntoViewIfNeeded();
    const file=`${out}/${width}-${height}-${theme}-${id}.png`;await page.screenshot({path:file});result.screenshots.push(file);
   }
   const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   result.axe.push({width,height,theme,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Horizontal overflow');
  }
 }
 await page.locator('#scenario').selectOption('reject_slash');
 if(!(await page.locator('#what-could-change-it').getByRole('status').innerText()).includes('36.61'))throw new Error('Scenario does not update');result.checks.push('Scenario updates to computed values');
 await page.locator('#reason').selectOption('INVALID_DATE');
 if(await page.locator('.receipts article').count()!==2)throw new Error('Receipt filter failed');result.checks.push('Rejection filter matches evidence');
 result.checks.push('Eight theme/viewport combinations without overflow');
 result.passed=!result.consoleErrors.length&&!result.externalRequests.length&&result.axe.every(x=>!x.violations.length);
}catch(e){result.failure=String(e).split("\n")[0]}finally{if(browser)await browser.close();fs.writeFileSync(`../results/ui-${label}.json`,JSON.stringify(result,null,2));fs.writeFileSync('../results/ui.json',JSON.stringify(result,null,2));console.log(JSON.stringify({...result,screenshots:result.screenshots.length},null,2));if(!result.passed)process.exitCode=1}
