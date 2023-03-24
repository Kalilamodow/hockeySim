from random import randint

MAXCHANCE = 100


class BruhException(Exception):
    def __init__(self):
        print('how did you even MANAGE to screw that up?')
        input('>>> press enter to continue')

    def __str__(self):
        return 'how did you even MANAGE to screw that up?\n>>> press enter to continue'


case = lambda lvl: randint(0, lvl) == randint(0, lvl)


def secs_to_mins_secs(seconds: int) -> str:
    mins = 0
    osc = seconds

    while osc > 59:
        mins += 1
        osc -= 60
    if len(str(mins)) < 2:
        mins = '0' + str(mins)
    if len(str(osc)) < 2:
        osc = '0' + str(osc)
    return f'{mins}:{osc}'


def create_actions_list(action_chances: dict) -> list:
    r = []
    chance_of_penalty = action_chances['penalty']
    chance_of_sog = action_chances['sog']
    chance_of_nothing = (MAXCHANCE + 1) - (chance_of_sog + chance_of_penalty)

    _ = [r.append('penalty') for _ in range(chance_of_penalty)]
    _ = [r.append('sog') for _ in range(chance_of_sog)]
    _ = [r.append('') for _ in range(chance_of_nothing)]
    return r


out = []
userTime = input('Period time in MM:SS (20:00): ')
userTime = '20:00' if not userTime else userTime
userTime = userTime.split(':')
gameTime = int(userTime[0]) * 60 + int(userTime[1])
periodTime = int(round(gameTime / 3))

# teamActionsList: creates a list for each period containing 1s and 2s. The main FOR loop then
# retrieves which team the action happens to depending on the team in the list.

# Structure:
# [
#   [ # period one array
#       1, 2, 1, 1, 1, 1, 1, 1, 2...
#   ],
#   [ # p2 array
#       2, 2, 1, 2, 1, 1, 2, 2, 2...
#   ],
#   [ # period 3 array
#       1, 1, 2, 2, 2, 1, 2, 1, 1...
#   ]
# ]
# upper comment shows use of this list
teamActionsList = [[randint(1, 2) for __ in range(periodTime - 1)] for _ in range(3)]
occurrences = (
    None,  # because we only want 1s and 2s :)
    teamActionsList[0].count(1) + teamActionsList[1].count(1) + teamActionsList[2].count(1),
    teamActionsList[0].count(2) + teamActionsList[1].count(2) + teamActionsList[2].count(2)
)
pred = 1 if occurrences[1] > occurrences[2] else 2 if occurrences[2] > occurrences[1] else 'idk'

if pred == 1:
    out.append(f'Prediction: TEAM 1 by {str(round((occurrences[1] - occurrences[2]) / 3))}0')
elif pred == 2:
    out.append(f'Prediction: TEAM 2 by {str(round((occurrences[2] - occurrences[1]) / 3))}0')
else:
    out.append("The teams seem equally matched! We'll see who'll win...")
out.append('\n')

maxTimeBetweenThingsHappening = input(f"Time between things happening \
(default: {round(gameTime / 120)}): ")

maxTimeBetweenThingsHappening = round(gameTime / 120) if not maxTimeBetweenThingsHappening else None

# Period for loop
period = 1

possiblePenalties = (
    'TRIPPING',
    'HOOKING',
    'TRASH TALK',
    'UNSPORTSMANLIKE CONDUCT',
    'CROSS-CHECKING',
    'SLASHING',
    'HOLDING',
    'HIGH-STICKING',
    'INTERFERENCE'
)

# Init stats vars
goals = {
    'TEAM 1': 0,
    'TEAM 2': 0
}
shotsOnGoal = {
    'TEAM 1': 0,
    'TEAM 2': 0
}

# Create lists of odds/actions for teams
startingOdds = {
    'penalty': 3,
    'sog': 30
}
odds = {
    'TEAM 1': startingOdds,
    'TEAM 2': startingOdds
}
startingActionsList = create_actions_list(startingOdds)
actions = {
    'TEAM 1': startingActionsList,
    'TEAM 2': startingActionsList
}

# lastAction variable: during loop, makes sure goals/penalties can't happen twice in a
# row. Even if it's random, we don't want something to happen many times in a row.
# sinceLast variable: var is incremented every loop. It's used to get the amount
# of time since the last play was done. If it's less than 'maxTimeBetweenThingsHappening',
# then skip the loop. Otherwise, reset sinceLast and continue.
lastAction = ''
sinceLast = 0

currentPenalties = {
    'TEAM 1': [],
    'TEAM 2': []
}
pastPenalties = {
    'TEAM 1': 0,
    'TEAM 2': 0
}

out.append('\tGAME START\n')

# endResultType: '', ' /OT', ' /SO' determines type of game that match ended in.
endResultType = ''

