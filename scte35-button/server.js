const axios = require('axios')
const express = require('express')
const cors = require('cors')
const serveStatic = require('serve-static')


// We use Express to serve just the static files
const app = express()
const port = 5001

app.use(cors());

app.use(serveStatic('./web', {
    setHeaders: setStaticCORS
}));

//We need to handle CORS differently for static files
function setStaticCORS(res, path) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
}

app.listen(port, () => {
    console.log(`Listening on port ${port}`)
})