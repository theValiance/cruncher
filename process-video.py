import sys
from yt_dlp import YoutubeDL
import numpy as np
import librosa
import json
import os

# Fetch YT Video
#####################################################
#get the video id from command line arg
vid = sys.argv[1]

#build video url
url = "https://www.youtube.com/watch?v={}".format(vid)

#video dl options
opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': './vids/{}'.format(vid)
}

#download the video
with YoutubeDL(opts) as ydl:
    ydl.download([url])

# Extract Features
#######################################################

# Load the audio file
print("Opening file...")
y, sr = librosa.load("./vids/{}.mp3".format(vid))

# Set the hop length; at 22050 Hz, 512 samples ~= 23ms
hop_length = 512

print("Computing features...")
# Separate harmonics and percussives into two waveforms
y_harmonic, y_percussive = librosa.effects.hpss(y)

#y_DB = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
y_harmonic_DB = librosa.amplitude_to_db(np.abs(librosa.stft(y_harmonic)), ref=np.max)

tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

y_percussive_DB = librosa.util.sync(librosa.amplitude_to_db(np.abs(librosa.stft(y_percussive)), ref=np.max), beats)

y_hp_DB_dif = librosa.util.sync(y_harmonic_DB, beats) - y_percussive_DB

y_beats = librosa.feature.tempo(y=y_percussive, sr=sr, aggregate=None)

# Compute chroma features from the harmonic signal
chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)

y_F0 = librosa.yin(y_harmonic, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
y_sf = librosa.feature.spectral_flatness(y=y)[0]

#plps = librosa.beat.plp(y=y_percussive, sr=sr, hop_length=hop_length)
#plps_delta = librosa.feature.delta(plps)

def dictToFloat(d):
    return dict(zip(d.keys(), [float(v) for v in d.values()]))

pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
chroma_mean = dictToFloat(dict(zip(["chroma_{}_mean".format(pitch) for pitch in pitches], np.mean(chromagram, axis=1))))
chroma_variance = dictToFloat(dict(zip(["chroma_{}_var".format(pitch) for pitch in pitches], np.var(chromagram, axis=1))))
chroma_min = dictToFloat(dict(zip(["chroma_{}_min".format(pitch) for pitch in pitches], np.min(chromagram, axis=1))))
chroma_max = dictToFloat(dict(zip(["chroma_{}_max".format(pitch) for pitch in pitches], np.max(chromagram, axis=1))))

features = {
    'db_harmonic_mean': float(np.mean(y_harmonic_DB)),
    'db_harmonic_var': float(np.var(y_harmonic_DB)),
    'db_harmonic_min': float(np.min(y_harmonic_DB)),
    'db_harmonic_max': float(np.max(y_harmonic_DB)),
    'db_percussive_mean': float(np.mean(y_percussive_DB)),
    'db_percussive_var': float(np.var(y_percussive_DB)),
    'db_percussive_min': float(np.min(y_percussive_DB)),
    'db_percussive_max': float(np.max(y_percussive_DB)),
    'db_dif_mean': float(np.mean(y_hp_DB_dif)),
    'db_dif_var': float(np.var(y_hp_DB_dif)),
    'db_dif_min': float(np.min(y_hp_DB_dif)),
    'db_dif_max': float(np.max(y_hp_DB_dif)),
    'tempo_mean': float(np.mean(y_beats)),
    'tempo_var': float(np.var(y_beats)),
    'tempo_min': float(np.min(y_beats)),
    'tempo_max': float(np.max(y_beats)),
    'f0_mean': float(np.mean(y_F0)),
    'f0_var': float(np.var(y_F0)),
    'f0_min': float(np.min(y_F0)),
    'f0_max': float(np.max(y_F0)),
    'sf_mean': float(np.mean(y_sf)),
    'sf_var': float(np.var(y_sf)),
    'sf_min': float(np.min(y_sf)),
    'sf_max': float(np.max(y_sf)),
    **chroma_mean,
    **chroma_variance,
    **chroma_min,
    **chroma_max
}

# Write Features to json
###############################################
print("Writing features to file...")
filePath = './features/{}.json'.format(vid)
os.makedirs(os.path.dirname(filePath), exist_ok=True)
with open(filePath, 'w') as file:
    json.dump(features, file)

# Cleanup video
###############################################
print("Cleaning up...")
os.unlink('./vids/{}.mp3'.format(vid))

print("Done :)")