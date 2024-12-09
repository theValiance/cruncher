import { z } from 'zod';

//build env parser
const envSchema = z.object({
	//mongo config
	MONGO_PROTOCOL: z.enum(['mongodb', 'mongodb+srv']).default('mongodb'),
	MONGO_HOST: z.string(),
	MONGO_DB_NAME: z.string().transform((val) => encodeURIComponent(val)),
	MONGO_USER: z.string().transform((val) => encodeURIComponent(val)),
	MONGO_PASSWORD: z.string().min(8).transform((val) => encodeURIComponent(val)),
}).readonly();

//parse env
export const env = envSchema.parse(process.env);