import mongoose from 'mongoose';
import { env } from './env.js';
import _ from 'lodash';
import { Video } from './models/video.js';
import { Entry } from './models/entry.js';
import ObjectsToCsv from 'objects-to-csv';

await mongoose.connect(`${env.MONGO_PROTOCOL}://${env.MONGO_USER}:${env.MONGO_PASSWORD}@${env.MONGO_HOST}/${env.MONGO_DB_NAME}?retryWrites=true&w=majority&appName=${env.APP_NAME}`);

//JSON.parse(readFileSync(`./features/${videoID}.json`, 'utf8'));

const res = [];

for await (const doc of Video.find({queued: {$exists: false}, features: {$exists: true}}).select('features').lean()) {
    const entry = await Entry.findOne({vid: doc._id, labels: { $exists: true }}).select('labels').lean();
    if (entry == null) continue;
    res.push({...doc.features, ..._.omit(entry.labels, 'set')});
}

const csv = new ObjectsToCsv(res);
await csv.toDisk('./output.csv');