while period < 4:
    out.append(f'\nPERIOD {period}\n')
    for s in range(periodTime):
        # Stuff to make sure plays do not happen too frequently
        if sinceLast < maxTimeBetweenThingsHappening:
            sinceLast += 1
            continue
        if s < periodTime / 5: continue

        # Penalty handling
        if len(currentPenalties['TEAM 1']) > 0:
            for pi1, _ in enumerate(currentPenalties['TEAM 1']):
                if currentPenalties['TEAM 1'][pi1] == 0:
                    del currentPenalties['TEAM 1'][pi1]
                    odds['TEAM 2']['sog'] -= 10
                    odds['TEAM 1']['sog'] += 5
                else:
                    currentPenalties['TEAM 1'][pi1] -= 1

        if len(currentPenalties['TEAM 2']) > 0:
            for pi2, _ in enumerate(currentPenalties['TEAM 2']):
                if currentPenalties['TEAM 2'][pi2] == 0:
                    del currentPenalties['TEAM 2'][pi2]
                    odds['TEAM 1']['sog'] -= 20
                    odds['TEAM 2']['sog'] += 5
                else:
                    currentPenalties['TEAM 2'][pi2] -= 1

        # init stuff
        rand = randint(0, MAXCHANCE)

        # Determines team that this play will be on
        team = 'TEAM ' + str(teamActionsList[period - 1][s - 1])
        action = actions[team][rand]
        secondsIntoPeriod = s
        if action == 'goal' and lastAction == 'g' and sinceLast < 60:
            sinceLast += 1
            continue
        secondsIntoPeriod = secs_to_mins_secs(secondsIntoPeriod)

        # Handling different events
        match action:
            case 'penalty':
                out.append(f"{team} got a penalty for {possiblePenalties[randint(0, 8)]} \
{secondsIntoPeriod} into period {period}")
                currentPenalties[team].append(90)
                pastPenalties[team] += 1
                if team == 'TEAM 1':
                    odds['TEAM 2']['sog'] += 20
                    odds['TEAM 1']['sog'] -= 5
                elif team == 'TEAM 2':
                    odds['TEAM 1']['sog'] += 20
                    odds['TEAM 2']['sog'] -= 5
                else:
                    raise BruhException

            case 'sog':
                if case(50):
                    frmt = f'{team} scored a goal {secondsIntoPeriod}\
]into period {str(period)}!'
                    out.append(frmt)
                    if case(10):
                        waiveReasons = ['a penalty', 'an offside', 'goalie interference']
                        out.append(f"Wait... it's under review... there might have been\
{waiveReasons[randint(0, 2)]}!")
                        if case(3):
                            out.append(f"The goal has been waived! Unlucky for {team}")
                            lastAction = ''
                        else:
                            out.append(f"They didn't have enough evidence! It's still a goal! \
{team} sure is lucky...")
                            goals[team] += 1
                            shotsOnGoal[team] += 1
                            lastAction = 'g'
                    else:
                        goals[team] += 1
                        shotsOnGoal[team] += 1
                        lastAction = 'g'
                    out.append(f"SCORE: {goals['TEAM 1']}-{goals['TEAM 2']}")
                    continue
                out.append(f"Shot on goal by {team} {secondsIntoPeriod} into period {period}")
                shotsOnGoal[team] += 1
                lastAction = ''

            case _:
                lastAction = ''
        sinceLast = 0
        actions['TEAM 1'] = create_actions_list(odds['TEAM 1'])
        actions['TEAM 2'] = create_actions_list(odds['TEAM 2'])

    period += 1

# Overtime!
reasonsForMiss = (
    '_TEAM_ shot it wide of net.',
    "_XTEAM_'s goalie saved it.",
    "An absolutely beautiful save by _XTEAM_'s goalie!",
    '_TEAM_ shot it high.',
    "Deflected by _XTEAM_'s goalies blocker up and out of play.",
    "Failed spin move by _TEAM_!"
)
sinceLast = 0
if goals['TEAM 1'] == goals['TEAM 2']:
    endResultType = ' /OT'
    out.append('\n\tOVERTIME\n')
    odds['TEAM 1'] = {
        'penalty': 0,
        'sog': 35
    }
    odds['TEAM 2'] = {
        'penalty': 0,
        'sog': 35
    }
    actions['TEAM 1'] = create_actions_list(odds['TEAM 1'])
    actions['TEAM 2'] = create_actions_list(odds['TEAM 2'])
    for s in range(300):
        if sinceLast < maxTimeBetweenThingsHappening / 4:
            sinceLast += 1
            continue
        if not case(10):
            continue
        rand = randint(0, MAXCHANCE)
        team = 'TEAM ' + str(randint(1, 2))
        action = actions[team][rand]
        if action == 'sog':
            if case(25):
                goals[team] += 1
                out.append(f'\tOVERTIME GOAL FOR {team}! \nScore: {goals["TEAM 1"]}-{goals["TEAM 2"]}')
            else:
                shotsOnGoal[team] += 1
                out.append(f'Shot on goal by {team}')
        sinceLast = 0

