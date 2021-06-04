from pygame.locals import *
import random
import sys
import copy, os, pygame

FPSSETT = 30  # кадров в секунду для обновления экрана
WINDOWWITH = 800  # ширина окна в пикселях
WINDOWHEIGHT = 600  # высота окна в пикселях
HFWINWIDTH = int(WINDOWWITH / 2)
HFWINHEIGHT = int(WINDOWHEIGHT / 2)
icon = pygame.image.load('Stars2.png')
pygame.display.set_icon(icon)

# ширина и высота каждой фигуры
TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 43

MOVE_STEP = 1  # кол-во пикселей, которые меняется при передвижении

# процент наружной декорации
OUTSIDE_DECORATION_PCT = 20

BLUE = (92, 204, 204)
DARKBLUE = (0, 99, 99)
BGCOLOR = BLUE
TEXTCOLOR = DARKBLUE

UP = 'вверх'
DOWN = 'вниз'
LEFT = 'лево'
RIGHT = 'право'


def main():
    global FPSCONTROL, DISPLAYSURF, IMAGESCAT, MAPTILE, DECOMPANOUT, FONTSB, PLAYERIMAGES, CURIMG

    # инициализация Pygame и настройка глобальных переменных
    pygame.init()
    FPSCONTROL = pygame.time.Clock()

    # поскольку Surface object и хранится в DISPLAYSURF
    # из функции pygame.display.set_mode()
    # это поверзностный объект появляется на экране компьютера
    # при вызове pygame.display.update ()

    DISPLAYSURF = pygame.display.set_mode((WINDOWWITH, WINDOWHEIGHT))

    pygame.display.set_caption('Звездная головоломка')
    FONTSB = pygame.font.Font('freesansbold.ttf', 20)

    # глобальное значение dict, которое будет содержать Pygame
    # поверхностнтыне объекты, возвращаемые  pygame.image.load().
    IMAGESCAT = {'uncovered goal': pygame.image.load('BlueSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'frog': pygame.image.load('frog.png'),
                  'cat': pygame.image.load('cat.png'),
                 'hamster': pygame.image.load('hamster.png'),
                 'pig': pygame.image.load('pig.png'),
                 'dog': pygame.image.load('dog.png'),
                 'rock': pygame.image.load('Rock.png'),
                 'short tree': pygame.image.load('Tree_Short.png'),
                 'tall tree': pygame.image.load('Tree_Tall.png'),
                 'ugly tree': pygame.image.load('Tree_Ugly.png')}

    # эти значения dict являются глобальными и отображают символы в текстовом файле

    MAPTILE = {'x': IMAGESCAT['corner'],
                   '#': IMAGESCAT['wall'],
                   'o': IMAGESCAT['inside floor'],
                   ' ': IMAGESCAT['outside floor']}
    DECOMPANOUT = {'1': IMAGESCAT['rock'],
                          '2': IMAGESCAT['short tree'],
                          '3': IMAGESCAT['tall tree'],
                          '4': IMAGESCAT['ugly tree']}

    # PLAYERIMAGES - все возможные персонажи, которыми может быть игрок.
    # currentImage - индекс текущего изображения игрока.
    CURIMG = 2
    PLAYERIMAGES = [IMAGESCAT['frog'],
                    IMAGESCAT['cat'],
                    IMAGESCAT['hamster'],
                    IMAGESCAT['pig'],
                    IMAGESCAT['dog']]

    startScreen()  # показывает начальный экран игры, пока игрок не нажмет клавишу для старта.

    # уровни из текстового файла readLevelsFile()

    levels = readLevelsFile('starPusherLevels.txt')
    currentLevelIndex = 0

    # основной игровой цикл. этот цикл выполняется.
    # когда пользователь завершает уровень, следующий/предыдущий цикл загружается.

    while True:
        # запуск уровня, для начала игры
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            # перейти на следующий уровень
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                # если уровней больше нет, то вернется к первому уровню
                currentLevelIndex = 0
        elif result == 'back':
            # перейти на предыдущий уровень
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                # если предыдущих уровней нет, то перейдет к последнему.
                currentLevelIndex = len(levels) - 1
        elif result == 'reset':
            pass  # Loop повторно вызывает runLevel() для сброса уровня.


def runLevel(levels, levelNum):
    global CURIMG
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True  # установить значерие True для вызова drawMap()
    levelSurf = FONTSB.render('Уровень %s из %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINDOWHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HFWINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HFWINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    levelIsComplete = False

    # отслеживание, насколько перемещается камера:
    cameraOffsetX = 0
    cameraOffsetY = 0

    # отслеживание, удерживаются ли клавиши для перемещения камеры:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True:  # основной игровой цикл
        # сброс переменных:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():  # цикл обработки события
            if event.type == QUIT:
                # игрок нажал "X" в углу окна.
                terminate()

            elif event.type == KEYDOWN:
                # обработка нажатия клавиш
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                # режим движения камеры
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:

                    CURIMG += 1
                    if CURIMG >= len(PLAYERIMAGES):

                        CURIMG = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                # отключить режим движения камеры.
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:
            # если игрок нажал клавишу, чтобы переместиться, сделайте ход
            # и двигайте любые звезды.
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                # счетчик шагов
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                # уровень пройден, показывается изображение "уровень пройден"
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += MOVE_STEP
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= MOVE_STEP
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += MOVE_STEP
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= MOVE_STEP

        # настроить объект Rect в зависимости от движения камеры.
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HFWINWIDTH + cameraOffsetX, HFWINHEIGHT + cameraOffsetY)

        # рисуем mapSurf на DISPLAYSURF Surface.
        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = FONTSB.render('Шаги: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINDOWHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            # уровень пройден. изображение "уровень пройден" остается
            # пока игрок не нажмет клавишу
            solvedRect = IMAGESCAT['solved'].get_rect()
            solvedRect.center = (HFWINWIDTH, HFWINHEIGHT)
            DISPLAYSURF.blit(IMAGESCAT['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()  # draw DISPLAYSURF to the screen.
        FPSCONTROL.tick()


def isWall(mapObj, x, y):
    ""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False  # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x'):
        return True  # wall is blocking
    return False


def decorateMap(mapObj, startxy):
    startx, starty = startxy

    # копия карты, чтоб не менялся оригинал
    mapObjCopy = copy.deepcopy(mapObj)

    # удаление символов, которые не являются стенами карты
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@'):
                mapObjCopy[x][y] = ' '

    # Заливка для определения внутренней или внешней плитки пола
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # преобразовывает стены в плитку
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y - 1) and isWall(mapObjCopy, x + 1, y)) or \
                        (isWall(mapObjCopy, x + 1, y) and isWall(mapObjCopy, x, y + 1)) or \
                        (isWall(mapObjCopy, x, y + 1) and isWall(mapObjCopy, x - 1, y)) or \
                        (isWall(mapObjCopy, x - 1, y) and isWall(mapObjCopy, x, y - 1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(DECOMPANOUT.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    """Возвращает True если положение (x, y) на карте заблокировано стеноц или звездой."""

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True  # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['stars']:
        return True  # a star is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):

    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']


    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    # проверяем, может ли персонаж двигаться в нужном направлении
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            # проверка, сможет ли игрок толкнуть звезду
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset * 2), playery + (yOffset * 2)):
                # перемещение звезды
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False

        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def startScreen():
    """Отображется начальный экран."""

    # размещение изображения заголовка
    titleRect = IMAGESCAT['title'].get_rect()
    topCoord = 20  # положение верхней части текста
    titleRect.top = topCoord
    titleRect.centerx = HFWINWIDTH
    topCoord += titleRect.height

    instructionText = ['Нажмите любую клавишу для старта.',
                       'Для прохождения уровня двигайте звездочку на нужное место.',
                       'Используйте клавиши со стрелками для перемещения фигур.',
                       'P - смена персонажа.',
                       'N - следующий уровень.',
                       'B - вернуться на предыдущий уровень.',
                       'Backspace - сброса уровня. Esc - выход из игры.', ]

    # Start with drawing a blank color to the entire window:
    DISPLAYSURF.fill(BGCOLOR)

    DISPLAYSURF.blit(IMAGESCAT['title'], titleRect)

    for i in range(len(instructionText)):
        instSurf = FONTSB.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 20  # расстояние между строчками в заголовке
        instRect.top = topCoord
        instRect.centerx = HFWINWIDTH
        topCoord += instRect.height
        DISPLAYSURF.blit(instSurf, instRect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return


        pygame.display.update()
        FPSCONTROL.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = []  # сожержит список объектов уровня
    levelNum = 0
    mapTextLines = []  # содержит линии для карты одного уровня
    mapObj = []  # объекты карты, созданные из данных mapTextLines
    for lineNum in range(len(content)):
        # обработка каждый строки, которая была в файле уровня
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # игнорировать ; в текстовом файле с уровнями
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # пустая строка означает конец карты в файле
            # преобразование текста в mapTextLines в объект уровня

            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # если добавить пробелы в конце коротких строк, карты будет более прямоугольной.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # преобразование mapTextLines в объекты карты
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None  # x и y для начальной позиции игрока
            starty = None
            goals = []
            stars = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))

            # проверка работочпособности уровней
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (
                levelNum + 1, lineNum, filename)
            # если отсутствует @ или +, игра не запускается
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (
                levelNum + 1, lineNum, filename)
            # уровень должен иметь хоть одну цель для завершения
            assert len(stars) >= len(
                goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (
                levelNum + 1, lineNum, filename, len(goals), len(stars))
            # уровень нельзя пройти, если нет конечной точки

            # создать объект уровня и объект состояния запуска игры
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            # сбросить переменные для чтения следующей карты
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x + 1][y] == oldCharacter:
        floodFill(mapObj, x + 1, y, oldCharacter, newCharacter)  # вызов справа
    if x > 0 and mapObj[x - 1][y] == oldCharacter:
        floodFill(mapObj, x - 1, y, oldCharacter, newCharacter)  # вызов слева
    if y < len(mapObj[x]) - 1 and mapObj[x][y + 1] == oldCharacter:
        floodFill(mapObj, x, y + 1, oldCharacter, newCharacter)  # вызов вниз
    if y > 0 and mapObj[x][y - 1] == oldCharacter:
        floodFill(mapObj, x, y - 1, oldCharacter, newCharacter)  # вызов вверх


def drawMap(mapObj, gameStateObj, goals):
    # mapSurf будет единственным объеком Surface на котором рисуются плитки.
    # вся карта размещается на DISPLAYSURF
    # сначала необходимо рассчитать ширину и высоту
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)  # начать с пустого цвета на поверхности

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in MAPTILE:
                baseTile = MAPTILE[mapObj[x][y]]
            elif mapObj[x][y] in DECOMPANOUT:
                baseTile = MAPTILE[' ']

            # сначала рисуется основная плитка пола/стены
            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in DECOMPANOUT:
                # рисуются урашения, которые есть на этой плитке
                mapSurf.blit(DECOMPANOUT[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    # A goal AND star are on this space, draw goal first.
                    mapSurf.blit(IMAGESCAT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESCAT['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGESCAT['uncovered goal'], spaceRect)

            # последний выход игрока
            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[CURIMG], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    # возвращается изначальное значение, если все цели отмечены звездами.
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            # нашли пространство с целью,он без звезды
            return False
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()