<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lyrics Display</title>
    <link rel="stylesheet" href="fullscreenlyrics.css">
</head>
<body>
    <?php
    if (isset($_GET['q'])) {
        $query = urlencode($_GET['q']);
        $url = "https://obunic.net/apps/lyrics/?q=" . $query;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        curl_close($ch);
        
        $lyricsData = json_decode($output, true);
        
        if (!empty($lyricsData)) {
            $firstEntry = $lyricsData[0];
            $artist = htmlspecialchars($firstEntry['artist']);
            $cover = htmlspecialchars($firstEntry['cover']);
            $lyrics = nl2br(htmlspecialchars($firstEntry['lyrics']));
            $title = htmlspecialchars($firstEntry['title']);
            ?>

            <div class="lyricsHeader">
                <div class="lyAheader">
                    <div class="lyAimg">
                        <img src="<?php echo $cover; ?>" alt="Cover image">
                    </div>
                    <div class="lyAinfo">
                        <span class="lyAtitle"><?php echo $title; ?></span><br>
                        <span class="lyAauthor">Song by <?php echo $artist; ?></span>
                    </div>
                </div>
            </div>
            <div class="lyricscontainer">
                <?php echo $lyrics; ?>
            </div>

            <?php
        } else {
            echo "<p>No lyrics found for the query.</p>";
        }
    } else {
        echo "<p>No query provided.</p>";
    }
    ?>
</body>
</html>