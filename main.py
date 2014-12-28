#encoding=utf8

import requests
import os.path, time
import datetime
import json
import collections
from collections import OrderedDict
import webbrowser
from wox import Wox,WoxAPI

class canIUse(Wox):

    data_fn = os.path.dirname(os.path.abspath(__file__)) + "\data.json"

    # write file
    def write_file(self, filename, data):
        f = open(filename, 'w')
        f.write(data)
        f.close()

    # read file
    def read_file(self, filename):
        f = open(filename, 'r')
        data = f.read()
        f.close()
        return data

    # create supported browser versions item
    def browserVersion(self,stats):
        version = "0"
        for (key, value) in stats.items():
            if value == 'a x':
                if version.find("+*-px-") > 0 :
                    continue
                version = key + "+*-px-"
            elif value == 'a':
                if version.find("+*") > 0:
                    continue
                version = key+"+*";
            elif value == 'y x':
                if version.find("-px-") > 0:
                    continue
                version = key+"-px-";
            elif value == 'y':
                version = key + "+"
                break
            else:
                version = "n/a"

        return version

    # create string from stats
    def get_stats(self, stats):
        data = ", ["
        data += "FF:" + stats['FF']
        data += ", CH:" + stats['Ch']
        data += ", SF:" + stats['S']
        data += ", IE:" + stats['IE']
        data += "]"

        return data

    # get data from https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json
    def get_data(self):
        r = requests.get('https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json')
        data = r.json(object_pairs_hook=collections.OrderedDict)
        parsed_data = data['data']
        dct = {}
        for (key, val) in parsed_data.items():
            title = val['title']
            url = "http://caniuse.com/#feat=" + key
            description = val['description']

            stats = {}
            for (browser, stat) in val['stats'].items():
                stats[browser] = self.browserVersion(stat)

            dct[key] = {
                "title":title,
                "url":url,
                "description":description,
                "stats":{
                    "IE":stats['ie'],
                    "FF":stats['firefox'],
                    "Ch":stats['chrome'],
                    "S":stats['safari']
                }
            }

        if len(dct):
            self.write_file(self.data_fn, json.dumps(dct))

    def query(self,key):
        # if file not exists or file is old - create data.json
        if not (os.path.isfile(self.data_fn)) or (os.path.getmtime(self.data_fn) <= int( time.time()-86400*7)) :
            self.get_data()

        # read data from file
        data = json.loads(self.read_file(self.data_fn), object_pairs_hook=collections.OrderedDict)
        query = key
        results  = []
        bykey  = collections.OrderedDict()
        bytitle  = collections.OrderedDict()
        bydesc  = collections.OrderedDict()

        if query == "":
            results.append({
                "Title": "Search caniuse.com",
                "SubTitle": "Support tables for HTML5, CSS3, etc",
                "IcoPath":"Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "",
                    "parameters":"",
                    "dontHideAfterAction":True
                    }
                })
            return results

        # create result from data
        for (key, result) in data.items():
            value = key.lower().strip()
            title = result['title'].lower().strip()
            description = result['description'].lower().strip()

            if value.find(query) == 0:
                results.append({
                    "Title": result['title'] + self.get_stats(result['stats']),
                    "SubTitle": result['description'],
                    "IcoPath":"Images\\caniuse.png",
                    "JsonRPCAction":{
                        "method": "openUrl",
                        "parameters":[result['url']],
                        "dontHideAfterAction":False
                        }
                    })
            elif value.find(query) > 0:
                bykey[key] = result
            elif title.find(query) != -1:
                bytitle[key] = result
            elif description.find(query) != -1:
                bydesc[key] = result

        for (key, keyres) in bykey.items():
            results.append({
                "Title": keyres['title'] + self.get_stats(keyres['stats']),
                "SubTitle": keyres['description'],
                "IcoPath":"Images\\caniuse.png","JsonRPCAction":{
                    "method": "openUrl",
                    "parameters":[keyres['url']],
                    "dontHideAfterAction":False
                }
            })

        for (key, titleres) in bytitle.items():
            results.append({
                "Title": titleres['title'] + self.get_stats(titleres['stats']),
                "SubTitle": titleres['description'],
                "IcoPath":"Images\\caniuse.png","JsonRPCAction":{
                    "method": "openUrl",
                    "parameters":[titleres['url']],
                    "dontHideAfterAction":False
                }
            })

        for (key, descres) in bydesc.items():
            results.append({
                "Title": descres['title'] + self.get_stats(descres['stats']),
                "SubTitle": descres['description'],
                "IcoPath":"Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "openUrl",
                    "parameters":[descres['url']],
                    "dontHideAfterAction":False
                }
            })

        return results

    def openUrl(self,url):
        webbrowser.open(url)
        # WoxAPI.shell_run(url)
        # os.popen('"'+self.exe_path+'"' + ' --site=0' + server)

if __name__ == "__main__":
    canIUse()