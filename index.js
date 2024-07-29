const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const mysql = require('mysql2/promise');
const fs = require('fs').promises;
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

(async () => {
    try {
        console.log("Connecting to database...")
        const dbconn = await mysql.createConnection({
            host: 'obunic.net',
            user: 'root',
            password: '!Stiefel(123)',
            database: 'geniuslyrics'
        });

        console.log("Connected to database!")

        console.log("Launching browser..")
        const browser0 = await puppeteer.launch({
            headless: false,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        });
        console.log("Browser launched!")
        
        console.log("Opening new tabs and setting up...")
        await Promise.all([
            openNewPages(browser0),
        ]);

        async function openNewPages(browser) {
            const p1 = await browser.newPage();
            const p2 = await browser.newPage();
            const p3 = await browser.newPage();
            const p4 = await browser.newPage();

            await Promise.all([
                initializeGenius(p1, dbconn),
                initializeGenius(p2, dbconn),
                initializeGenius(p3, dbconn),
                initializeGenius(p4, dbconn),
            ]);
        }
    } catch(error) {
        console.log(error);
    }
})();

async function initializeGenius(p, dbconn) {
    console.log("[+] Initialize Genius");
    setHeaders(p);
    lyricsCrawling(p, dbconn);
}

async function lyricsCrawling(p, dbconn) {
    try {
        console.log("[:] crawling.. " + new Date());
        console.log("[.] getting a url to fetch");
        const url = await getUrlToFetch(dbconn);
        console.log("[~] got a url to fetch: " + url);
        //const url = "https://genius.com/Udo-jurgens-jeder-lugt-so-wie-er-kann-lyrics"
        if (!url) {
            console.error('[!] No URL found to fetch.');
            return;
        }
        const blacklist = await fs.readFile('blacklist.txt', 'utf-8');
        const blacklistArray = blacklist.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        let responseStatus = null;
        p.on('response', response => {
            if (response.url() === url) {
                responseStatus = response.status();
            }
        });

        await p.goto(url, { waitUntil: 'domcontentloaded' });
        await delay(500);

        if (responseStatus === 404) {
            console.log("[~] No lyrics found on page. 404");
            await insertLyrics(url, "", "", "We can't provide any lyrics to this song.", "", "", "", dbconn);
            await wipeOutUrl(url, dbconn);
            return lyricsCrawling(p, dbconn);
        } else {
            console.log(responseStatus);
        }

        const nahBro = await p.evaluate(() => {
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
            console.log("[~] No lyrics found on page.")
            await insertLyrics(url, "", "", "We can't provide any lyrics to this song.", "", "", "", dbconn);
            await wipeOutUrl(url, dbconn);
            return lyricsCrawling(p, dbconn);
        }

        const lyrics = await p.evaluate(() => {
            const elements = document.querySelectorAll('div[data-lyrics-container="true"]');
            return Array.from(elements).map(element => {
                element.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
                return element.textContent;
            }).join('\n');
        });

        const author = await p.evaluate(() => {
            const element = document.evaluate('//*[@id="application"]/main/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/span/span/a', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            return element.singleNodeValue.textContent.trim();
        });

        const releaseDate = await p.evaluate(() => {
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
        
        const views = await p.evaluate(() => {
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

        const title = await p.evaluate(() => {
            const titelm = document.querySelector('h1').textContent;
            return titelm
        })

        const cover = await p.evaluate(() => {
            const element = document.evaluate('//*[@id="application"]/main/div[1]/div[2]/div[2]/div/img', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return element ? element.src : null;
        });

        //console.log('url: ', url);
        //console.log('views: ', views)
        //console.log('artist: ', author);
        //console.log('release date: ', releaseDate);
        //console.log('title: ', title);
        //console.log('Content:', lyrics);

        insertLyrics(url, title, author, lyrics, releaseDate, views, cover, dbconn);

        await p.waitForSelector('a');

        const hrefs = await p.evaluate(() => {
            const anchorElements = document.querySelectorAll('a');
            return Array.from(anchorElements).map(anchor => anchor.href);
        });

        const filteredHrefs = hrefs
            .filter(href => href.includes('https://genius.com'))
            .filter(href => !blacklistArray.includes(href));

        await batchInsertIntoDatabase(filteredHrefs, dbconn);

        await wipeOutUrl(url, dbconn);
        lyricsCrawling(p, dbconn);

    } catch(error) {
        console.log(error)
        lyricsCrawling(p, dbconn);
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

async function wipeOutUrl(url, dbconn) {
    try {
        [rows, fields] = await dbconn.execute('UPDATE album_songs SET visited = 1 WHERE song_url = ?', [url]);
        
        if (rows.affectedRows > 0) {
            console.log('[~] URL marked as visited in song_urls:', url);
            return true;
        } else {
            console.error('URL not found in either table:', url);
            return false;
        }
    } catch (error) {
        console.error('Error marking URL as visited:', error);
        return false;
    }
}

async function getUrlToFetch(dbconn) {
    try {
        const [rows, fields] = await dbconn.execute('SELECT song_url FROM album_songs WHERE visited=0 LIMIT 250');
        
        if (rows.length > 0) {
            // Select a random row from the fetched rows
            const randomIndex = Math.floor(Math.random() * rows.length);
            return rows[randomIndex].song_url;
        } else {
            console.error('No unvisited URLs found in the table.');
            return null;
        }
    } catch (error) {
        console.error('Error fetching URL from the database:', error);
        return null;
    }
}

async function batchInsertIntoDatabase(urls, dbconn) {
    try {
        // Start a transaction
        await dbconn.beginTransaction();

        for (const url of urls) {
            const urlType = await urlIdentifier(url);
            const query = `INSERT IGNORE INTO ${urlType} (url, visited) VALUES (?, ?)`;

            try {
                await dbconn.execute(query, [url, 0]);
            } catch (error) {
                console.error(`Error inserting ${url} into ${urlType}:`, error);
                // Optionally, you can rollback and rethrow the error
                await dbconn.rollback();
                throw error;
            }
        }

        // Commit the transaction if all inserts succeed
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