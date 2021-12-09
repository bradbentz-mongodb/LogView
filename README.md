# LogView

View a directory of logs with one command. Sort logs across multiple files by timestamp and filter by common patterns.


## Components

A python cli containing log view utility functions. Pass in a directory of logs to sort logs in that directory by timestamp and display to stdout.


Sort logs in a given directory by timestamp.
```
./python_cli.py .
```

Invalid directory
```
./python_cli.py foo
Invalid directory foo
```

Specify start and end times
```
./python_cli.py . --start-time 2021-12-01T00:00:00+00:00 --end-time 2021-12-05T00:00:00+00:00
Viewing logs in /Users/brad/LogView starting from 2021-12-01 00:00:00+00:00 ending at 2021-12-05 00:00:00+00:00
```

## Example configuration file

```
./python_cli.py -c parser.conf
```

parser.conf:
```
[directory]
~

[start_time]
2021-12-01T00:00:00+00:00

[end_time]
2021-12-05T00:00:00+00:00

[match_pattern]
Hel[l]o \= 1
goodbye
pattern with space
-i abc.?def.*

[exclude_pattern]
DEBUG
```


## Linting

To lint this project, run ./lint.sh from the project directory.

```
./lint.sh
```
