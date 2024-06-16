<?php
header('Content-Type: application/json');

// Enable error reporting
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Database connection details
$servername = "localhost";
$username = "admin";
$password = "!Stiefel(123)";
$dbname = "geniuslyrics";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(array("error" => "Connection failed: " . $conn->connect_error)));
}

// Initialize variables for counting albums_fetched
$albums_fetched_0 = 0;
$albums_fetched_1 = 0;

// Counting albums_fetched for artists
$sql = "SELECT albums_fetched, COUNT(*) AS count FROM artists GROUP BY albums_fetched";
$result = $conn->query($sql);

if ($result) {
    while ($row = $result->fetch_assoc()) {
        if ($row['albums_fetched'] == 0) {
            $albums_fetched_0 = $row['count'];
        } elseif ($row['albums_fetched'] == 1) {
            $albums_fetched_1 = $row['count'];
        }
    }
} else {
    die(json_encode(array("error" => "Error fetching albums_fetched counts: " . $conn->error)));
}

// Initialize an array to store the counts
$dataCounts = array();

// Calculate done_percentage
$done_percentage = ($albums_fetched_1 / ($albums_fetched_0 + $albums_fetched_1)) * 100;
$done_percentage = round($done_percentage) . "%";

// Add total count and additional counts to the data counts array
$dataCounts = array_merge(array("albums_fetched_0" => $albums_fetched_0, "albums_fetched_1" => $albums_fetched_1, "done_percentage" => $done_percentage), $dataCounts);

// Close the connection
$conn->close();

// Return the data counts as JSON
echo json_encode($dataCounts);
?>