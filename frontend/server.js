var express= require('express');
const app = express();
var path = require('path')
const server = require('http').createServer(app);
var cors = require('cors')
const mongoose = require('mongoose');

const PORT = 3000;


<<<<<<< HEAD
<<<<<<< HEAD
const dbUrl = 'mongodb+srv://<user>:<password>@<cluster>.s0pds.mongodb.net/test';

=======
//const dbUrl = 'mongodb+srv://<user>:<password>@<cluster>.s0pds.mongodb.net/test';
const dbUrl = 'mongodb+srv://admin:valami_amit_megjegyzek123@feedbackcluster.s0pds.mongodb.net/test';
>>>>>>> b903390 (db connection)
=======
const dbUrl = 'mongodb+srv://<user>:<password>@<cluster>.s0pds.mongodb.net/test';
>>>>>>> be9e053 (maybe stuff)
mongoose.connect(dbUrl);

mongoose.connection.on('connected', () => {
    console.log('csatlakozva DB-hez');
})

mongoose.connection.on('error', (error) => {
    console.log('Hiba tortent', error);
})

var FeedbackModel = require('./feedback.model');

app.use(cors())
app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res, next) => {
    res.sendFile(__dirname + '/index.html');
}).post((req, res, next) => {
    if(req.body.user_id && req.body.description){
        var feedback = new FeedbackModel(req.body.user_id, req.body.description);
        feedback.save((err, doc) => {
            if (err) res.status(500).send("Adatbazis hiba");
            if (doc) res.status(200).send("Sikeres visszajelzes!");
        })
    }
});
server.listen(PORT);
<<<<<<< HEAD
console.log(`Server is running on port ${PORT}`);
=======
console.log(`Server is running on port ${PORT}`);
>>>>>>> b903390 (db connection)
