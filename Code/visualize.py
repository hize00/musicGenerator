from music21 import *
import turtle
import random
import math
import pygame
import time


# parse the midi file returning a dictionary (keys: notes B2, E4, B4.E4.C4 --- values: "pitch index")
def song_to_pitch_dict(song):
    song = converter.parse(song)
    raw_components = []
    notes = []
    note_dict = {}
    #roll = song.parts[0]
    #roll.measures(1, 100).plot()
    for s in song.recurse():
        raw_components.append(s)
        try:
            if s.isNote:
                notes.append((s.name, s.octave))
                note_dict[s.nameWithOctave] = 0
            elif s.isChord:
                chord, name, pitch = get_chord_notation(s)
                notes.append((name, pitch))
                note_dict[chord] = 0
        except:
            pass

    """TODO add F#,C- etc"""
    alphabet = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    val_sorted = sorted(notes, key=lambda word: [alphabet.index(c) for c in word[0]])
    val_sorted = set(val_sorted)
    val_sorted = sorted(val_sorted, key=lambda element: element[1])

    for index, item in enumerate(val_sorted):
        note_dict[to_note_notation(item[0], item[1])] = index+1

    return note_dict, notes


# e.g: transforms 'CED 4' to 'C4.E4.D4'
def to_note_notation(s, pitch):
    note = ''
    if len(s) > 1:
        for c in s:
            note = note + c + str(pitch) + '.'
        note = note[:-1]
    else:
        note = s + str(pitch)
    return note


# get data from a music21 chord string --- for example: <music21 B4 E4> -> B4.E4, BE, 4
def get_chord_notation(s):
    chord = ''
    name = ''
    for p in s.pitches:
        chord = chord + p.nameWithOctave + '.'
        name = name + p.name
        pitch = p.octave
    chord = chord[:-1]
    return chord, name, pitch


def spinner():
    fred = turtle.Turtle()
    fred.hideturtle()
    fred.speed(0)
    length = 500
    angle = 91
    colors = ['gold', 'red', 'blue', 'green', 'pink', 'turquoise', 'purple', 'orange', 'white', 'black']

    for r in range(length):
        color = random.choice(colors)
        fred.pencolor(color)
        fred.fillcolor(color)
        fred.forward(r)
        fred.left(angle)
    turtle.exitonclick()


def testDraw():
    fred = turtle.Turtle()
    fred.hideturtle()
    fred.speed(0)
    w = fred.screen.canvwidth
    h = fred.screen.canvheight

    fred.pencolor("red")
    for i in range(0, 10):
        fred.setpos(random.randint(1, w), random.randint(1,h))
        fred.pendown()
        fred.goto(random.randint(1, w), random.randint(1, h))
        fred.penup()
    turtle.exitonclick()


def wave(notes_dict, notes):
    fred = turtle.Turtle()
    fred.hideturtle()
    fred.speed(0)
    w = fred.screen.window_width()
    h = fred.screen.window_height()
    x = -w
    y = 0
    colors = ['gold', 'red', 'blue', 'green', 'pink', 'turquoise', 'purple', 'orange', 'white', 'black']

    size = len(notes_dict)
    if h % size == 0:
        delta_h = math.ceil((h % size))
    else:
        delta_h = h / size

    """
    REMAPPARE PITCH PER CANVAS ex: (1,23) deve diventare in (-1000, 1000=
    """

    fred.setpos(0, h/2)
    for n in notes:
        time.sleep(0.15)
        x = x + 3
        y = notes_dict[to_note_notation(n[0], n[1])] * delta_h/2
        color = random.choice(colors)
        fred.pencolor(color)
        fred.pendown()
        fred.goto(x, y)
        fred.penup()


# play music file
def play_music(music_file):
    pygame.init()
    clock = pygame.time.Clock()
    try:
        pygame.mixer.music.load(music_file)
        print("Music file %s loaded!" % music_file)
    except pygame.error:
        print("File %s not found! (%s)" % (music_file, pygame.get_error()))
        return
    pygame.mixer.music.play()
    note_pitch_dict, notes = song_to_pitch_dict(music_file)

    """ DRAW WHILE PLAYING MUSIC"""
    wave(note_pitch_dict, notes)

    while pygame.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)


if __name__ == '__main__':
    note_pitch_dict, notes = song_to_pitch_dict('test.mid')
    # spinner()
    # testDraw()
    play_music('test.mid')

