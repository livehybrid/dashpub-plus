const chromium = require('chrome-aws-lambda');
//const fetch = require('node-fetch');
const https = require('https');
const fs = require("fs");

var url = "http://"+process.env.NGINX_HOST+":"+process.env.NGINX_PORT;

(async () => {
    let browser = "";
    const executablePath = await chromium.executablePath
    browser = await chromium.puppeteer.launch({
        args: [      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--single-process'],
        defaultViewport: chromium.defaultViewport,
        executablePath: executablePath,
        headless: "new",
        ignoreHTTPSErrors: true,
    });

    // Use puppeteer to parse and extract all href links
    const page = await browser.newPage();
    await page.goto("http://"+process.env.NGINX_HOST+":"+process.env.NGINX_PORT, { timeout:90000, waitUntil: 'networkidle2'});
    await page.screenshot({path: '/dashpub/screenshots/index.jpg', type: 'jpeg', quality: 80, fullPage: true});
    const links = await page.$$('a');
    for (const link of links) {
        const href = await link.evaluate(el => el.href);
        const url = new URL(href);
        const dashboard = url.pathname.startsWith('/') ? url.pathname.slice(1) : url.pathname;
        try {
            const dashboard_url = "http://"+process.env.NGINX_HOST+":"+process.env.NGINX_PORT+"/"+dashboard;
            console.log(`Getting dashboard - ${dashboard_url}`);
            const page = await browser.newPage();
            page.on('console', msg => console.log('PAGE LOG:', msg.text()));
            await page.setViewport({ width: 810, height: 415 })
            await page.goto(dashboard_url, {
                timeout: 90000,
                waitUntil: 'networkidle2'
            });
            await page.waitForSelector(".url2png-cheese", {timeout: 100000});
            const body = page.$("body");
            console.log("Taking screenshot")
            await page.screenshot({path: '/dashpub/screenshots/' + dashboard + '.jpg', type: 'jpeg', quality: 80, fullPage: true});
            await page.close();
        } catch (error) {
            console.log(error);
        }
    };

    await browser.close();
})();