# "Regular" shootout
if goals['TEAM 1'] == goals['TEAM 2']:
    out.append('\n\tSHOOTOUT\n')
    endResultType = ' /SO'
    for n in range(10):
        team = 1 if (n % 2) == 0 else 2
        team = 'TEAM ' + str(team)
        if case(10):
            goals[team] += 1
            out.append(f'Shootout goal by {team}!')
        else:
            reasonForMiss = str(reasonsForMiss[randint(0, 5)])
            xteam = 'TEAM ' + '1' if team[-1] == '1' else '2'
            out.append(reasonForMiss.replace('_TEAM_', team).replace('_XTEAM_', xteam))

# "Goalies are cracked" shootout
if goals['TEAM 1'] == goals['TEAM 2']:
    winnerYet = False
    soRound = 0
    while not winnerYet:
        soRound += 1
        if case(8):
            out.append('TEAM 1 scored a goal in round' + str(soRound) + '. Will TEAM 2 be able to tie it up?')
            goals['TEAM 1'] += 1
        else:
            out.append("TEAM 1 wasn't able to score in round"
                       + str(soRound) + ". Will TEAM 2 be able to score?")
            if case(8):
                out.append("TEAM 2 SCORED IN ROUND " + str(soRound) + "! What a goal! TEAM 2 wins!")
                goals['TEAM 2'] += 1
            continue
        if case(8):
            out.append("TEAM 2 scored as well! Time for round " + str(soRound) + '.')
            goals['TEAM 2'] += 1
        else:
            out.append("TEAM 2 COULDN'T MAKE IT! TEAM 1 WINS!")

# Determines winner of game
if goals['TEAM 1'] > goals['TEAM 2']:
    winner = 'TEAM 1'
elif goals['TEAM 2'] > goals['TEAM 1']:
    winner = 'TEAM 2'
else:
    winner = 'my code is broken :('

# Determine goalie save percentages
if goals['TEAM 2'] != 0:
    goalie1SVP = round((1 - goals['TEAM 2'] / shotsOnGoal['TEAM 2']) * 100, 2)
else:
    goalie1SVP = 100
if goals['TEAM 1'] != 0:
    goalie2SVP = round((1 - goals['TEAM 1'] / shotsOnGoal['TEAM 1']) * 100, 2)
else:
    goalie2SVP = 100

if __name__ == '__main__':
    # Create final scoreboard
    endingOut = f'''
    \tFINAL SCORE: {goals['TEAM 1']}-{goals['TEAM 2']}{endResultType}
    \tSOG - TEAM 1: {shotsOnGoal['TEAM 1']}
    \tSOG - TEAM 2: {shotsOnGoal['TEAM 2']}
    \tGOALIE SV% - TEAM 1: {goalie1SVP}%
    \tGOALIE SV% - TEAM 2: {goalie2SVP}%

    \tPENALTIES - TEAM 1: {pastPenalties['TEAM 1']}
    \tPENALTIES - TEAM 2: {pastPenalties['TEAM 2']}
    '''

    endingOut += f'\n{winner} won the game!'
    output = '\n'.join(out) + '\n\n' + endingOut

    # PRINT OUTPUT :D
    print(output)

    # For running the file directly
    endInput = input('\n\n>>> press enter to continue')
else:
    # Scoring system: goal - 3p | SOG - 1p | penalty - -2p | goalie sv% > 90 - 2
    team1score = goals['TEAM 1'] * 4 + shotsOnGoal['TEAM 1'] + \
        pastPenalties['TEAM 1'] * -2 + 2 if goalie1SVP > 90 else 0
    team2score = goals['TEAM 2'] * 4 + shotsOnGoal['TEAM 2'] + \
        pastPenalties['TEAM 2'] * -2 + 2 if goalie2SVP > 90 else 0
    results = {
        'winner': winner,
        'TEAM 1': {
            'goals': goals['TEAM 1'],
            'penalties': pastPenalties['TEAM 1'],
            'sog': shotsOnGoal['TEAM 1'],
            'g_sv%': goalie1SVP,
            'score': team1score
        },
        'TEAM 2': {
            'goals': goals['TEAM 2'],
            'penalties': pastPenalties['TEAM 2'],
            'sog': shotsOnGoal['TEAM 2'],
            'g_sv%': goalie2SVP,
            'score': team2score
        }
    }

    def return_game(): return results
