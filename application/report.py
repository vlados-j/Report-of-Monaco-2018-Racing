from datetime import datetime, timedelta
import argparse
from os import path


def get_parser():
    """It's the parser for a command line"""
    my_parser = argparse.ArgumentParser(description='Shows the results table of F1 players, or stats of each player')

    my_parser.add_argument('--files', type=str, help='the path to folder with the logs and abbreviations')
    my_parser.add_argument('--driver', type=str, help='name of the specific driver to output info about him')
    my_parser.add_argument('--asc', action='store_false', help='shows the list of players in ascending order by time')
    my_parser.add_argument('--desc', action='store_true', help='shows the list of players in descending order by time')

    return my_parser


def cli():
    """
    Current function parses data from the command line, and execute the final result by calling
    necessary functions
    """
    parser = get_parser()
    parsers_data = parser.parse_args()
    if parsers_data.files is not None and path.isdir(parsers_data.files):
        start_path = parsers_data.files + '/start.log'
        finish_path = parsers_data.files + '/end.log'
        abbreviations_path = parsers_data.files + '/abbreviations.txt'
        try:
            collected_abbreviations = collecting_abbreviations(abbreviations_path)
            collected_data = collecting_racers_data(start_path, finish_path, collected_abbreviations)
            structured_info = players_info(collected_data)
            if parsers_data.driver is not None and structured_info[parsers_data.driver]['lap_time'] > timedelta(0):
                print('Racer -', structured_info[parsers_data.driver]['name'],
                      '\nTeam -', structured_info[parsers_data.driver]['team'],
                      '\nTime -', str(structured_info[parsers_data.driver]['lap_time'])[3:-3])
            elif parsers_data.driver is not None:
                print('Racer -', structured_info[parsers_data.driver]['name'],
                      '\nTeam -', structured_info[parsers_data.driver]['team'],
                      '\nTime - Incorrect data. Check logs')
            else:
                prepared_info_for_report = build_report(structured_info, parsers_data.desc)
                print_report(prepared_info_for_report)
        except FileNotFoundError as e:
            print(e, 'Please, check if the files start.log, end.log, abbreviations.txt files are exist')
        except KeyError:
            print('Probably there is the wrong racers name. Please, check the spelling')
        except Exception:
            print('Something went wrong!')
    else:
        print('\nThere is no such a directory\n')
        parser.print_help()


def collecting_abbreviations(file_path: str):
    """
    Current function takes the path of the file, and returns the name of players, teams, and theirs abbreviations
    """
    with open(file_path, 'r') as unsorted_file:
        racers_data = {}
        abbreviations = unsorted_file.read().splitlines()
        abbreviations = list(filter(None, abbreviations))
        for each_racer in abbreviations:
            separated_data = each_racer.strip().split(sep='_')
            racers_data[separated_data[0]] = [separated_data[1], separated_data[2]]
        return racers_data


def collecting_racers_data(start_file_path, finish_file_path, collected_data):
    """
    Current function takes log files, add all the necessary data to previously created dictionary of lists with
    name, and team. Then append each list with the player's start time, and finish time
    """
    players_list = file_reader(start_file_path)
    for players_result in players_list:
        collected_data[players_result.strip()[:3]].append(players_result.strip()[3:])
    players_list = file_reader(finish_file_path)
    for players_result in players_list:
        collected_data[players_result.strip()[:3]].append(players_result.strip()[3:])
    return collected_data


def file_reader(file_path):
    """File reader which read the file, split it into the lines, removes empty strings, and returns the list of lines"""
    with open(file_path, 'r') as file:
        players_list = file.read().splitlines()
        return list(filter(None, players_list))


class Racer:
    """
    Class Racer presents each racer and takes attributes such as name, team, start time, and finish time.
    Class has 1 method (lap_calculator) which calculates the racer's lap time
    """
    def __init__(self, name, team, start_time, finish_time):
        self.name = name
        self.team = team
        self.start_time = start_time
        self.finish_time = finish_time

    def lap_calculator(self):
        start_time = datetime.strptime(self.start_time, '%Y-%m-%d_%H:%M:%S.%f')
        finish_time = datetime.strptime(self.finish_time, '%Y-%m-%d_%H:%M:%S.%f')
        return finish_time - start_time


def players_info(collected_data):
    """
    Current function collects the list of Racer objects from the previously given data for further usage.
    Then creates a dictionary where the key is the name, and 3 values - name, team, and lap time. From this function we
    take data to prepare info for report, or take it for output a statistic about a particular racer
    """
    racer_objects = [Racer(collected_data[racer][0],
                           collected_data[racer][1],
                           collected_data[racer][2],
                           collected_data[racer][3]) for racer in collected_data]
    structured_info = {}
    for racer in racer_objects:
        structured_info[racer.name] = {'name': racer.name,
                                       'team': racer.team,
                                       'lap_time': racer.lap_calculator()}
    return structured_info


def build_report(structured_info, asc_flag):
    """
    Current function takes the dictionary of previously created Racer objects, and the flag (True or False) which shows
    in which order to sort the players. Then returns 2 lists:
    1. The list of sorted data by time along with name and team for printing the report.
    2. The same list, but with the racers with the incorrectly taken time.
    """
    info_for_report = [[key, value['team'], value['lap_time']] for key, value in structured_info.items()
                       if value['lap_time'] >= timedelta(0)]
    info_for_report.sort(key=lambda x: x[2], reverse=asc_flag)
    info_with_incorrect_time = [[key, value['team'], 'Incorrect data. Check logs'] for key, value in structured_info.items()
                                if value['lap_time'] < timedelta(0)]
    return info_for_report, info_with_incorrect_time


def print_report(prepared_info_for_report):
    """The function takes all ready information from build_report function, and prints all info to console"""
    info_for_report, info_with_incorrect_time = prepared_info_for_report
    counter = 0
    for item in info_for_report:
        counter += 1
        print(f"{counter} {item[0] : <20} | {item[1] : <25} | {str(item[2])[3:-3]}")
        if counter == 15:
            print(80 * '-')
    for item in info_with_incorrect_time:
        counter += 1
        print(f"{counter} {item[0] : <20} | {item[1] : <25} | {item[2]}")
        if counter == 15:
            print(80 * '-')


if __name__ == '__main__':
    cli()
