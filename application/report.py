from datetime import datetime


def collecting_racers_data(file_path: str, title_for_time: str):
    """
    Current function returns takes log file, and returns sorted list with racer abbreviation and time of each racer
    """
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
    """
    Current function takes the path of the file, and returns the name of players, teams, and theirs abbreviations
    """
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


def lap_time_calculator(start_time: str, finish_time: str):
    """
    Current function takes start and end time of each player, and calculates the lap time.
    If the time is negative, function returns an error
    """
    try:
        start_time = datetime.strptime(start_time, '%Y-%m-%d_%H:%M:%S.%f')
        finish_time = datetime.strptime(finish_time, '%Y-%m-%d_%H:%M:%S.%f')
        lap_time = str(finish_time - start_time)
        if lap_time[0] == '-':
            return 'Incorrect time. Please, check logs.'
        else:
            return str(finish_time - start_time)[:-3]
    except Exception:
        return 'Unexpected error. Please, check if the logs are correct'


def data_merge():
    """
    Current function takes all the parsed files, and returns combined a list with info about the racers for output
    """
    start_data = collecting_racers_data('../files/start.log', 'start_time')
    finish_data = collecting_racers_data('../files/end.log', 'finish_time')
    abbreviations_data = collecting_abbreviations('../files/abbreviations.txt')
    collected_data = []
    for racer_index in range(len(start_data)):
        if start_data[racer_index]['racer_abbreviation'] == finish_data[racer_index]['racer_abbreviation'] == abbreviations_data[racer_index]['racer_abbreviation']:
            collected_data.append({
                'full_name': abbreviations_data[racer_index]['full_name'],
                'team': abbreviations_data[racer_index]['team'],
                'lap_time': lap_time_calculator(start_data[racer_index]['start_time'], finish_data[racer_index]['finish_time'])
            })
        else:
            collected_data.append({
                'full_name': 'Invalid data',
                'team': 'Invalid data',
                'lap_time': 'Invalid data'
            })
    collected_data.sort(key=lambda a: a['lap_time'])
    return collected_data


def print_report():
    """
    Current function takes all sorted data, and returns structured data to a console
    """
    pass


print(data_merge())
