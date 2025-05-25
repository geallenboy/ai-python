# Dates

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/code/builtin/data-transformation-functions/dates.md "Edit this page")

# Dates#

A reference document listing built-in convenience functions to support data transformation in [expressions](../../../../glossary/#expression-n8n) for dates.

JavaScript in expressions

You can use any JavaScript in expressions. Refer to [Expressions](../../../expressions/) for more information.

###  beginningOf(unit?: DurationUnit): Date #

Transforms a Date to the start of the given time period. Returns either a JavaScript Date or Luxon Date, depending on input. 

#### Function parameters#

unitOptionalString enum

A valid string specifying the time unit.

Default: `week`

One of: `second`, `minute`, `hour`, `day`, `week`, `month`, `year`

* * *

###  endOfMonth(): Date #

Transforms a Date to the end of the month. 

* * *

###  extract(datePart?: DurationUnit): Number #

Extracts the part defined in datePart from a Date. Returns either a JavaScript Date or Luxon Date, depending on input. 

#### Function parameters#

datePartOptionalString enum

A valid string specifying the time unit.

Default: `week`

One of: `second`, `minute`, `hour`, `day`, `week`, `month`, `year`

* * *

###  format(fmt: TimeFormat): String #

Formats a Date in the given structure 

#### Function parameters#

fmtRequiredString enum

A valid string specifying the time format. Refer to [Luxon | Table of tokens](https://moment.github.io/luxon/#/formatting?id=table-of-tokens) for formats.

* * *

###  isBetween(date1: Date | DateTime, date2: Date | DateTime): Boolean #

Checks if a Date is between two given dates. 

#### Function parameters#

date1RequiredDate or DateTime

The first date in the range.

date2RequiredDate or DateTime

The last date in the range.

* * *

###  isDst(): Boolean #

Checks if a Date is within Daylight Savings Time. 

* * *

###  isInLast(n?: Number, unit?: DurationUnit): Boolean #

Checks if a Date is within a given time period. 

#### Function parameters#

nOptionalNumber

The number of units. For example, to check if the date is in the last nine weeks, enter 9.

Default: `0`

unitOptionalString enum

A valid string specifying the time unit.

Default: `minutes`

One of: `second`, `minute`, `hour`, `day`, `week`, `month`, `year`

* * *

###  isWeekend(): Boolean #

Checks if the Date falls on a Saturday or Sunday. 

* * *

###  minus(n: Number, unit?: DurationUnit): Date #

Subtracts a given time period from a Date. Returns either a JavaScript Date or Luxon Date, depending on input. 

#### Function parameters#

nRequiredNumber

The number of units. For example, to subtract nine seconds, enter 9 here.

unitOptionalString enum

A valid string specifying the time unit.

Default: `milliseconds`

One of: `second`, `minute`, `hour`, `day`, `week`, `month`, `year`

* * *

###  plus(n: Number, unit?: DurationUnit): Date #

Adds a given time period to a Date. Returns either a JavaScript Date or Luxon Date, depending on input. 

#### Function parameters#

nRequiredNumber

The number of units. For example, to add nine seconds, enter 9 here.

unitOptionalString enum

A valid string specifying the time unit.

Default: `milliseconds`

One of: `second`, `minute`, `hour`, `day`, `week`, `month`, `year`

* * *

###  toDateTime(): Date #

Converts a JavaScript date to a [Luxon date object](https://docs.n8n.io/code/cookbook/luxon/). 

* * *

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 
