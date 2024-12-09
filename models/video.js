import mongoose from 'mongoose';
import z from 'zod';

export const videoSchema = new mongoose.Schema({
	//youtube video id
	_id: {
		type: String,
		set: z.string().regex(/^[A-Za-z0-9_-]{11}$/).parse,
	},
	//store the title here because we need it on front end and dont want to burn through YT API requests
	title: {
		type: String,
		required: true,
	},
	//whether the video is queued for processing or not
	queued: {
		type: Boolean,
		select: false,
	},
	//we can stick whatever we want in the feature obj
	features: {
		type: mongoose.Schema.Types.Mixed,
		select: false,
	},
}, {
	toJSON: {
		transform: (_doc, ret) => {
			ret.id = ret._id;
			delete ret._id;
		}
	},
	versionKey: false,
});

export const Video = mongoose.model('Video', videoSchema);