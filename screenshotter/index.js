const chromium = require("@sparticuz/chromium");
const puppeteer = require("puppeteer-core");
//const fetch = require('node-fetch');
const https = require('https');
const fs = require("fs");

const url = "http://"+process.env.NGINX_HOST+":"+process.env.NGINX_PORT;

(async () => {
    let browser = "";
    try {
        const executablePath = await chromium.executablePath();
        browser = await puppeteer.launch({
            args: [
                '--no-sandbox',
                '--use-gl=angle',
                '--use-angle=swiftshader',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
//                '--single-process',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-features=site-per-process'
            ],
            defaultViewport: chromium.defaultViewport,
            executablePath: executablePath,
            headless: "new",
            ignoreHTTPSErrors: true,
        });

        const page = await browser.newPage();
        console.log(`Goto ${url}`);
        let links = [];
        await page.goto(url, { timeout: 90000, waitUntil: 'networkidle2' });
        try {
            await page.screenshot({ path: '/dashpub/screenshots/index.jpg', type: 'jpeg', quality: 80, fullPage: true });
            links = await page.evaluate((baseUrl) => {
                return Array.from(document.querySelectorAll('a'))
                    .map(link => link.href)
                    .filter(href => href.startsWith(baseUrl));
            }, url);
        } catch (error) {
            console.error('Screenshot failed:', error);
        } finally {
              console.log("Done index screenshot");
              await page.close();
        }
        console.log(links);
        for (const link of links) {
            try {
                const href = link
                const dashboard = new URL(href, page.url()).pathname.slice(1);
                const dashboard_url = `${url}/${dashboard}`;
                console.log(`Processing: ${dashboard_url}`);
                const pageInstance = await browser.newPage();
                pageInstance.setDefaultNavigationTimeout(120000); // Set timeout to 120 seconds

                //pageInstance.on('console', msg => console.log('PAGE LOG:', msg.text()));
                pageInstance.on('response', async (response) => {
                    const headers = response.headers();
//                    console.log(`URL: ${response.url()}`);
//                    console.log('HTTP Headers:', headers);
                });
                await pageInstance.setViewport({ width: 1920, height: 1080 });
                await pageInstance.goto(dashboard_url, { timeout: 90000, waitUntil: 'domcontentloaded' });
                await pageInstance.waitForSelector(".url2png-cheese", { timeout: 100000 });
                await pageInstance.screenshot({ path: `/dashpub/screenshots/${dashboard}.jpg`, type: 'jpeg', quality: 80, fullPage: true });
                await pageInstance.close();
            } catch (error) {
                console.error(`Error processing ${link}:`, error);
            } finally {
              console.log(`Finished ${link}`);
            }
        }

        await browser.close();
    } catch (error) {
        console.error('Error during Puppeteer operation:', error);
        if (browser) await browser.close();
    }
})();
