from datetime import datetime


def sorted_players():
    """
    Current function reads the start and finish date of each racer from logs,
    counts the best lap time of each racer.
    """
    with open('../files/start.log', 'r') as start, open('../files/end.log', 'r') as end:
        start = start.read().splitlines()
        end = end.read().splitlines()
        players_list = []
        for players_start_data in start:
            for players_end_data in end:
                if players_start_data[0:3] == players_end_data[0:3]:
                    start_time = datetime.strptime(players_start_data[3:], '%Y-%m-%d_%H:%M:%S.%f')
                    finish_time = datetime.strptime(players_end_data[3:], '%Y-%m-%d_%H:%M:%S.%f')
                    players_list.append([str(finish_time - start_time)[:-3], players_start_data[0:3]])
        return sorted(players_list)


def build_report():
    """
    Current function combines all the information we need for printing the report
    such as name, team, and the best lap time of all the players
    :return:
    """
    report_data = []
    for lap_time, players_abbreviation in sorted_players():
        for players_initials, players_name, team_name in split_abbreviations():
            if players_abbreviation == players_initials:
                report_data.append([players_name, team_name, lap_time])
    return report_data


def split_abbreviations():
    """
    That function take a text file, and splits each abbreviation from file into 3 string in list:
    1. Abbreviation of each racer.
    2. The name of the racer.
    3. Team name.
    :return:
    """
    with open('../files/abbreviations.txt', 'r') as abbreviations:
        abbreviations = abbreviations.read().splitlines()
        return [abbreviation.split(sep='_') for abbreviation in abbreviations]


def print_report():
    """
    A function prints the report
    """
    list_of_results = build_report()
    for i in range(len(list_of_results)):
        print(f'{i+1}. {list_of_results[i][0]}' + (20-len(str(i+1))-len(list_of_results[i][0]))*' ' + '|' +
              5*' ' + list_of_results[i][1] + (30-len(str(list_of_results[i][1])))*' ' + '|' +
              5*' ' + list_of_results[i][2])
        if i == 14:
            print(80*'-')


if __name__ == '__main__':
    print_report()
