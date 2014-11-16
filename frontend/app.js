var express = require('express');
var app = express();
var router = express.Router();

var wwwroot = './prod/hoocal/';


// app.use('/media', express.static(__dirname + '/media'));
app.use(express.static(wwwroot));

console.log('Listening on localhost:8080');
app.listen(8080);