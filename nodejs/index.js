var express= require('express');
const app = express();
var path = require('path')
const server = require('http').createServer(app);
var cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const fs = require('fs');
const axios = require('axios');

const PORT = 3000;

let rawdata = fs.readFileSync('node_credentials.json');
const credentials = JSON.parse(rawdata);
const dbUrl = `mongodb+srv://${credentials.user}:${credentials.password}@${credentials.cluster}.s0pds.mongodb.net/test`;

mongoose.connect(dbUrl, {useNewUrlParser: true});
mongoose.connection.on('connected', () => {
    console.log('csatlakozva DB-hez');
});
mongoose.connection.on('error', (error) => {
    console.log('Hiba tortent', error);
});

app.use(cors())
app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res, next) => {
    res.sendFile(__dirname + '/index.html');
})

app.use('/', require('./routes'));

server.listen(PORT);
console.log(`Server is running on port ${PORT}`);
