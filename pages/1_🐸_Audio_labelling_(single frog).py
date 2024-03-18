import streamlit as st
import librosa
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
import soundfile as sf
import os
import pandas as pd
import config
import json

path = 'data/3s/'

def get_id_from_filename(filename):
	return int(filename.split('-')[0])

def get_id_from_filepath(filepath):
	return int(filepath.split('/')[2].split('-')[0])

# CALLBACK - add labels (submit form, all chunks for a given id)
def add_label(keys):
	# Check there is at least one label
	proceed_labels = False
	labelled_chunks = []
	for k in keys:
		if st.session_state[k]:
			proceed_labels = True
			labelled_chunks.append(k)

	if proceed_labels:
		for chunk in labelled_chunks:
			st.session_state['labels'][chunk] = [l[2:] for l in st.session_state[chunk]] #clip the emoji

		# Save the new (full) labels
		with open('data/labels.json', 'w', encoding='utf-8') as f:
			json.dump(st.session_state['labels'], f, indent=4)

		# Update idx and ids
		st.session_state['ids'][st.session_state['current_species']].remove(st.session_state['current_id'])
		if st.session_state['current_idx'] > len(st.session_state['ids'][st.session_state['current_species']]):
			st.session_state['current_idx'] -= 1

		# Update current id if there are still some left
		if st.session_state['ids'][st.session_state['current_species']]:
			st.session_state['current_id'] = st.session_state['ids'][st.session_state['current_species']][st.session_state['current_idx']]

		# Update counts
		st.session_state['labelled_ids'][st.session_state['current_species']] += 1
		st.session_state['labelled_chunks'][st.session_state['current_species']] += len(labelled_chunks)

		# Clear/remove chunk multiselect key info from state
		for k in keys:
			del st.session_state[k]
		st.session_state['global_entities'] = []

	# If no changes
	else:
		if st.session_state['current_idx'] < len(st.session_state['ids'][st.session_state['current_species']]) - 1:
			st.session_state['current_idx'] += 1
		else:
			st.session_state['current_idx'] = 0		
		st.session_state['current_id'] = st.session_state['ids'][st.session_state['current_species']][st.session_state['current_idx']]

# CALLBACK - change species
def set_species():
    if st.session_state['ids'][st.session_state['current_species']]:
    	st.session_state['current_id'] = st.session_state['ids'][st.session_state['current_species']][0]
    	st.session_state['current_idx'] = 0

# Sidebar stuff
st.sidebar.title('Audio labelling (single frog)')
st.sidebar.selectbox('Select a species', config.all_species, on_change=set_species, key='current_species')


# Main stuff
st.title('Audio labelling (single frog)')
st.info('Here we will verify the presence of frogs in chunks of audio. To begin with we tackle the simple case of single frogs. It is important to also tag whether or not there are insects, birds or humans present. Empty recordings also need to be explicitly labelled.')

# If there are any more to do
if st.session_state['ids'][st.session_state['current_species']]:
	# Selector for global options
	audio_entities = ['🐸 {}'.format(st.session_state['current_species'])] + config.label_options
	st.multiselect('Preload these into every chunk (useful for insects or constant croaking)', audio_entities, key='global_entities')

	# Display
	with st.form(key='labelling'):
		current_chunks = [f for f in st.session_state['chunks'][st.session_state['current_species']] if str(st.session_state['current_id']) in f]
		#current_chunks = current_chunks[0:3]
		#st.write(str(st.session_state['ids'][st.session_state['current_species']])) # Show full list we'll cycle through
		st.success('Current ID: {} ({} chunks)'.format(st.session_state['current_id'], len(current_chunks)))

		# Grid
		N_COLS = 4
		N_ROWS = int(np.ceil(len(current_chunks) / N_COLS))
		i = 0
		keys = []
		for r in range(N_ROWS):
			cols = st.columns(N_COLS)
			cols2 = st.columns(N_COLS*3)
			for c in range(N_COLS):
				if i < len(current_chunks):
					# Load audio
					filepath = os.path.join(path, current_chunks[i])
					y, sr = librosa.load(filepath, sr=32000)

					# Generate & display the mel spectrogram for the i'th chunk
					ps = librosa.feature.melspectrogram(y=y, sr=sr)
					ps_db = librosa.power_to_db(ps, ref=np.max)
					fig, ax = plt.subplots()
					librosa.display.specshow(ps_db, x_axis='time', y_axis='mel', sr=sr, ax=ax)
					ax.set_title(current_chunks[i])
					cols[c].pyplot(fig)

					# Display audio
					cols[c].audio(filepath, format='audio/wav')

					# The label options
					cols[c].multiselect('What is present?', audio_entities, st.session_state['global_entities'], key=current_chunks[i])

					# Increment
					i += 1

		# Submit all the info via callback
		st.form_submit_button('Next', on_click=add_label, args=(current_chunks,))

else:
	st.success('All done for **{}** single frog recordings'.format(st.session_state['current_species']))

# Display progress
ids_done = st.session_state['labelled_ids'][st.session_state['current_species']]
ids_tot = st.session_state['total_ids'][st.session_state['current_species']]
chunks_done = st.session_state['labelled_chunks'][st.session_state['current_species']]
chunks_tot = st.session_state['total_chunks'][st.session_state['current_species']]

st.sidebar.write('Completed IDs: {} of {}'.format(ids_done, ids_tot))
progress_ids = st.sidebar.progress(ids_done / ids_tot if ids_tot != 0 else 1.0)

st.sidebar.write('Completed chunks: {} of {}'.format(chunks_done, chunks_tot))
progress_ids = st.sidebar.progress(chunks_done / chunks_tot if chunks_tot != 0 else 1.0)

# Display labels (debugging)
#st.sidebar.write(st.session_state['labels'])