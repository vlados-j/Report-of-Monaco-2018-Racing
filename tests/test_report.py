from argparse import Namespace
from application import *
from unittest.mock import patch, Mock, mock_open
import sys
import pytest


def test_get_parser():
    test_args = ['fake_report.py', '--files', 'fake/path/for/tests', '--asc']
    with patch.object(sys, 'argv', test_args):
        setup = get_parser()
        assert str(setup) == "ArgumentParser(prog='fake_report.py', usage=None, description='Shows the results " \
                             "table of F1 players, or stats of each player', formatter_class=<class 'argparse." \
                             "HelpFormatter'>, conflict_handler='error', add_help=True)"


@pytest.mark.parametrize("parsed_data, expected_result",
                         [(Namespace(files='fake/path', driver=None, ordering='asc'),
                           '1 Sebastian Vettel     | FERRARI                   | 1:04.999\n' \
                           '- Daniel Ricciardo     | RED BULL RACING TAG HEUER | Incorrect data\n'),
                          (Namespace(files='fake/path', driver='Sebastian Vettel'),
                           'Racer - Sebastian Vettel \nTeam - FERRARI \nTime - 1:04.999\n'),
                          (Namespace(files='fake/path', driver='Sebastian Vettellll'),
                           'There is the wrong racers name. Please, check the spelling\n')
                          ])
@patch('application.report.processing_data')
@patch('application.report.get_parser')
def test_cli(mock_get_parser, mock_processing_data, parsed_data, expected_result, capsys):
    mock_get_parser.return_value = Mock(parse_args=Mock(return_value=parsed_data))
    mock_processing_data.return_value = {'Sebastian Vettel':
                                             Racer('Sebastian Vettel', 'SVF', 'FERRARI',
                                                   datetime(2018, 5, 24, 12, 2, 58, 917),
                                                   datetime(2018, 5, 24, 12, 4, 3, 332)),
                                         'Daniel Ricciardo':
                                             Racer('Daniel Ricciardo', 'DRR', 'RED BULL RACING TAG HEUER', None, None)}
    cli()
    out, err = capsys.readouterr()
    assert out == expected_result


@patch('application.report.get_parser')
def test_cli_with_error(mock_get_parser, capsys):
    parsed_data = Namespace(files='fake/path', driver=None, ordering='asc')
    mock_get_parser.return_value = Mock(parse_args=Mock(return_value=parsed_data))
    cli()
    out, err = capsys.readouterr()
    expected_output = "[Errno 2] No such file or directory: 'fake/path/abbreviations.txt' Please, " \
                      "check the folder path and if the files start.log, end.log, abbreviations.txt " \
                      "files are exist\n"
    assert out == expected_output


def test_collecting_abbreviations():
    mock_file_content = 'DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER\nSVF_Sebastian Vettel_FERRARI\n'
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as _file:
        expected_result = {
            'DRR': {'abbreviation': 'DRR', 'name': 'Daniel Ricciardo', 'team': 'RED BULL RACING TAG HEUER'},
            'SVF': {'abbreviation': 'SVF', 'name': 'Sebastian Vettel', 'team': 'FERRARI'}}
        assert collecting_abbreviations('fake/path') == expected_result


@patch('application.report.file_reader')
def test_time_uploader(mocked_file_reader):
    mocked_file_reader.return_value = ['SVF2018-05-24_12:02:58.917', 'NHR2018-05-24_12:02:49.914 ']
    collected_data = {'SVF': {'abbreviation': 'SVF', 'name': 'Sebastian Vettel', 'team': 'FERRARI'},
                      'NHR': {'abbreviation': 'NHR', 'name': 'Nico Hulkenberg', 'team': 'RENAULT'}}
    test_function = time_uploader('fake/path', collected_data, 'start_time')
    expected_result = {'NHR': {'abbreviation': 'NHR',
                               'name': 'Nico Hulkenberg',
                               'start_time': datetime(2018, 5, 24, 12, 2, 49, 914000),
                               'team': 'RENAULT'},
                       'SVF': {'abbreviation': 'SVF',
                               'name': 'Sebastian Vettel',
                               'start_time': datetime(2018, 5, 24, 12, 2, 58, 917000),
                               'team': 'FERRARI'}}
    assert test_function == expected_result


