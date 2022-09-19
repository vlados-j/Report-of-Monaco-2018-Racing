from datetime import datetime, timedelta
import argparse
from os import path


def get_parser():
    """The parser for a command line"""
    my_parser = argparse.ArgumentParser(description='Shows the results table of F1 players, or stats of each player')

    my_parser.add_argument('--files', type=str, required=True,
                           help='the path to folder with the logs and abbreviations')
    my_parser.add_argument('--driver', type=str, help='name of the specific driver to output info about him')
    my_parser.add_argument('--asc', action='store_false', help='shows the list of players in ascending order by time')
    my_parser.add_argument('--desc', action='store_true', help='shows the list of players in descending order by time')

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
            drivers_info = structured_info[parsers_data.driver]
            print('Racer -', drivers_info.name,
                  '\nTeam -', drivers_info.team,
                  '\nTime -', drivers_info.lap_time_str)
        else:
            prepared_info_for_report = build_report(structured_info, parsers_data.desc)
            print_report(prepared_info_for_report)
    except FileNotFoundError as e:
        print(e, 'Please, check the folder path and if the files start.log, end.log, abbreviations.txt files are '
                 'exist')
    except KeyError:
        print('Probably there is the wrong racers name. Please, check the spelling')
    # except Exception:
    #     print('Something went wrong!')


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
        racers_data = {}
        abbreviations = unsorted_file.read().splitlines()
        abbreviations = [item for item in abbreviations if item]
        for each_racer in abbreviations:
            abbreviation, name, team = each_racer.strip().split('_')
            racers_data[abbreviation] = {'name': name, 'team': team}
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

    def __init__(self, name, team, start_time, finish_time):
        self.name = name
        self.team = team
        self.start_time = start_time
        self.finish_time = finish_time

    def __lt__(self, other):
        if self.lap_time and other.lap_time:
            return self.lap_time < other.lap_time
        elif other.lap_time:
            return True
        else:
            return False

    @property
    def lap_time(self):
        if self.finish_time - self.start_time > timedelta(0):
            return self.finish_time - self.start_time
        else:
            return None

    @property
    def lap_time_str(self):
        return str(self.lap_time)[3:-3] if self.lap_time else None


def players_info(collected_data):
    """
    Func takes info about racers and returns a dict where key is the name of the racer, and value is the Racer object.
    """
    structured_info = {collected_data[racer]['name']:
                           Racer(collected_data[racer]['name'],
                                 collected_data[racer]['team'],
                                 collected_data[racer].get('start_time'),
                                 collected_data[racer].get('finish_time')) for racer in collected_data}
    return structured_info


def build_report(structured_info, asc_flag):
    """
    Func takes dict in format {name: Racer object, ...}, and split it into 2 lists (with correct time, and incorrect).
    Then sorts the list with correct data in requested order, and returns those 2 lists.
    """
    # info_for_report, info_with_incorrect_time = [], []
    # for racers_name, racer in structured_info.items():
    #     if racer.lap_time:
    #         info_for_report.append(racer)
    #     else:
    #         info_with_incorrect_time.append(racer)
    info_for_report = sorted(structured_info.items(), key=lambda x: x[1].lap_time, reverse=asc_flag)
    return info_for_report


def print_report(prepared_info_for_report):
    """
    Func prints the information about all the racers with given lists with info about the racers.
    """
    print(prepared_info_for_report)
    # counter = 0
    # for racer in info_for_report:
    #     counter += 1
    #     print(f"{counter} {racer.name : <20} | {racer.team : <25} | {racer.lap_time_str}")
    #     if counter == 15:
    #         print(70 * '-')
    # for racer in info_with_incorrect_time:
    #     counter += 1
    #     print(f"{counter} {racer.name : <20} | {racer.team : <25} | {racer.lap_time_str}")
    #     if counter == 15:
    #         print(70 * '-')


if __name__ == '__main__':
    cli()
