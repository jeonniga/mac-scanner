try: #python3
    from urllib.request import urlopen
except: #python2
    from urllib2 import urlopen


def load_dictionary(file):
    # 지정된 oui 바이너리 파일을 읽어서 딕셔너리로 리턴한다
    oui = {}
    with open(file, 'r') as f:
        for line in f:
            if '(hex)' in line:
                data = line.split('(hex)')
                key = data[0].replace('-', ':').lower().strip()
                company = data[1].strip()
                oui[key] = company
    return oui


def download_oui(to_file):
    # 기준이 되는 oui DB파일을 내려받는다.
    uri = 'http://standards-oui.ieee.org/oui/oui.txt'
    print("Trying to download current version of oui.txt from [%s] to file [%s]" % (uri, to_file))
    oui_data = urlopen(uri, timeout=10).read()
    with open(to_file, 'wb') as oui_file:
        oui_file.write(oui_data)
