const puppeteer = require('puppeteer');
const mysql = require('mysql2/promise');
const fs = require('fs').promises;
const http = require('http');
const path = require('path');
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

(async () => {
    try {
        const dbconn = await mysql.createConnection({
            host: 'obunic.net',
            user: 'root',
            password: '!Stiefel(123)',
            database: 'geniuslyrics'
        });

        const browser0 = await puppeteer.launch({ headless: true });
        
        await Promise.all([
            openNewPages(browser0),
        ]);

        async function openNewPages(browser) {
            const p1 = await browser.newPage();
            const p2 = await browser.newPage();
            const p3 = await browser.newPage();
            const p4 = await browser.newPage();
            const p5 = await browser.newPage();
            const p6 = await browser.newPage();

            await Promise.all([
                initializeGenius(p1, dbconn),
                initializeGenius(p2, dbconn),
                initializeGenius(p3, dbconn),
                initializeGenius(p4, dbconn),
                initializeGenius(p5, dbconn),
                initializeGenius(p6, dbconn),
            ]);
        }
    } catch(error) {
        console.log(error);
    }
})();

async function initializeGenius(p, dbconn) {
    console.log("[+] Initializing crawler");
    setHeaders(p);
    albumCrawling(p, dbconn);
}

async function albumCrawling(p, dbconn) {
    try {
        const { album_url, album_id } = await getUrlToFetch(dbconn);
        console.log(new Date() + " scraping another album:", album_url);
        //const url = "https://genius.com/albums/Udo-jurgens/Griechischer-wein-seine-neuen-lieder";
        if (!album_url) {
            console.error('No Album found to fetch.' + album_url, album_id);
            return;
        }

        await p.goto(album_url);
        await delay(500);

        const songs_container = '/html/body/routable-page/ng-outlet/album-page/div[2]/div[1]/div';

        const song_urls = await p.evaluate((songs_container) => {
            let nodes = document.evaluate(songs_container, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            let urls = [];
            for (let i = 0; i < nodes.snapshotLength; i++) {
                let node = nodes.snapshotItem(i);
                let links = node.querySelectorAll('a');
                links.forEach(link => urls.push(link.href));
            }
            return urls;
        }, songs_container);

        console.log("Extracted URLs:", song_urls);

        for (const song_url of song_urls) {
            insertSongUrl(dbconn, song_url, album_id);
        }

        markAlbumAsFetched(dbconn, album_id)
        albumCrawling(p, dbconn);
    } catch (error) {
        console.error("Error during scraping:", error);
        albumCrawling(p, dbconn);
    }
}

async function markAlbumAsFetched(dbconn, album_id) {
    try {
        // First, try to mark the URL as visited in the priority_song_urls table
        let [rows, fields] = await dbconn.execute('UPDATE albums SET fetched = 1 WHERE album_id = ?', [album_id]);
        
        if (rows.affectedRows > 0) {
            console.log('Album id marked:', album_id);
            return true;
        }
    } catch (error) {
        console.error('Error marking URL as visited:', error);
        return false;
    }
}

async function getUrlToFetch(dbconn) {
    const query = `
        SELECT album_id, url
        FROM albums
        WHERE fetched=0
        ORDER BY RAND()
        LIMIT 1
    `;

    try {
        const result = await dbconn.query(query);
        
        if (Array.isArray(result) && result.length > 0 && Array.isArray(result[0]) && result[0].length > 0) {
            const album = result[0][0];
            return {
                album_url: album.url,
                album_id: album.album_id
            };
        } else {
            throw new Error("No unfetched albums found");
        }
    } catch (err) {
        console.error("Error fetching album from database:", err);
        throw err;
    }
}

async function insertSongUrl(dbconn, song_url, album_id) {
    try {
        const insertQuery = `
            INSERT INTO album_songs (song_url, album_id)
            VALUES (?, ?)
            ON DUPLICATE KEY UPDATE
                song_url = VALUES(song_url),
                album_id = VALUES(album_id);
        `;
        const values = [song_url, album_id];
        
        await dbconn.query(insertQuery, values);
        console.log('Album song URL inserted successfully');
    } catch (error) {
        console.error('Error inserting album song url:', error);
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