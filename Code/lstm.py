""" This module prepares midi file data and feeds it to the neural
    network for training """
import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import os

def train_network():
    """ Train a Neural Network to generate music """
    notes = get_notes()

    # get amount of pitch names
    n_vocab = len(set(notes))

    network_input, network_output = prepare_sequences(notes, n_vocab)

    model = create_network(network_input, n_vocab)

    train(model, network_input, network_output)

def get_notes():
    """ Get all the notes and chords from the midi files in the specified directory """
    notes = []

    # change path here for different songs
    # for file in glob.glob("songs_classical/*.mid"):
    for file in glob.glob("songs3/*_CONV.mid"):
        midi = converter.parse(file)

        print("Parsing %s" % file)

        notes_to_parse = None

        try: # file has instrument parts
            s2 = instrument.partitionByInstrument(midi)
            notes_to_parse = s2.parts[0].recurse() 
        except: # file has notes in a flat structure
            notes_to_parse = midi.flat.notes

        for element in notes_to_parse:
            if isinstance(element, note.Note):
                # if single note append it
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                # if chord compose the chord with int - ex: A5 B3 D3 -> 4.7.0
                notes.append('.'.join(str(n) for n in element.normalOrder))

    with open('data/notes', 'wb') as filepath:
        pickle.dump(notes, filepath)

    return notes


def prepare_sequences(notes, n_vocab):
    """ Prepare the sequences used by the Neural Network """
    # 100 means that we consider the previous 100 notes to make predictions
    sequence_length = 100

    # get all pitch names and sort them
    pitchnames = sorted(set(item for item in notes))

    # create a dictionary to map pitches to integers
    # key: note  description - value: int - ex: {'A5': 0, 'B3': 1...}
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    network_input = []
    network_output = []

    # create input sequences and the corresponding outputs
    for i in range(0, len(notes) - sequence_length, 1):
        # get 100 notes
        sequence_in = notes[i:i + sequence_length]
        # get first note after 100
        sequence_out = notes[i + sequence_length]
        # create input as array of arrays of 100 int (= sequence length) -> values of dictionary
        network_input.append([note_to_int[char] for char in sequence_in])
        # create output as array predictions -> values of dictionary
        network_output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    network_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    network_input = network_input / float(n_vocab)
    # one hot encoding
    network_output = np_utils.to_categorical(network_output)

    return (network_input, network_output)

def create_network(network_input, n_vocab):
    """ create the structure of the neural network """
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    return model

def train(model, network_input, network_output):
    """ train the neural network """
    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    #model.fit(network_input, network_output, epochs=200, batch_size=64, callbacks=callbacks_list)
    model.fit(network_input, network_output, epochs=150, batch_size=32, callbacks=callbacks_list)


def convert_notes():
    # converting everything into the key of C major or A minor

    # major conversions
    majors = dict(
        [("A-", 4), ("G#", 4), ("A", 3), ("A#", 2), ("B-", 2), ("B", 1), ("C", 0), ("C#", -1), ("D-", -1),  ("D", -2),
         ("D#", -3),("E-", -3), ("E", -4), ("F", -5), ("F#", 6), ("G-", 6), ("G", 5)])
    minors = dict(
        [("G#", 1), ("A-", 1), ("A", 0), ("A#", -1), ("B-", -1), ("B", -2), ("C", -3), ("C#", -4), ("D-", -4), ("D", -5),
         ("D#", 6), ("E-", 6), ("E", 5), ("F", 4), ("F#", 3), ("G-", 3), ("G", 2)])


    # os.chdir("./")
    for file in glob.glob("songs3/*.mid"):
        score = converter.parse(file)
        key = score.analyze('key')
        #    print key.tonic.name, key.mode
        if key.mode == "major":
            halfSteps = majors[key.tonic.name]

        elif key.mode == "minor":
            halfSteps = minors[key.tonic.name]

        newscore = score.transpose(halfSteps)
        key = newscore.analyze('key')
        f = file[:-4]
        newFileName = f + '_CONV.mid'
        newscore.write('midi', newFileName)

if __name__ == '__main__':
    # convert_notes()
    train_network()
