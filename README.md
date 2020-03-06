# Master Of Coin (Telegram Bot)

A simple telegram bot that records and show spendings built using python (pyTelegramBotAPI). 

# Why this?

To learn python! In the process create a nice tool that I wanted: quick and easy way to record expenses! Sure, there are better free and nicer looking mobile apps out there to track expenses with but sometimes it takes just too many taps/clicks to do something as simple as recording how much I ate for lunch or 'Food'. Note: This little bot is not designed or optimized to serve bazzillion or gazzilion users! It was a fun project shared among close friends and family - the amazing thing is you can take this code and customize it anyway you want it that fits your needs. Example the categories used for recording a new spending doesn't suit you, change it! 

# How to setup?

1. Get api key from botfather
2. Install the following dependencies: ... ... (todo)
3. Run `python3 coin_bot.py`
   (ideally set it up in cloud or any free FaaS)

# How to use?

## Help menu and list of commands

`help` show help menu

## Record a new expenses

* `/new` and select category
* key in $ amount 

## Show spendings

* `/show` and select mode (day or month)

## View all spending history

* `/history` to view all spending history so far

# For Developers

## Data structure and persisting

`data.json` file is loaded on every read/write action into a global dictionary, with the following json key-value structure

```json
    "CHAT ID 1": [
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        ...
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>"
    ],
    "CHAT ID 2": [
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        ...
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>"
    ],
    "CHAT ID 2": [
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>",
        ...
        "<DD-MMM-YYYY HH:MM>,<CategoryString>,<Amount>"
    ]
}
```

Keys: String id that uniquely identifies user client.
Values: String arrays comma seperated with date values, category strings, amount

## Query method

The functionality to group category, sum of spending for that category, by day or month is done by

1. Defining query time or date or month

2. Enumerating dictionary key,values for query
   
   ```python
   dateFormat = '%d-%b-%Y'
   timeFormat = '%H:%M'
   monthFormat = '%b-%Y'
   
   #get all string array of ['Date','Category','amount'] for client id
   history = global_dictionary['CHAT_ID']
   
   #prepare query string for specific date/time/month
   query = datetime.now().today().strftime(dateFormat)
   
   #enumerate key values to get a match of string array ['Date','Category','amount']
   result = [value for index, value in enumerate(history) if str(query) in value]
   
   CALCULATE(result)
   ```

3. Suming up all categories
   
   ```python
   def CALCULATE(result)
   catSum = {}
   
        for row in result:

           s = row.split(',') # ['Date','Category','amount']

           cat = s[1]  # 'Category'
           
        # sum grouped category amounts
           if cat in catSum:
               #round up to 2 decimal
               catSum[cat] = round(catSum[cat] + float(s[2]),2)    
           else:
               #first entry
               catSum[cat] = float(s[2])
   ```

This functionality is added because I wanted to have a quick overview the total amount of spending for each category (having a budget in mind) I could tell if I overspent or not. 

Example: If I had spent $4 on breakfast, lunch and dinner respectively (adds up to $12) I could create a query for todays date and show a sum of all category. The result could be formatted in a simple text response from the bot as such:


```bash
Total spending for today:
CATEGORY, AMOUNT
----------------
Food: $12.0
```





## todo

* delete (made a mistake and want to remove a spending record)

## Good features and may be implemented

* Set a expenses goal and set notify/alert you if you are overspending
* Email spendings (eg. txt,csv or xls) to yourself
