import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
import config
import umap
import pandas as pd
import seaborn as sns
st.title('Visualisations')

# Load and munge the (xy) with the new labels
# Note the (xy) coords come from separate script operated on the vectors
# df = pd.read_json('frogid_v3_chunked_3.json')
# e = umap.UMAP(random_state=0).fit_transform(df.vector.tolist())
# df[['filename','x','y']].to_csv('frogid_v3_chunked_3_xy.txt', index=False, sep='\t')

#@st.cache() # don't cache, since we want to mutate it
def load_xy():
	dfxy = pd.read_csv('data/frogid_v3_chunked_3_xy.txt', sep='\t')
	return dfxy

dfxy = load_xy()
dfxy['label'] = dfxy.filename.map(st.session_state['labels'])
st.write('Original size:', len(dfxy))
#dfxy = dfxy[~dfxy.label.isnull()]
dfxy['label'] = dfxy.label.fillna('')
dfxy['labelstr'] = dfxy.label.map(lambda x: ','.join(x))

st.write('Munged size:', len(dfxy))
st.write(dfxy.head())

l = st.text_input('Wildcard', value='insect')
dfxy['ovr'] = dfxy.labelstr.str.lower().str.contains(l)

fig, ax = plt.subplots()
sns.scatterplot(data=dfxy, x='x', y='y', s=5, hue='ovr')
plt.title('wildcard: *{}*'.format(l))
#plt.xlim(-10,5)
#plt.ylim(0,15)
st.pyplot(fig)