def test_file_reader():
    mock_file_content = 'test test test\ntest test test\n'
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as _file:
        assert file_reader('fake/path') == ['test test test', 'test test test']


def test_Racer():
    racer1 = Racer('Alex', 'ALX', 'Red Bull', datetime(2018, 5, 24, 12, 2, 58, 917),
                   datetime(2018, 5, 24, 12, 4, 3, 332))
    racer2 = Racer('Alex', 'ALX', 'Red Bull', datetime(2018, 5, 24, 12, 13, 4, 512), None)
    assert racer1.lap_time == timedelta(seconds=64, microseconds=999415)
    assert racer1.lap_time_str == '1:04.999'
    assert racer2.lap_time is None
    assert racer2.lap_time_str == 'Incorrect data'


def test_players_info():
    info_for_test = {'Alex': {'name': 'Alex', 'abbreviation': 'ALX', 'team': 'Benz'},
                     'John': {'name': 'John', 'abbreviation': 'JHN', 'team': 'Audi',
                              'start_time': datetime(2018, 5, 24, 12, 2, 58, 917),
                              'finish_time': datetime(2018, 5, 24, 12, 4, 3, 332)}}
    function_result = players_info(info_for_test)
    assert isinstance(function_result['Alex'], Racer)
    assert isinstance(function_result['John'], Racer)


def test_build_report():
    racer1 = Racer('Sebastian Vettel', 'SVF', 'FERRARI', datetime(2018, 5, 24, 12, 2, 58, 917000),
                   datetime(2018, 5, 24, 12, 4, 3, 332))
    racer2 = Racer('Esteban Ocon', 'EOF', 'FORCE INDIA MERCEDES', datetime(2018, 5, 24, 12, 17, 58, 810),
                   datetime(2018, 5, 24, 12, 12, 11, 838))
    racer3 = Racer('Fernando Alonso', 'FAM', 'MCLAREN RENAULT', datetime(2018, 5, 24, 12, 13, 4, 512),
                   datetime(2018, 5, 24, 12, 14, 17, 169))
    racer4 = Racer('Daniel Ricciardo', 'DRR', 'RED BULL RACING TAG HEUER', datetime(2018, 5, 24, 12, 14, 12, 54),
                   datetime(2018, 5, 24, 12, 11, 24, 67))
    test_dict = {'Sebastian Vettel': racer1, 'Esteban Ocon': racer2, 'Fernando Alonso': racer3, 'Daniel Ricciardo': racer4}
    assert build_report(test_dict, 'asc') == [racer1, racer3, racer2, racer4]
    assert build_report(test_dict, 'desc') == [racer3, racer1, racer2, racer4]


def test_print_report(capsys):
    racer1 = Racer('Sebastian Vettel', 'SVF', 'FERRARI', datetime(2018, 5, 24, 12, 2, 58, 917000),
                   datetime(2018, 5, 24, 12, 4, 3, 332))
    racer2 = Racer('Esteban Ocon', 'EOF', 'FORCE INDIA MERCEDES', datetime(2018, 5, 24, 12, 17, 58, 810),
                   datetime(2018, 5, 24, 12, 12, 11, 838))
    racer3 = Racer('Fernando Alonso', 'FAM', 'MCLAREN RENAULT', datetime(2018, 5, 24, 12, 13, 4, 512),
                   datetime(2018, 5, 24, 12, 14, 17, 169))
    racer4 = Racer('Daniel Ricciardo', 'DRR', 'RED BULL RACING TAG HEUER', datetime(2018, 5, 24, 12, 14, 12, 54),
                   datetime(2018, 5, 24, 12, 11, 24, 67))
    list_of_objects = [racer1, racer3, racer2, racer4]
    print_report(list_of_objects, 'asc')
    out, err = capsys.readouterr()
    assert out == '1 Sebastian Vettel     | FERRARI                   | 1:04.083\n' \
                  '2 Fernando Alonso      | MCLAREN RENAULT           | 1:12.999\n' \
                  '- Esteban Ocon         | FORCE INDIA MERCEDES      | Incorrect data\n' \
                  '- Daniel Ricciardo     | RED BULL RACING TAG HEUER | Incorrect data\n'
