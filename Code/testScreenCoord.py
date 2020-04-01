from turtle import Screen


def getPos(x, y):
    clicks.append((x, y))


def display():
    print(clicks)
    clicks.clear()


screen = Screen()
screen.screensize(500, 500)

clicks = []

screen.onscreenclick(getPos)
screen.onkeypress(display, "P")

screen.listen()
screen.mainloop()