﻿# InteractiveBrokers
## Overview

Easy-to-use CSV puller for Interactive Brokers Flex Queries. Queries must be already set up.

Simply enter the auth token, the query ID's and they will return as CSV's.

## Installation

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```
In the same folder as the script, set up two ".txt" files, as follows:

### token.txt

```bash
000000000000000000000000
```

Found under "Configure Flex Web Service", as "Current Token".

### query.txt

```bash
0000000,Friendly Name
```

The output file type for your Queires must be CSV.

## Usage

To use the scripts in this repository, you will need to have an Interactive Brokers account and obtain API access. 


## Contact

For any questions or issues, please open an issue on GitHub or contact the maintainers.
