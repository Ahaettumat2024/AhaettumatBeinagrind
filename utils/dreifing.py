import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def getEarlyFarmedDistribution(stofnstaerdir, farmNo):
    # Reiknar hlutfall snemmbúinna stokulaxa sem fer í hverja á 
    farmPosition = st.session_state['eldi'].loc[farmNo,'staðsetning']
    distances = st.session_state['rivers']['fjarlægð'].to_numpy()
    adjustedDistances = distances - farmPosition

    adjustedDistances = np.append(adjustedDistances,0)
    stofnstaerdir = np.append(stofnstaerdir.to_numpy(),100)

    distribution = stofnstaerdir/(np.absolute(adjustedDistances)+10)
    distribution = distribution/np.sum(distribution)
    distribution = distribution[:-1]
    return distribution

@st.cache_data
def getLateFarmedDistribution(stofnstaerdir, farmNo):
    # Reiknar hlutfall síbúinna stokulaxa sem fer í hverja á 
    farmPosition = st.session_state['eldi'].loc[farmNo,'staðsetning']
    distances = st.session_state['rivers']['fjarlægð'].to_numpy()
    adjustedDistances = distances - farmPosition
    distribution = stofnstaerdir/(np.absolute(adjustedDistances)+10)
    distribution = distribution/np.sum(distribution)
    return distribution

@st.cache_data
def getResults(stofnstaerdir, farmEarlyReturns, farmLateReturns, ITERS):
    # Reiknar niðurstöður
    stofn = stofnstaerdir.copy()
    stofn.drop('Heild', axis=1, inplace=True)
    results = stofn.copy()
    for i in farmEarlyReturns.index:
        print(i)
        for j in farmEarlyReturns.columns:
            if farmEarlyReturns.loc[i,j] > 0:
                results.loc[i] += farmEarlyReturns.loc[i,j]*getEarlyFarmedDistribution(results.loc[i],j)
            if farmLateReturns.loc[i,j] > 0:
                results.loc[i] += farmLateReturns.loc[i,j]*getLateFarmedDistribution(results.loc[i],j)
        results.loc[i,:] = 100*(results.loc[i,:].to_numpy()-stofn.loc[i,:].to_numpy())/results.loc[i,:].to_numpy()
    return results

## Oþarfi að breyta
def plotDistribution(ax, type, farm):
    # Plottar dreyfingu
    farmDict = pd.Series(st.session_state['eldi'].index, index=st.session_state['eldi']['Nafn'].values).to_dict()
    farmNo = farmDict[farm]
    stofnstaerdir = st.session_state['rivers']['Meðalfjöldi']
    if type == 'Snemmbúnir':
        distribution = getEarlyFarmedDistribution(stofnstaerdir, farmNo)
    else:
        distribution = getLateFarmedDistribution(stofnstaerdir, farmNo)

    ax.bar(st.session_state['rivers']['nafn'], distribution)
    return ax

def plotResult(ax, river, results):
    print(results)
    if river == 'Heild':
        results = results.mean(axis=0)
        ax.bar(results.index, results)
        ax.axhline(4, color='r', linestyle='dashed', linewidth=1)
        ax.set_title('Meðalhlutfall eldislaxa í á')
        ax.set_ylabel('Meðalhlutfall')
    else:
        ax.hist(results.loc[:,river])
        ax.axvline(results.loc[:,river].mean(), color='g', linestyle='dashed', linewidth=1)
        ax.axvline(4, color='r', linestyle='dashed', linewidth=1)
        ax.text(results.loc[:,river].mean()+0.2,1,'Meðaltal',rotation=0,color='g')
        ax.set_title(f'Hlutfall eldislaxa í {river}')
        ax.set_xlabel('Hlutfall')
        ax.set_ylabel('Fjöldi ára')
    return ax