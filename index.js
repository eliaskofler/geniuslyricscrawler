const puppeteer = require('puppeteer');
const mysql = require('mysql2/promise');
const fs = require('fs');
const http = require('http');
const path = require('path');
const delay = (time) => new Promise(resolve => setTimeout(resolve, time));

