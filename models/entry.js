import mongoose from 'mongoose';
import z from 'zod';

const labelSetOptions = {
	discriminatorKey: 'set',
	_id: false,
};

const labelSetSchema = new mongoose.Schema({
	set: {
		type: String,
		required: true,
		enum: ['A'],
	}
}, labelSetOptions);

export const entrySchema = new mongoose.Schema({
	//youtube video id, also acts as a ref to Video model
	vid: {
		type: String,
		required: true,
		set: z.string().regex(/^[A-Za-z0-9_-]{11}$/).parse,
	},
	//ip address of the submitter
	ip: {
		type: String,
		required: true,
		set: z.string().ip().parse,
		select: false,
	},
	//timestamp of submission
	timestamp: {
		type: Date,
		default: Date.now,
		required: true,
	},
	//name of the submitter, to lowercase
	name: {
		type: String,
		required: true,
		set: v => _.capitalize(_.trim(v)),
	},
	//labels for this entry. can support different sets of labels using discriminants
	labels: {
		type: labelSetSchema,
		required: true,
	}
}, {
	versionKey: false,
	toJSON: {
		virtuals: true,
		transform: (_doc, ret) => {
			delete ret._id;
		}
	},
	id: false,
});

entrySchema.virtual('video', {
	ref: 'Video',
	localField: 'vid',
	foreignField: '_id',
	justOne: true,
});

//to reduce code duplication we define the mongoose type here...
const labelEntry = {
	type: Number,
	required: true,
	min: 0,
	max: 1,
};

//one set of labels, set 'A'
entrySchema.path('labels').discriminator('A', new mongoose.Schema({
	energy: labelEntry,
	sharpness: labelEntry,
	mood: labelEntry,
	color: labelEntry,
}, labelSetOptions));

//export model access
export const Entry = mongoose.model("Entry", entrySchema);