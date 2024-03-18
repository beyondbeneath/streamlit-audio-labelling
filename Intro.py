import streamlit as st
import os
import pandas as pd
import config
import glob
import json

# Main intro page
st.set_page_config(
    page_title='FrogID',
    page_icon='🐸',
    layout='wide'
)

# Filter a df into single species
def load_species(df, species):
    # Returns one df with examples of species solo, and another with examples with other frogs
    dfs = df[df.validated_frog_names.fillna('').str.contains(species)]
    dfs1 = dfs[~dfs.validated_frog_names.str.contains(',')]
    dfs2 = dfs[dfs.validated_frog_names.str.contains(',')]
    return dfs1, dfs2

# Resolve id from filepath
def get_id_from_filepath(filepath):
    return int(filepath.split('/')[2].split('-')[0])

st.cache()
def load_data():
    # Loads the datafile (id, labels) and the file chunk list
    df = pd.read_csv('data/syd-frogs.txt', sep='\t')
    audio_chunks_all = sorted(glob.glob(config.path + '*.wav'))

    # Get stats
    stats = {'ids':{}, 'chunks':{}, 'total_ids':{}, 'total_chunks':{}}
    for s in config.all_species:
        dfs1, dfs2 = load_species(df, s)
        stats['ids'][s] = dfs1.id.tolist()
        stats['chunks'][s] = sorted([os.path.basename(f) for f in audio_chunks_all if get_id_from_filepath(f) in stats['ids'][s]])
        stats['total_ids'][s] = len(stats['ids'][s])
        stats['total_chunks'][s] = len(stats['chunks'][s])    
    
    return df, audio_chunks_all, stats


# Load the stuff
df, audio_chunks_all, stats = load_data()

# Setup state
if 'id' not in st.session_state:
    st.session_state['audio_chunks_all'] = audio_chunks_all
    st.session_state['ids'] = {}
    st.session_state['chunks'] = {}
    st.session_state['total_ids'] = {}
    st.session_state['total_chunks'] = {}
    st.session_state['labelled_ids'] = {}
    st.session_state['labelled_chunks'] = {}

    for s in config.all_species:
        st.session_state['ids'][s] = stats['ids'][s]
        st.session_state['chunks'][s] = stats['chunks'][s]
        st.session_state['total_ids'][s] = stats['total_ids'][s] = len(st.session_state['ids'][s])
        st.session_state['total_chunks'][s] = stats['total_chunks'][s] = len(st.session_state['chunks'][s])
        st.session_state['labelled_ids'][s] = 0
        st.session_state['labelled_chunks'][s] = 0

    # Labels
    if os.path.exists('data/labels.json'):
        st.session_state['labels'] = json.loads(open('data/labels.json', 'r').read())
        loaded_ids = [int(chunk.split('-')[0]) for chunk in st.session_state['labels']]
        loaded_ids_unique = set(loaded_ids)
        for s in config.all_species:
            for id in loaded_ids_unique:
                if id in st.session_state['ids'][s]:
                    st.session_state['labelled_ids'][s] += 1
                    st.session_state['labelled_chunks'][s] += loaded_ids.count(id)
                    st.session_state['ids'][s].remove(id)

    elif 'labels' not in st.session_state:
        # Placeholders
        st.session_state['labels'] = {}
    
     # Defaults
    st.session_state['current_species'] = config.all_species[0]
    st.session_state['current_id'] = st.session_state['ids'][st.session_state['current_species']][0]
    st.session_state['current_idx'] = 0

st.title('FrogID')