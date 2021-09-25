var express= require('express');
const app = express();
var path = require('path')
const server = require('http').createServer(app);
var cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');

const PORT = 3000;


const dbUrl = 'mongodb+srv://admin:a_new_password_icanremember123@feedbackcluster.s0pds.mongodb.net/test';

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


app.use(cors());
app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res, next) => {
    res.sendFile(__dirname + '/index.html');
})

app.post('/', (req, res, next) => {
    console.log(req);
    if(req.body.user_id && req.body.description){
        const feedback = new FeedbackModel({user_id: req.body.user_id, description: req.body.description});
        feedback.save((err, doc) => {
            if (err) res.status(500).send("Adatbazis hiba");
            if (doc) res.status(200).send("Sikeres visszajelzes!");
        })
    }
});
server.listen(PORT);
console.log(`Server is running on port ${PORT}`);