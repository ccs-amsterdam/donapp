# donapp
Web site allowing downloading of whatsapp data


# Installation (Linux)

Clone and install dependencies as normal:

```{sh}
git clone https://github.com/vanatteveldt/donapp
cd donapp
python3 -m venv env
env/bin/pip install -U pip wheel
env/bin/pip install -r requirements.txt
```

Install latest firefox and geckodriver:

```{sh}
mkdir bin
cd bin
wget -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US"
tar xf firefox.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
tar xf geckodriver-v0.29.0-linux64.tar.gz      
```

Make sure you have libgtk-3-0 installed, otherwise issues with Firefox might occurr
```
sudo apt-get install -y libgtk-3-0
```

# Run debug version

```{sh}
QUART_APP=donapp.server PATH=bin/:bin/firefox/:$PATH env/bin/quart run
```

To run in headless mode:
```{sh}
QUART_APP=donapp.server PATH=bin:bin/firefox/:$PATH /usr/bin/xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" env/bin/quart run
```
