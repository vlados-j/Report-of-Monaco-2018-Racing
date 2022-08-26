from datetime import datetime


"""
It's a draft for task 6. Here is only several functions of processing data
"""


def collecting_racers_data(file_path: str, title_for_time: str):
    with open(file_path, 'r') as file:
        players_data = []
        players_list = file.read().splitlines()
        players_list = list(filter(None, players_list))
        for players_result in players_list:
            players_data.append({'racer_abbreviation': players_result.strip()[:3],
                                title_for_time: players_result.strip()[3:]})
        players_data.sort(key=lambda a: a['racer_abbreviation'])
        return players_data


def collecting_abbreviations(file_path: str):
    with open(file_path, 'r') as unsorted_file:
        abbreviations_list = []
        abbreviations = unsorted_file.read().splitlines()
        abbreviations = list(filter(None, abbreviations))
        for each_racer in abbreviations:
            separated_data = each_racer.strip().split(sep='_')
            abbreviations_list.append({'racer_abbreviation': separated_data[0],
                                       'full_name': separated_data[1],
                                       'team': separated_data[2]})
        abbreviations_list.sort(key=lambda a: a['racer_abbreviation'])
        return abbreviations_list


def data_merge():
    start_data = collecting_racers_data('../files/start.log', 'start_time')
    finish_data = collecting_racers_data('../files/end.log', 'finish_time')
    abbreviations_data = collecting_abbreviations('../files/abbreviations.txt')


print(collecting_racers_data('../files/start.log', 'start_time'))
print(collecting_racers_data('../files/end.log', 'finish_time'))
print(collecting_abbreviations('../files/abbreviations.txt'))
