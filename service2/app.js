const express = require('express');
const os = require('os');
const { exec } = require('child_process');

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    exec('ps ax', (err, stdout) => {
        if (err) {
            return res.status(500).send(err);
        }
        const ipAddress = Object.values(os.networkInterfaces()).flat().find(i => i.family === 'IPv4').address;
        exec('df -h', (err, df) => {
            if (err) {
                return res.status(500).send(err);
            }
            const uptime = os.uptime();

            res.json({
                "Service": "Service2",
                "IP Address": ipAddress,
                "Running Processes": stdout.split('\n').filter(Boolean),
                "Available Disk Space": df,
                "Uptime (seconds)": uptime
            });
        });
    });
});


app.post('/stop', (req, res) => {
    exec('docker ps -q | xargs -I {} docker stop {}', (err, stdout, stderr) => {
        if (err) {
            console.error("Error stopping containers:", stderr);
            return res.status(500).send("Error stopping containers.");
        }
        res.send(stdout || "All containers stopped successfully.");
    });
});

app.listen(port, () => {
    console.log(`Service2 listening at http://localhost:${port}`);
});
