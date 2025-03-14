const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const mysql = require('mysql2/promise');
const fs = require('fs').promises;
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

(async () => {
    try {
        console.log("Connecting to database...");
        const dbconn = await mysql.createConnection({
            host: 'obunic.net',
            user: 'root',
            password: '!Stiefel(123)',
            database: 'geniuslyrics'
        });

        console.log("Connected to database!");

        console.log("Launching browser...");
        const browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        });
        console.log("Browser launched!");

        await openNewPages(browser, dbconn);
    } catch (error) {
        console.log(error);
    }
})();

async function openNewPages(browser, dbconn) {
    while (true) {
        const page = await browser.newPage();
        await initializeGenius(page, dbconn);
        await page.close();
    }
}

async function initializeGenius(page, dbconn) {
    console.log("[+] Initialize Genius");

    // Enable request interception
    await page.setRequestInterception(true);

    page.on('request', request => {
        if (request.resourceType() === 'script') {
            request.abort();
        } else {
            request.continue();
        }
    });

    await setHeaders(page);
    while (true) {
        await lyricsCrawling(page, dbconn);
    }
}

async function lyricsCrawling(page, dbconn) {
    try {
        console.log("[:] crawling.. " + new Date());
        console.log("[.] getting a url to fetch");
        const url = await getUrlToFetch(dbconn);
        console.log("[~] got a url to fetch: " + url);
        if (!url) {
            console.error('[!] No URL found to fetch.');
            return;
        }

        const blacklist = await fs.readFile('blacklist.txt', 'utf-8');
        const blacklistArray = blacklist.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        let responseStatus = null;
        page.on('response', response => {
            if (response.url() === url) {
                responseStatus = response.status();
            }
        });

        await page.goto(url);
        await delay(500);

        if (responseStatus === 404) {
            console.log("[~] No lyrics found on page. 404");
            await insertLyrics(url, "", "", "We can't provide any lyrics to this song.", "", "", "", dbconn);
            await wipeOutUrl(url, dbconn);
            return;
        } else {
            console.log(responseStatus);
        }

        const nahBro = await page.evaluate(() => {
            const element = document.evaluate('//*[@id="lyrics-root"]/div[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (element.textContent === "Lyrics for this song have yet to be released. Please check back once the song has been released.") {
                return true;
            } else if (element.textContent === "This song is an instrumental") {
                return true;
            } else {
                return false;
            }
        });

        if (nahBro) {
            console.log("[~] No lyrics found on page.");
            await insertLyrics(url, "", "", "We can't provide any lyrics to this song.", "", "", "", dbconn);
            await wipeOutUrl(url, dbconn);
            return;
        }

        const lyrics = await page.evaluate(() => {
            const elements = document.querySelectorAll('div[data-lyrics-container="true"]');
            return Array.from(elements).map(element => {
                element.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
                return element.textContent;
            }).join('\n');
        });

        const author = await page.evaluate(() => {
            const element = document.evaluate('//*[@id="application"]/main/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/span/span/a', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            return element.singleNodeValue.textContent.trim();
        });

        const releaseDate = await page.evaluate(() => {
            try {
                const element = document.evaluate('//*[@id="application"]/main/div[1]/div[3]/div[1]/div[2]/div/span[1]/span', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                if (element && element.singleNodeValue) {
                    if (element.singleNodeValue.textContent.trim().includes("viewer")) {
                        return "No release date given.";
                    } else if (element.singleNodeValue.textContent.trim().includes("view")) {
                        return "No release date given.";
                    }
                    return element.singleNodeValue.textContent.trim();
                } else {
                    return "No release date given.";
                }
            } catch (error) {
                console.error("Error:", error);
                return "Error occurred while retrieving release date";
            }
        });

        const views = await page.evaluate(() => {
            try {
                const element = document.evaluate('//*[@id="application"]/main/div[1]/div[3]/div[1]/div[2]/div/span[3]/span', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                if (element && element.singleNodeValue) {
                    return element.singleNodeValue.textContent.trim();
                } else {
                    return "No views given.";
                }
            } catch (error) {
                console.error("Error:", error);
                return "Error occurred while retrieving views";
            }
        });

        const title = await page.evaluate(() => {
            const titelm = document.querySelector('h1').textContent;
            return titelm;
        });

        const cover = await page.evaluate(() => {
            const metaTag = document.querySelector('meta[property="og:image"]');
            return metaTag ? metaTag.getAttribute('content') : null;
        });

        insertLyrics(url, title, author, lyrics, releaseDate, views, cover, dbconn);

        await page.waitForSelector('a');

        const hrefs = await page.evaluate(() => {
            const anchorElements = document.querySelectorAll('a');
            return Array.from(anchorElements).map(anchor => anchor.href);
        });

        const filteredHrefs = hrefs
            .filter(href => href.includes('https://genius.com'))
            .filter(href => !blacklistArray.includes(href));

        //await batchInsertIntoDatabase(filteredHrefs, dbconn);

        await wipeOutUrl(url, dbconn);
    } catch (error) {
        console.log(error);
    }
}

async function insertLyrics(url, title, artist, lyrics, release_date, views, cover, dbconn) {
    try {
        const insertQuery = `
            INSERT INTO lyrics (url, title, artist, lyrics, release_date, views, cover)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                artist = VALUES(artist),
                release_date = VALUES(release_date),
                cover = VALUES(cover)
        `;
        const values = [url, title, artist, lyrics, release_date, views, cover];

        await dbconn.query(insertQuery, values);

        console.log('[+] Lyrics inserted successfully');
    } catch (error) {
        console.error('[!] Error inserting lyrics:', error);
    }
}

async function wipeOutUrl(url, db) {
    try {
        filePath = "songs.txt"
        let fileData = await fs.readFile(filePath, 'utf-8');
        let lines = fileData.split('\n');
        let originalLength = lines.length;

        // Filter out the line with the matching URL
        lines = lines.filter(line => {
            let [songUrl] = line.split(',');
            return songUrl !== url;
        });

        if (lines.length < originalLength) {
            await fs.writeFile(filePath, lines.join('\n'), 'utf-8');
            console.log('[~] URL deleted from songs.txt:', url);
            return true;
        } else {
            console.error('URL not found in songs.txt:', url);
            return false;
        }
    } catch (error) {
        console.error('Error deleting URL from songs.txt:', error);
        return false;
    }
}

async function getUrlToFetch(db) {
    try {
        filePath = "songs.txt"
        let fileData = await fs.readFile(filePath, 'utf-8');
        let lines = fileData.split('\n').filter(line => line.trim() !== ''); // Filter out any empty lines
        
        if (lines.length > 0) {
            const randomIndex = Math.floor(Math.random() * lines.length);
            let [songUrl] = lines[randomIndex].split(',');
            console.log(songUrl);
            return songUrl;
        } else {
            console.error('No URLs found in songs.txt.');
            return null;
        }
    } catch (error) {
        console.error('Error fetching URL from songs.txt:', error);
        return null;
    }
}

async function batchInsertIntoDatabase(urls, dbconn) {
    try {
        await dbconn.beginTransaction();

        for (const url of urls) {
            const urlType = await urlIdentifier(url);
            const query = `INSERT IGNORE INTO ${urlType} (url, visited) VALUES (?, ?)`;

            try {
                await dbconn.execute(query, [url, 0]);
            } catch (error) {
                console.error(`Error inserting ${url} into ${urlType}:`, error);
                await dbconn.rollback();
                throw error;
            }
        }

        await dbconn.commit();
        console.log('[+] All data inserted successfully');
    } catch (error) {
        console.error('Transaction failed:', error);
    }
}

async function urlIdentifier(url) {
    if (url.includes("/tags/")) {
        return "tag_urls";
    } else if (url.includes("https://genius.com/Genius-")) {
        return "translation_urls";
    } else if (url.endsWith("-lyrics")) {
        return "song_urls";
    } else if (url.includes("/artists/")) {
        return "artist_urls";
    } else if (url.includes("/albums/")) {
        return "album_urls";
    } else {
        return "crap_urls";
    }
}

async function setHeaders(page) {
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en'
    });

    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

    await page.setViewport({
        width: 1920,
        height: 1080
    });

    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, "language", {
            get: function() {
                return "en-US";
            }
        });
        Object.defineProperty(navigator, "languages", {
            get: function() {
                return ["en-US", "en"];
            }
        });
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });
    });
}
