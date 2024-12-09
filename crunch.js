//import libs
import mongoose from 'mongoose';
import { spawn } from 'child_process';
import { readFileSync } from "node:fs";
//import parsed envs
import { env } from './env.js';
//import models
import { Video } from './models/video.js';
import { Entry } from './models/entry.js';

//connect to mongoDB
await mongoose.connect(`${env.MONGO_PROTOCOL}://${env.MONGO_USER}:${env.MONGO_PASSWORD}@${env.MONGO_HOST}/${env.MONGO_DB_NAME}?retryWrites=true&w=majority&appName=${env.APP_NAME}`);

const max_processes = 6;
const processes = [];
const ignore = [];

async function attemptSpawnProcess() {
	if (processes.length >= max_processes) return;
	const vid = await Video.findOne({queued: true, _id: {'$nin': [...processes, ...ignore]}});
	if (vid != null) {
		spawnProcess(vid._id);
		attemptSpawnProcess();
	} else {
		console.log('No videos to process! Retrying in 60 seconds.');
		setTimeout(attemptSpawnProcess, 60000);
	}
}

function spawnProcess(videoID) {
	console.log(`Processing video ${videoID}`);
	processes.push(videoID);
	const process = spawn('python', ["./process-video.py", videoID]);

	process.on('close', async (code) => {
		if (code == 0) {
			await Video.updateOne({_id: videoID}, {$unset: { queued: 1 }, features: JSON.parse(readFileSync(`./features/${videoID}.json`, 'utf8'))});
			console.log(`Finished processing video ${videoID}`);
		}
		else {
			console.log(`Error processing video ${videoID}, ignoring...`);
			ignore.push(videoID);
		}
		processes.splice(processes.findIndex(v => v == videoID), 1);
		attemptSpawnProcess();
	});
}

console.log('Starting...');
attemptSpawnProcess();