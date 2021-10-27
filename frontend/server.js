var express= require('express');
const app = express();
var path = require('path')
const server = require('http').createServer(app);
var cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const fs = require('fs');

const PORT = 3000;

let rawdata = fs.readFileSync('node_credentials.json');
const credentials = JSON.parse(rawdata);
const dbUrl = `mongodb+srv://${credentials.user}:${credentials.password}@${credentials.cluster}.s0pds.mongodb.net/test`;

mongoose.connect(dbUrl);

mongoose.connection.on('connected', () => {
    console.log('csatlakozva DB-hez');
})

mongoose.connection.on('error', (error) => {
    console.log('Hiba tortent', error);
})

require('./feedback.model');
const FeedbackModel = mongoose.model('feedback');

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json({}));
app.use(cors())
app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res, next) => {
    res.sendFile(__dirname + '/index.html');
}).post('/', (req, res, next) => {
    console.log(req.body)
    if(req.body.user_id && req.body.description){
        var feedback = new FeedbackModel({
            user_id: req.body.user_id,
            description: req.body.description
        });
        feedback.save((err, doc) => {
            if (err) res.status(500).send("Adatbazis hiba");
            if (doc) res.status(200).send("Sikeres visszajelzes!");
        })
    }
});
server.listen(PORT);
console.log(`Server is running on port ${PORT}`);
