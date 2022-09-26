from datetime import datetime, timedelta
import argparse
from os import path


def get_parser():
    """The parser for a command line"""
    my_parser = argparse.ArgumentParser(description='Shows the results table of F1 players, or stats of each player')
    group = my_parser.add_mutually_exclusive_group()

    my_parser.add_argument('--files', type=str, required=True,
                           help='the path to folder with the logs and abbreviations')
    my_parser.add_argument('--driver', type=str, help='name of the specific driver to output info about him')
    group.add_argument('--asc', action='store_const', dest='ordering', const='asc',
                       help='shows the list of players in ascending order by time')
    group.add_argument('--desc', action='store_const', dest='ordering', const='desc',
                       help='shows the list of players in descending order by time')

    return my_parser


def cli():
    """
    Current function parses the arguments from command line, assign 3 paths (start_path, finish_path,
    abbreviations_path), and executing either info about the racer, either the list of racers with the results
    """
    parser = get_parser()
    parsers_data = parser.parse_args()

    start_path = path.join(parsers_data.files, 'start.log')
    finish_path = path.join(parsers_data.files, 'end.log')
    abbreviations_path = path.join(parsers_data.files, 'abbreviations.txt')

    try:
        structured_info = processing_data(start_path, finish_path, abbreviations_path)
        if parsers_data.driver:
            drivers_info = structured_info.get(parsers_data.driver)
            if drivers_info is not None:
                print('Racer -', drivers_info.name,
                      '\nTeam -', drivers_info.team,
                      '\nTime -', drivers_info.lap_time_str)
            else:
                print('There is the wrong racers name. Please, check the spelling')
        else:
            prepared_info_for_report = build_report(structured_info, parsers_data.ordering)
            print_report(prepared_info_for_report, parsers_data.ordering)
    except FileNotFoundError as e:
        print(e, 'Please, check the folder path and if the files start.log, end.log, abbreviations.txt files are '
                 'exist')


def processing_data(start_path, finish_path, abbreviations_path):
    """Function calls the necessary functions to get info for CLI function about all the racers"""
    collected_abbreviations = collecting_abbreviations(abbreviations_path)
    collected_data = collecting_racers_data(start_path, finish_path, collected_abbreviations)
    return players_info(collected_data)


def collecting_abbreviations(file_path: str):
    """
    Function reads data from abbreviations.txt file, and returns a dict of racers in format
    {abbreviation: {name: name, team: team}, ..., ...}.
    """
    with open(file_path, 'r') as unsorted_file:
        abbreviations = unsorted_file.read().splitlines()
    racers_data = {}
    abbreviations = [item for item in abbreviations if item]
    for each_racer in abbreviations:
        abbreviation, name, team = each_racer.strip().split('_')
        racers_data[abbreviation] = {'abbreviation': abbreviation, 'name': name, 'team': team}
    return racers_data


def collecting_racers_data(start_file_path, finish_file_path, collected_data):
    """
    Takes start and end paths to files, and previously created container from abbreviation file, and update the last
    file with info from start and end file (start and finish time). If there is no info about time, func assigns None.
    """
    updated_data = time_uploader(start_file_path, collected_data, 'start_time')
    updated_data = time_uploader(finish_file_path, updated_data, 'finish_time')
    return updated_data


def time_uploader(file_path, collected_data, key_title):
    """
    Function updates the container with info about the racer from start or end file.
    :param file_path: path to a file (start or end file).
    :param collected_data: previously created container with data from previously parsed files.
    :param key_title: the name of the key we want to update the dictionary with.
    :return: updated container.
    """
    players_list = file_reader(file_path)
    for players_result in players_list:
        racers_data = players_result.strip()
        abbreviation = racers_data[:3]
        time = datetime.strptime(racers_data[3:], '%Y-%m-%d_%H:%M:%S.%f')
        collected_data[abbreviation][key_title] = time
    return collected_data


def file_reader(file_path):
    """
    Reads the files start and end for further processing, and returns the list of lines from a file
    """
    with open(file_path, 'r') as file:
        players_list = file.read().splitlines()
        return [item for item in players_list if item]


class Racer:
    """
    Class Racer represents a racer with the properties such as name, team, start_time, finish_time, lap_time, lap_time_str
    """

    def __init__(self, name, abbreviation, team, start_time, finish_time):
        self.name = name
        self.abbreviation = abbreviation
        self.team = team
        self.start_time = start_time
        self.finish_time = finish_time

    def __lt__(self, other):
        if self.lap_time and other.lap_time:
            return self.lap_time < other.lap_time
        else:
            return other.lap_time is not None

    @property
    def lap_time(self):
        if self.finish_time or self.start_time:
            if self.finish_time - self.start_time > timedelta(0):
                return self.finish_time - self.start_time

    @property
    def lap_time_str(self):
        return str(self.lap_time)[3:-3] if self.lap_time else "Incorrect data"


def players_info(collected_data):
    """
    Func takes info about racers and returns a dict where key is the name of the racer, and value is the Racer object.
    """
    structured_info = {}
    for racer in collected_data:
        racers_data = collected_data[racer]
        structured_info[racers_data['name']] = Racer(racers_data['name'],
                                                     racers_data['abbreviation'],
                                                     racers_data['team'],
                                                     racers_data.get('start_time'),
                                                     racers_data.get('finish_time'))
    return structured_info


def build_report(structured_info, ordering):
    """
    Func takes dict in format {name: Racer object, ...}, creates a new list, and sorts all the racers in given by
    ordering.
    """
    sorted_info = sorted(structured_info.values(), reverse=(ordering == 'desc'))
    sorted_info.sort(key=lambda x: x.lap_time is None)
    return sorted_info


def print_report(prepared_info_for_report: list, ordering):
    """
    Func prints the information about all the racers from given sorted list with the racer objects.
    """
    number_of_valid_racers = len([None for racer in prepared_info_for_report if racer.lap_time])
    if ordering == 'desc':
        racer_number_sequence = iter(range(number_of_valid_racers, 0, -1))
    else:
        racer_number_sequence = iter(range(1, number_of_valid_racers + 1))

    for racer in prepared_info_for_report:
        if racer.lap_time:
            racers_number = next(racer_number_sequence)
            print(f"{racers_number} {racer.name : <20} | {racer.team : <25} | {racer.lap_time_str}")
            if ordering != 'desc' and racers_number == 15:
                print(70*'-')
            elif ordering == 'desc' and (racers_number == 16 or racers_number == 1):
                print(70 * '-')
        else:
            print(f"- {racer.name : <20} | {racer.team : <25} | {racer.lap_time_str}")


if __name__ == '__main__':
    cli()
