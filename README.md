# Expense Tracker CLI

A command-line expense tracking application built with Python.

## Tech Stack
Python · CSV · Datetime Module

## Features
- Add, edit, delete expenses with persistent CSV storage
- Date-range filtering and category-based financial reports
- Input validators reject malformed dates, empty fields, and negative values
- Quick stats: total, average, median, largest spend

## Commands
| Command  | Description                          |
|----------|--------------------------------------|
| add      | Add a new expense                    |
| list     | View all expenses                    |
| filter   | Filter by date range / category      |
| report   | Full financial report                |
| edit     | Edit an existing expense             |
| delete   | Delete an expense                    |
| stats    | Quick stats summary                  |

## Run
```bash
python expense_tracker.py
```

## Requirements
No external dependencies — pure Python stdlib
