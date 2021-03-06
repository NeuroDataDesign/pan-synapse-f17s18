import numpy as np
import pandas as pd
from skimage import measure
from skimage import filters
import pymeda

def get_pymeda_features(predictions, raw_data):
    #run connected components
    components = label_synapses(predictions)
    synapse_centroids = calculate_synapse_centroids(components)
    features = get_aggregate_sum(synapse_centroids, raw_data)
    return features
    
def label_synapses(predictions):
    synapse_labels = measure.label(predictions, background=0)
    connected_components = {}
    for z in range(synapse_labels.shape[0]):
        for y in range(synapse_labels.shape[1]):
            for x in range(synapse_labels.shape[2]):
                if (synapse_labels[z][y][x] in connected_components.keys()):
                    connected_components[synapse_labels[z][y][x]].append((z, y, x))
                else:
                    connected_components[synapse_labels[z][y][x]] = [(z, y, x)]
    connected_components.pop(0)
    return connected_components

# Input: dictionary of connected_components
def calculate_synapse_centroids(connected_components):
    synapse_centroids = []
    for key, value in connected_components.items():
        z, y, x = zip(*value)
        synapse_centroids.append((int(sum(z)/len(z)), int(sum(y)/len(y)), int(sum(x)/len(x))))
    return synapse_centroids

# Data should be z transformed
def get_aggregate_sum(synapse_centroids, data):
    z_max, y_max, x_max = data[next(iter(data))].shape
    data_dictionary = dict((key, []) for key in data.keys())
    for centroid in synapse_centroids:
        z, y, x = centroid
        z_lower = z - 1
        z_upper = z + 1
        y_lower = y - 11
        y_upper = y + 11
        x_lower = x - 11
        x_upper = x + 11
        # prob a better way but w/e tired rn
        # ignore boundary synapses
        if z_lower < 0 or z_upper >= z_max:
            continue
        if y_lower < 0 or y_upper >= y_max:
            continue
        if x_lower < 0 or x_upper >= x_max:
            continue
        for key in data.keys():
            data_dictionary[key].append(np.sum(data[key][z_lower:z_upper, y_lower:y_upper, x_lower: x_upper]))
    return data_dictionary

def get_data_frame(data_dict):
    df = pd.DataFrame(data_dict)
    df = df.loc[:, (df != 0).any(axis=0)]
    return df

def pymeda_pipeline(predictions, raw_data, title = "PyMeda Plots", cluster_levels = 2, path = "./"):
    features = get_pymeda_features(predictions, raw_data)
    df = get_data_frame(features)
    meda = pymeda.Meda(data = df, title = title, cluster_levels = cluster_levels)
    meda.generate_report(path)
    return
