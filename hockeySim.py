from random import randrange

MAXCHANCE = 100


class SwayTooLargeError(Exception):
    def __str__(self):
        return 'Sway must be between -149 and 149.'


def fast_randint(s, b): return randrange(s, b + 1)


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


def case(lvl):
    num1 = fast_randint(0, lvl)
    num2 = fast_randint(0, lvl)
    return num1 == num2


# Sway: Bases the odds for one team over the other. The farther the param is from 0
# the more the odds lean toward the team. Use negative number for TEAM 1 or positive
# number for TEAM 2.


def simulate(sway: int = 0, periodTime: int = 400):
    out = []
    if sway > 150 or sway < -150: raise SwayTooLargeError

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
    if sway != 0:
        # xteam: NOT team that has a higher change
        xteam = '1' if sway < 0 else '2'
        team = '1' if xteam == '2' else '2'
        xteamNegChance = abs(sway)
        teamActionsList = [[
            int(xteam if case(xteamNegChance) else team) for __ in range(periodTime - 1)
        ] for _ in range(3)]
    else:
        teamActionsList = [[fast_randint(1, 2) for __ in range(periodTime - 1)] for _ in range(3)]

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

    maxTimeBetweenThingsHappening = 10

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
    # How much the SOG odds change
    sogOddsChangeOnPenalty = {
        'inc': 5,
        'dec': 10
    }

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
        'sog': 40
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
                        odds['TEAM 2']['sog'] -= sogOddsChangeOnPenalty['dec']
                        odds['TEAM 1']['sog'] += sogOddsChangeOnPenalty['inc']
                    else:
                        currentPenalties['TEAM 1'][pi1] -= 1

            if len(currentPenalties['TEAM 2']) > 0:
                for pi2, _ in enumerate(currentPenalties['TEAM 2']):
                    if currentPenalties['TEAM 2'][pi2] == 0:
                        del currentPenalties['TEAM 2'][pi2]
                        odds['TEAM 1']['sog'] -= sogOddsChangeOnPenalty['dec']
                        odds['TEAM 2']['sog'] += sogOddsChangeOnPenalty['inc']
                    else:
                        currentPenalties['TEAM 2'][pi2] -= 1

            # init stuff
            rand = fast_randint(0, MAXCHANCE)

            # Determines team that this play will be on
            team = 'TEAM ' + str(teamActionsList[period - 1][s - 1])
            action = actions[team][rand]
            timeIntoPeriod = s
            if action == 'goal' and lastAction == 'g' and sinceLast < 60:
                sinceLast += 1
                continue
            timeIntoPeriod = secs_to_mins_secs(timeIntoPeriod)

            # Handling different events
            match action:
                case 'penalty':
                    out.append(f"{team} got a penalty for {possiblePenalties[fast_randint(0, 8)]} \
{timeIntoPeriod} into period {period}")
                    currentPenalties[team].append(90)
                    pastPenalties[team] += 1
                    if team == 'TEAM 1':
                        odds['TEAM 2']['sog'] += sogOddsChangeOnPenalty['inc']
                        odds['TEAM 1']['sog'] -= sogOddsChangeOnPenalty['dec']
                    elif team == 'TEAM 2':
                        odds['TEAM 1']['sog'] += sogOddsChangeOnPenalty['inc']
                        odds['TEAM 2']['sog'] -= sogOddsChangeOnPenalty['dec']

                case 'sog':
                    if case(8):
                        frmt = f'{team} scored a goal {timeIntoPeriod} into period {str(period)}!'
                        out.append(frmt)
                        if case(15):
                            waiveReasons = ['a penalty', 'an offside', 'goalie interference']
                            out.append(f"Wait... it's under review... there might have been\
{waiveReasons[fast_randint(0, 2)]}!")
                            if case(3):
                                out.append(f"The goal has been waived! Unlucky for {team}")
                                lastAction = ''
                            else:
                                out.append(f"It's still a goal!")
                                goals[team] += 1
                                shotsOnGoal[team] += 1
                                lastAction = 'g'
                        else:
                            goals[team] += 1
                            shotsOnGoal[team] += 1
                            lastAction = 'g'
                        out.append(f"SCORE: {goals['TEAM 1']}-{goals['TEAM 2']}")
                        continue
                    out.append(f"Shot on goal by {team} {timeIntoPeriod} into period {period}")
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
            secsIntoOvertime = secs_to_mins_secs(s)
            rand = fast_randint(0, MAXCHANCE)
            team = 'TEAM ' + str(fast_randint(1, 2))
            action = actions[team][rand]
            if action == 'sog':
                if case(25):
                    goals[team] += 1
                    out.append(f'\tOVERTIME GOAL FOR {team} {secsIntoOvertime} INTO OVERTIME! \
\nScore: {goals["TEAM 1"]}-{goals["TEAM 2"]}')
                else:
                    shotsOnGoal[team] += 1
                    out.append(f'Shot on goal by {team} {secsIntoOvertime} into overtime')
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
                reasonForMiss = str(reasonsForMiss[fast_randint(0, 5)])
                xteam = 'TEAM ' + '1' if team[-1] == '1' else '2'
                out.append(reasonForMiss.replace('_TEAM_', team).replace('_XTEAM_', xteam))

    # "Goalies are cracked" shootout
    if goals['TEAM 1'] == goals['TEAM 2']:
        soRound = 0
        while True:
            soRound += 1
            shootoutRoundAsStr: str = str(soRound)
            if case(8):
                out.append(f'TEAM 1 scored a goal in round {shootoutRoundAsStr}. Will TEAM 2 be able to tie it up?')
                goals['TEAM 1'] += 1
            else:
                out.append(f"TEAM 1 wasn't able to score in round {shootoutRoundAsStr}. Will TEAM 2 be able to score?")
                if case(8):
                    out.append(f"TEAM 2 SCORED IN ROUND {shootoutRoundAsStr}! What a goal! TEAM 2 wins!")
                    goals['TEAM 2'] += 1
                    break
                continue
            if case(8):
                out.append(f"TEAM 2 scored as well! Time for round {shootoutRoundAsStr}.")
                goals['TEAM 2'] += 1
                continue
            else:
                out.append("TEAM 2 COULDN'T MAKE IT! TEAM 1 WINS!")
                break

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
    # Team rating:
    # Goals are worth 4 points, SOG are worth 1 point for two, penalties are -2 points each, and goalie having
    # a sv% above 90% gives 2 points.
    return {
        'winner': winner,
        'endResultType': endResultType,
        'outputAsText': out,
        'TEAM 1': {
            'goals': goals['TEAM 1'],
            'penalties': pastPenalties['TEAM 1'],
            'sog': shotsOnGoal['TEAM 1'],
            'g_sv%': goalie1SVP,
            'rating': goals['TEAM 1'] * 4 + round(shotsOnGoal['TEAM 1'] / 2) + pastPenalties['TEAM 1'] * -2 +
            2 if goalie1SVP > 90 else 0
        },
        'TEAM 2': {
            'goals': goals['TEAM 2'],
            'penalties': pastPenalties['TEAM 2'],
            'sog': shotsOnGoal['TEAM 2'],
            'g_sv%': goalie2SVP,
            'rating': goals['TEAM 2'] * 4 + round(shotsOnGoal['TEAM 2'] / 2) + pastPenalties['TEAM 2'] * -2 +
            2 if goalie2SVP > 90 else 0
        }
    }


if __name__ == '__main__':
    # Create final scoreboard
    results = simulate()

    endingOut = f'''
    \tFINAL SCORE: {results['TEAM 1']['goals']}-{results['TEAM 2']['goals']}{results['endResultType']}
    \tSOG - TEAM 1: {results['TEAM 1']['sog']}
    \tSOG - TEAM 2: {results['TEAM 2']['sog']}
    \tGOALIE SV% - TEAM 1: {results['TEAM 1']['g_sv%']}%
    \tGOALIE SV% - TEAM 2: {results['TEAM 2']['g_sv%']}%

    \tPENALTIES - TEAM 1: {results['TEAM 1']['penalties']}
    \tPENALTIES - TEAM 2: {results['TEAM 2']['penalties']}
    '''

    endingOut += f"\n{results['winner']} won the game!"
    output = '\n'.join(results['outputAsText']) + '\n\n' + endingOut

    # PRINT OUTPUT :D
    print(output)

    # For running the file directly
    endInput = input('\n\n>>> press enter to continue')
