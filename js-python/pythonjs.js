const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function generatePDF(htmlFilePath, outputFilePath) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  const contentHtml = fs.readFileSync(htmlFilePath, 'utf8');

  await page.setContent(contentHtml, {
    waitUntil: 'networkidle0'
  });
  await page.pdf({
    path: outputFilePath,
    format: 'A4',
    printBackground: true
  });

  await browser.close();
}

const [htmlFilePath, outputFilePath] = process.argv.slice(2);
generatePDF(htmlFilePath, outputFilePath)
  .then(() => console.log(`PDF generated: ${outputFilePath}`))
  .catch(err => console.error(err));
