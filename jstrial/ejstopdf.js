const fs = require('fs');
const ejs = require('ejs');
const puppeteer = require('puppeteer');
const path = require('path');

const directoryName = 'renders';
const templateName = 't2table.ejs'; // Ensure your template is renamed to .ejs
const dataName = 'data1.json';

// Create directory if it doesn't exist
if (!fs.existsSync(directoryName)) {
  fs.mkdirSync(directoryName, { recursive: true });
}

// Function to render PDF from HTML
async function generatePDF(htmlContent, outputFilename) {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
    await page.emulateMediaType('screen');
    await page.pdf({
      path: path.join(directoryName, outputFilename),
      format: 'A4',
      printBackground: true,
    });
    await browser.close();
    console.log(`Successfully generated PDF: ${outputFilename}`);
    return true;
  } catch (e) {
    console.log(`Error generating ${outputFilename}: ${e}`);
    return false;
  }
}

// Load JSON data
const jsonData = require(`./${dataName}`);

// Prepare EJS template
const template = fs.readFileSync(templateName, 'utf-8');

// Generate PDFs for each entry
jsonData.forEach(async (entry, index) => {
  const renderedHtml = ejs.render(template, entry);

  const pdfFilename = `${templateName.replace('.ejs', '')}_${index + 1}_${entry.form_id || 'unknown'}.pdf`;

  await generatePDF(renderedHtml, pdfFilename);
});
