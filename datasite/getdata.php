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
$dbname = "lyrics";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(array("error" => "Connection failed: " . $conn->connect_error)));
}

// List of tables to get the count of rows
$tables = array("lyrics", "album_songs", "artists", "albums", "urls_album", "urls_artist", "urls_song");

// Initialize an array to store the counts
$dataCounts = array();

// Loop through each table and get the row count
$totalCount = 0; // Initialize total count
foreach ($tables as $table) {
    $sql = "SELECT COUNT(*) as count FROM $table";
    $result = $conn->query($sql);

    if ($result) {
        $row = $result->fetch_assoc();
        $count = $row['count'];
        $dataCounts[$table] = $count;
        $totalCount += $count; // Add count to total count
    } else {
        $dataCounts[$table] = "Error: " . $conn->error;
    }
}

// Add total count to the data counts array
$dataCounts = array_merge(array("total" => $totalCount), $dataCounts);

// Close the connection
$conn->close();

// Return the data counts as JSON
echo json_encode($dataCounts);
?>