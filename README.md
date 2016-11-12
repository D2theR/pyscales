#PyScales#
>>>>>>> b9ffb01acb79e57906e20405a2757fc7cf2fbbe3
==========================================================================================
PyScales is a project created by Daniel Rerko as a rapid inventory/data gathering utility.
==========================================================================================
Supported OS: Linux (Ubuntu 16.02 latest tested)
Software: Python (v3), Django Web-framework as a management frontend. 
Database: PostgreSQL 9.4 Deployed through LAPP Stack 5.5.31-0
See requirements.txt for all Python packages. 
==========================================================================================
It uses the Python programming language, packages like PySerial to interface with data acquisition devices specifically, scales but could potentially be configured to run any and all RS232 communicable devices. The current rapid inventory management "API" runs within the command-line and uses ZBar barcode reader package with an attached webcam to scan QR codes for easier data acquisition.

PyScales is a project created by Daniel Rerko as a rapid inventory/data gathering
utility designed to run within the Python (v3) programming language on Linux Debian based OSes and uses the Django Web-framework as a management frontend. It is NOT currently released to the public in it's current form.

It uses plugins like PySerial to interface with data acquisition devices specifically, scales but could potentially be configured to run any and all RS232 communicable devices.

The current rapid inventory management API runs within the command-line and uses ZBar barcode reader package with an attached webcam to scan QR codes for easier data acquisition.

##INSTALLATION##

Once the Git repo has been acquired...

cd to install/extracted directory

```
chmod -x "build_pyscales_env.sh"

./build_pyscales_env.sh

source bin/activate

cd /pdi_ims

```

From the pdi_ims directory run the following Django custom command and viola!:
```
python manage.py pyscales
```

### CONFIGURATION & NOTES ###

PyScales will not run stand alone. It needs a fully configured LAPP stack server running as a seperate instance. 
The server and the Pi-Client only share Django Models.  
