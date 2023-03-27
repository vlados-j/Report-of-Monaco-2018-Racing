<h1>The application was created to read data from log files, order racers from F1 by time and print report that shows the top 15 racers and the rest after underline, for example:</h1>


1. Daniel Ricciardo      | RED BULL RACING TAG HEUER     | 1:12.013

2. Sebastian Vettel      | FERRARI                       | 1:12.415

3. ...

------------------------------------------------------------------------

16. Brendon Hartley   | SCUDERIA TORO ROSSO HONDA         | 1:13.179

17. Marcus Ericsson  | SAUBER FERRARI                     | 1:13.265

The application has a command-line interface. The application have a few parameters. E.g.
> python report.py --files <folder_path> [--asc | --desc]  shows list of drivers and optional order (default order is asc)

> python report.py --files <folder_path> --driver “Sebastian Vettel”  shows statistic about driver 

<b>The application was converted to the python package, and uplaoded to PyPl, so it can be easily used using the next link </b> - https://test.pypi.org/project/application-vlados/0.0.1/.

<b>The format of the log files can be checked in the files folder inside the project.</b>
