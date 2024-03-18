import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
import config
import librosa

st.title('Statistics')

# All species listed with progress
st.header('All species progress')
with st.expander('Expand'):
	c = st.container()
	cols = c.columns([3,3,1,3,1,3])
	cols[0].markdown('**Species**')
	cols[1].markdown('**IDs done**')
	cols[2].write('')
	cols[3].markdown('**Chunks done**')
	cols[4].write('')

	for s in config.all_species:
		c = st.container()
		cols = c.columns([3,3,1,3,1,3])
		# Display progress
		ids_done = st.session_state['labelled_ids'][s]
		ids_tot = st.session_state['total_ids'][s]
		chunks_done = st.session_state['labelled_chunks'][s]
		chunks_tot = st.session_state['total_chunks'][s]
		cols[0].write(s)
		cols[1].progress(ids_done / ids_tot if ids_tot !=0 else 1.0)
		cols[2].write('{} of {}'.format(ids_done, ids_tot))
		cols[3].progress(chunks_done / chunks_tot if chunks_tot !=0 else 1.0)
		cols[4].write('{} of {}'.format(chunks_done, chunks_tot))

# Show raw labels json
st.header('Labels')
with st.expander('Expand'):
	st.write(st.session_state['labels'])


# Produce some canonical examples
st.header('Canonical examples')
with st.expander('Expand'):
	for s in config.all_species:
		species_chunks = []
		st.subheader(s)
		for chunk in st.session_state['labels']:
			# If a perfect species match
			if s in st.session_state['labels'][chunk] and len(st.session_state['labels'][chunk]) == 1:
				species_chunks.append(chunk)

		# Choose 4 and plot
		species_chunks_samples = np.random.choice(species_chunks, 4)
		fig = plt.figure(figsize=(6,4))
		p = 1
		for chunk in species_chunks_samples:
			# Generate & display the mel spectrogram for the i'th chunk
			filepath = os.path.join(config.path, chunk)
			y, sr = librosa.load(filepath, sr=32000)
			ps = librosa.feature.melspectrogram(y=y, sr=sr)
			ps_db = librosa.power_to_db(ps, ref=np.max)
			ax = plt.subplot(2,2,p)
			librosa.display.specshow(ps_db, x_axis='time', y_axis='mel', sr=sr, ax=ax)
			ax.set_title(chunk)
			p += 1
		plt.tight_layout()
		st.pyplot(fig)
			