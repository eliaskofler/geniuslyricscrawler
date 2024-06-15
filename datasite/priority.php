<?php
header('Content-Type: application/json');

// Enable error reporting
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Database configuration
$servername = "localhost";
$username = "admin";
$password = "!Stiefel(123)";
$dbname = "geniuslyrics";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if 'url' parameter is set in GET request
if (isset($_GET['url'])) {
    $url = $_GET['url'];

    // Prepare and bind
    $stmt = $conn->prepare("INSERT INTO priority_song_urls (url, visited, last_visited) VALUES (?, false, NULL) ON DUPLICATE KEY UPDATE url = url");
    $stmt->bind_param("s", $url);

    // Execute the statement
    if ($stmt->execute()) {
        $response = array("status" => "success", "message" => "Priority URL inserted successfully.");
    } else {
        $response = array("status" => "error", "message" => "Error inserting URL: " . $stmt->error);
    }

    // Close the statement
    $stmt->close();
} else {
    $response = array("status" => "error", "message" => "No URL parameter provided.");
}

// Close the connection
$conn->close();

// Output response as JSON
header('Content-Type: application/json');
echo json_encode($response);
?>