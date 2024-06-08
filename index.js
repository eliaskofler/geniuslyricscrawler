const puppeteer = require('puppeteer');
const mysql = require('mysql2/promise');
const fs = require('fs');
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