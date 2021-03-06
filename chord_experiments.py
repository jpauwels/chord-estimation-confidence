#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import numpy as np
from os.path import join, basename, splitext, isfile
from chord_estimation import HMMSmoothedChordsFromTemplates, run_on_file_list, run_on_file_list_with_arg, evaluate_chords, MadMomDeepChromaExtractor, MadMomCLPChromaExtractor, MadMomPCPChromaExtractor, MadMomHPCPChromaExtractor
import pandas as pd

def run_experiments(list_path, audio_dir, reference_label_dir, output_dir, chroma_extractor, chromas, chord_types, type_templates, self_probs, audio_suffix='.wav', chordfile_suffix='.lab', hmm_decoders=['decodeMAP']):
    list_name = splitext(basename(list_path))[0]
    
    if not all([isfile(join(output_dir, 'HMMChords-{}-{}Ps'.format(y, round(x,3)), '{}-ResultsMirex.txt'.format(list_name))) for x in self_probs for y in hmm_decoders]):
        # Calculate chromagrams
        chromagrams = run_on_file_list(list_path, lambda x: chroma_extractor(join(audio_dir, x+audio_suffix)), verbose=True)
        # Calculate chords with confidence from chromagrams
        print('HMM self probabilities: ', end='')
        for self_prob in self_probs:
            print(round(self_prob, 3), end=' ')
            for decoder in hmm_decoders:
                chord_dir = join(output_dir, 'HMMChords-{}-{}Ps'.format(decoder, round(self_prob,3)))
                log_probs_and_confidences = run_on_file_list_with_arg(list_path, HMMSmoothedChordsFromTemplates(audio_dir, chord_dir, chromas, chord_types, type_templates, chroma_extractor, self_prob, audio_suffix, chordfile_suffix, decode_method=decoder), chromagrams)
                if log_probs_and_confidences:
                    pd.DataFrame(log_probs_and_confidences).to_csv(join(chord_dir, list_name+'-logprobs_confidences.csv'), index=False, header=False)
        print('')
    else:
        print('HMM self probabilities: ' + ' '.join(map(lambda x: str(round(x, 3)), self_probs)))
    # Evaluate chord sequences
    for decoder in hmm_decoders:
        hmm_scores = []
        for self_prob in self_probs:
            chord_dir = join(output_dir, 'HMMChords-{}-{}Ps'.format(decoder, round(self_prob, 3)))
            hmm_scores.append(evaluate_chords(list_path, reference_label_dir, chord_dir, 'MirexMajMin', join(chord_dir, '{}-ResultsMirex.txt'.format(list_name))))
        print('{} {} HMM chord scores: {}'.format(list_name, decoder, hmm_scores))
        if len(self_probs) > 1:
            print('Best score of {} for self probability of {}'.format(np.max(hmm_scores), self_probs[np.argmax(hmm_scores)]))


## Chroma extraction configuration
samplerate = 44100
block_size = 8192
step_size = 4410

## Chord estimation configuration
type_templates = np.array([[1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                           [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
                           [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                           [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]])
chord_types = ['maj', 'min', 'dim', 'aug']
chromas = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
chord_self_probs = [0.1]
hmm_decoders = ['decodeMAP_with_medianOPC', 'decode_with_PPD']

## Experiments
run_experiments('Lists/sines.lst', 'Audio', 'Ground-Truth', join('Experiments', 'DeepChroma', 'Sines'), MadMomDeepChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)

# Isophonics
# run_experiments('Lists/IsophonicsChords2010.lst', '/import/c4dm-datasets/C4DM Music Collection', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'DeepChroma', 'Isophonics'), MadMomDeepChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/IsophonicsChords2010.lst', '/import/c4dm-datasets/C4DM Music Collection', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'CLPChroma', 'Isophonics'), MadMomCLPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/IsophonicsChords2010.lst', '/import/c4dm-datasets/C4DM Music Collection', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'PCPChroma', 'Isophonics'), MadMomPCPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/IsophonicsChords2010.lst', '/import/c4dm-datasets/C4DM Music Collection', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'HPCPChroma', 'Isophonics'), MadMomHPCPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)

# RWC-Popular
# run_experiments('Lists/RWC-Popular.lst', '../Datasets/RWC-Popular', '../Ground-Truth/Chord Annotations MARL/RWC_Pop_Chords', join('Experiments', 'DeepChroma', 'RWC-Popular'), MadMomDeepChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, audio_suffix='.aiff', self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/RWC-Popular.lst', '../Datasets/RWC-Popular', '../Ground-Truth/Chord Annotations MARL/RWC_Pop_Chords', join('Experiments', 'CLPChroma', 'RWC-Popular'), MadMomCLPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, audio_suffix='.aiff', self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/RWC-Popular.lst', '../Datasets/RWC-Popular', '../Ground-Truth/Chord Annotations MARL/RWC_Pop_Chords', join('Experiments', 'PCPChroma', 'RWC-Popular'), MadMomPCPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, audio_suffix='.aiff', self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('Lists/RWC-Popular.lst', '../Datasets/RWC-Popular', '../Ground-Truth/Chord Annotations MARL/RWC_Pop_Chords', join('Experiments', 'HPCPChroma', 'RWC-Popular'), MadMomHPCPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, audio_suffix='.aiff', self_probs=chord_self_probs, hmm_decoders=hmm_decoders)

# Isophonics stereo augmented
# run_experiments('Lists/IsophonicsChords2010-augmentedstereo.lst', '/import/c4dm-01/StereoSeparation', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'DeepChroma', 'IsophonicsAugmented'), MadMomDeepChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
# run_experiments('../Lists/IsophonicsChords2010-augmentedstereo.lst', '/import/c4dm-01/StereoSeparation', '../Ground-Truth/Chord Annotations C4DM', join('Experiments', 'CLPChroma', 'IsophonicsAugmented'), MadMomCLPChromaExtractor(samplerate, block_size, step_size), chromas, chord_types, type_templates, self_probs=chord_self_probs, hmm_decoders=hmm_decoders)
