const puppeteer = require('puppeteer');
const mysql = require('mysql2/promise');
const fs = require('fs').promises;
const http = require('http');
const path = require('path');
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

(async () => {
    try {
        const dbconn = await mysql.createConnection({
            host: 'localhost',
            user: '',
            password: '',
            database: 'geniuslyrics'
        });
        
        const browser = await puppeteer.launch({ headless: false });
        
        await Promise.all([
            openNewPages(browser)
        ]);

        async function openNewPages(browser) {
            const p1 = await browser.newPage();

            await Promise.all([
                initializeGenius(p1, dbconn)
            ])
        }
    } catch(error) {
        console.log(error);
    }
})();

async function initializeGenius(p, dbconn) {
    console.log("[+] Initializing crawler");
    setHeaders(p);
    lyricsCrawling(p, dbconn);
}

async function lyricsCrawling(p, dbconn) {
    try {
        console.log("crawling..");
        const url = "https://genius.com/Udo-jurgens-griechischer-wein-lyrics";
        const blacklist = await fs.readFile('blacklist.txt', 'utf-8');
        const blacklistArray = blacklist.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        await p.goto(url);
        await delay(1000);

        const captchaDetected = await p.evaluate(() => {
            return !!document.getElementById('pow-captcha-content');
        });
    
        if (captchaDetected) {
            console.log('CAPTCHA detected, sending HTTP GET request to 127.0.0.1:4321');
            
            http.get('http://127.0.0.1:4321', (res) => {
                console.log(`Got response: ${res.statusCode}`);
            }).on('error', (e) => {
                console.error(`Got error: ${e.message}`);
            });
    
            console.log('Waiting for 1 minute due to CAPTCHA.');
            await delay(30000);
            crawlData(p, connection);
            return;
        }


        // Wait for the elements with the specified attribute to be loaded
        await p.waitForSelector('div[data-lyrics-container="true"]');

        // Extract the content of all matching elements and join them into a single string
        const content = await p.evaluate(() => {
            const elements = document.querySelectorAll('div[data-lyrics-container="true"]');
            return Array.from(elements).map(element => {
            // Replace <br> with newline characters
            element.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
            return element.textContent;
            }).join('\n');
        });

        console.log('Content:', content);


        await p.waitForSelector('a');

        // Extract all href attributes from anchor tags
        const hrefs = await p.evaluate(() => {
            const anchorElements = document.querySelectorAll('a');
            return Array.from(anchorElements).map(anchor => anchor.href);
        });

        // Filter out the hrefs that are in the blacklist
        const filteredHrefs = hrefs
            .filter(href => href.includes('genius.com'))
            .filter(href => !blacklistArray.includes(href));

        console.log('Filtered Hrefs:', filteredHrefs);

    } catch(error) {
        console.log(error);
    }
}

async function setHeaders(p) {
    await p.setExtraHTTPHeaders({
        'Accept-Language': 'en'
    });

    await p.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, "language", {
            get: function() {
                return "en-US";
            }
        });
        Object.defineProperty(navigator, "language", {
            get: function() {
                return ["en-US", "en"];
            }
        });
    });
}